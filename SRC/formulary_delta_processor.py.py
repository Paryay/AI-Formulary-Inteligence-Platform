#!/usr/bin/env python3
"""
Formulary File Delta Processor
Handles multiple file formats and generates delta files for efficient processing
"""

import pandas as pd
import os
import hashlib
from pathlib import Path
from datetime import datetime
import json
import argparse


class FormularyDeltaProcessor:
    """Process formulary files and generate delta changes"""
    
    SUPPORTED_FORMATS = {
        '.csv': {'sep': ','},
        '.txt': {'sep': '|'},  # Common pipe-delimited
        '.tsv': {'sep': '\t'},
        '.xlsx': {},
        '.xls': {}
    }
    
    def __init__(self, archive_dir='./archive', output_dir='./output'):
        self.archive_dir = Path(archive_dir)
        self.output_dir = Path(output_dir)
        self.archive_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def detect_format(self, filepath):
        """Auto-detect file format and delimiter"""
        filepath = Path(filepath)
        ext = filepath.suffix.lower()
        
        if ext in ['.xlsx', '.xls']:
            return 'excel', {}
        
        # For text files, try to detect delimiter
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            
        if '|' in first_line:
            return 'csv', {'sep': '|'}
        elif '\t' in first_line:
            return 'csv', {'sep': '\t'}
        elif ',' in first_line:
            return 'csv', {'sep': ','}
        else:
            # Try fixed-width or other format
            return 'csv', {'sep': None}  # Let pandas auto-detect
    
    def read_file(self, filepath, **kwargs):
        """Read file in any supported format"""
        filepath = Path(filepath)
        file_type, params = self.detect_format(filepath)
        
        print(f"Reading {filepath.name} as {file_type} with params {params}")
        
        try:
            if file_type == 'excel':
                df = pd.read_excel(filepath, **kwargs)
            else:
                # Merge detected params with user-provided kwargs
                read_params = {**params, **kwargs}
                df = pd.read_csv(filepath, **read_params, low_memory=False)
            
            print(f"✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            raise
    
    def generate_row_hash(self, row):
        """Generate unique hash for a row to detect changes"""
        row_str = '|'.join(str(v) for v in row.values)
        return hashlib.md5(row_str.encode()).hexdigest()
    
    def find_previous_file(self, carrier_name):
        """Find the most recent archived file for this carrier"""
        pattern = f"{carrier_name}_*.pkl"
        files = list(self.archive_dir.glob(pattern))
        
        if not files:
            return None
        
        # Get most recent
        latest = max(files, key=lambda p: p.stat().st_mtime)
        print(f"Found previous file: {latest.name}")
        return latest
    
    def compare_and_generate_delta(self, new_file, carrier_name, key_columns=None):
        """
        Compare new file with previous and generate delta files
        
        Args:
            new_file: Path to new full file
            carrier_name: Name of carrier (for archiving)
            key_columns: List of columns that uniquely identify a row (e.g., ['NDC', 'PLAN_ID'])
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Read new file
        print(f"\n{'='*60}")
        print(f"Processing: {carrier_name}")
        print(f"{'='*60}")
        new_df = self.read_file(new_file)
        
        # Find previous file
        prev_file = self.find_previous_file(carrier_name)
        
        if prev_file is None:
            print("\n⚠ No previous file found - treating entire file as new additions")
            result = {
                'added': new_df,
                'deleted': pd.DataFrame(),
                'modified': pd.DataFrame(),
                'unchanged': pd.DataFrame()
            }
        else:
            print("\nComparing with previous file...")
            prev_df = pd.read_pickle(prev_file)
            
            result = self.compare_dataframes(prev_df, new_df, key_columns)
        
        # Generate output files
        output_files = self.save_delta_files(result, carrier_name, timestamp)
        
        # Archive new file for next month's comparison
        archive_path = self.archive_dir / f"{carrier_name}_{timestamp}.pkl"
        new_df.to_pickle(archive_path)
        print(f"\n✓ Archived to: {archive_path}")
        
        # Generate summary report
        self.generate_summary_report(result, carrier_name, timestamp, output_files)
        
        return output_files
    
    def compare_dataframes(self, old_df, new_df, key_columns=None):
        """Compare two dataframes and identify changes"""
        
        # If key columns not specified, use all columns as key
        if key_columns is None:
            print("⚠ No key columns specified - using row hashing for comparison")
            old_df['_row_hash'] = old_df.apply(self.generate_row_hash, axis=1)
            new_df['_row_hash'] = new_df.apply(self.generate_row_hash, axis=1)
            key_columns = ['_row_hash']
        
        # Ensure key columns exist
        for col in key_columns:
            if col not in old_df.columns or col not in new_df.columns:
                raise ValueError(f"Key column '{col}' not found in both files")
        
        # Create comparison keys
        old_df['_key'] = old_df[key_columns].astype(str).agg('||'.join, axis=1)
        new_df['_key'] = new_df[key_columns].astype(str).agg('||'.join, axis=1)
        
        old_keys = set(old_df['_key'])
        new_keys = set(new_df['_key'])
        
        # Find differences
        added_keys = new_keys - old_keys
        deleted_keys = old_keys - new_keys
        common_keys = old_keys & new_keys
        
        print(f"\n📊 Comparison Results:")
        print(f"   Previous file: {len(old_df):,} rows")
        print(f"   New file:      {len(new_df):,} rows")
        print(f"   Added:         {len(added_keys):,} rows")
        print(f"   Deleted:       {len(deleted_keys):,} rows")
        print(f"   Common:        {len(common_keys):,} rows")
        
        # Get added and deleted rows
        added_df = new_df[new_df['_key'].isin(added_keys)].drop(columns=['_key'])
        deleted_df = old_df[old_df['_key'].isin(deleted_keys)].drop(columns=['_key'])
        
        # Find modified rows (same key, different content)
        old_common = old_df[old_df['_key'].isin(common_keys)].set_index('_key').drop(columns=['_row_hash'] if '_row_hash' in old_df.columns else [])
        new_common = new_df[new_df['_key'].isin(common_keys)].set_index('_key').drop(columns=['_row_hash'] if '_row_hash' in new_df.columns else [])
        
        # Compare row by row
        modified_keys = []
        for key in common_keys:
            if not old_common.loc[key].equals(new_common.loc[key]):
                modified_keys.append(key)
        
        modified_df = new_df[new_df['_key'].isin(modified_keys)].drop(columns=['_key'])
        unchanged_df = new_df[new_df['_key'].isin(common_keys - set(modified_keys))].drop(columns=['_key'])
        
        print(f"   Modified:      {len(modified_keys):,} rows")
        print(f"   Unchanged:     {len(unchanged_df):,} rows")
        
        # Clean up temporary columns
        if '_row_hash' in added_df.columns:
            added_df = added_df.drop(columns=['_row_hash'])
        if '_row_hash' in deleted_df.columns:
            deleted_df = deleted_df.drop(columns=['_row_hash'])
        if '_row_hash' in modified_df.columns:
            modified_df = modified_df.drop(columns=['_row_hash'])
        if '_row_hash' in unchanged_df.columns:
            unchanged_df = unchanged_df.drop(columns=['_row_hash'])
        
        return {
            'added': added_df,
            'deleted': deleted_df,
            'modified': modified_df,
            'unchanged': unchanged_df
        }
    
    def save_delta_files(self, result, carrier_name, timestamp):
        """Save delta files in multiple formats"""
        output_files = {}
        
        print("\n💾 Generating output files...")
        
        for change_type, df in result.items():
            if len(df) > 0 or change_type in ['added', 'modified']:  # Always create added/modified even if empty
                base_name = f"{carrier_name}_{change_type}_{timestamp}"
                
                # CSV for easy import
                csv_path = self.output_dir / f"{base_name}.csv"
                df.to_csv(csv_path, index=False)
                
                # Excel for review
                excel_path = self.output_dir / f"{base_name}.xlsx"
                df.to_excel(excel_path, index=False)
                
                output_files[change_type] = {
                    'csv': csv_path,
                    'excel': excel_path,
                    'row_count': len(df)
                }
                
                print(f"   ✓ {change_type}: {len(df):,} rows → {csv_path.name}")
        
        return output_files
    
    def generate_summary_report(self, result, carrier_name, timestamp, output_files):
        """Generate human-readable summary report"""
        report_path = self.output_dir / f"{carrier_name}_SUMMARY_{timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write(f"FORMULARY DELTA PROCESSING REPORT\n")
            f.write(f"Carrier: {carrier_name}\n")
            f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            f.write("CHANGE SUMMARY:\n")
            f.write("-"*70 + "\n")
            total_changes = len(result['added']) + len(result['deleted']) + len(result['modified'])
            f.write(f"Total Changes:        {total_changes:,}\n")
            f.write(f"  - Added:            {len(result['added']):,}\n")
            f.write(f"  - Deleted:          {len(result['deleted']):,}\n")
            f.write(f"  - Modified:         {len(result['modified']):,}\n")
            f.write(f"  - Unchanged:        {len(result['unchanged']):,}\n\n")
            
            if total_changes > 0:
                pct_change = (total_changes / (len(result['unchanged']) + total_changes)) * 100
                f.write(f"Percentage Changed:   {pct_change:.2f}%\n\n")
            
            f.write("\nOUTPUT FILES:\n")
            f.write("-"*70 + "\n")
            for change_type, files in output_files.items():
                f.write(f"\n{change_type.upper()}:\n")
                f.write(f"  CSV:   {files['csv'].name}\n")
                f.write(f"  Excel: {files['excel'].name}\n")
                f.write(f"  Rows:  {files['row_count']:,}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("RECOMMENDATION:\n")
            if total_changes < len(result['unchanged']) * 0.1:  # Less than 10% changed
                f.write("✓ Process ONLY the delta files (added + modified) for faster loading\n")
                f.write("  This will be significantly faster than processing the full file.\n")
            else:
                f.write("⚠ Large number of changes detected.\n")
                f.write("  Consider whether full file reload might be more efficient.\n")
            f.write("="*70 + "\n")
        
        print(f"\n📋 Summary report: {report_path}")
        
        # Also print to console
        with open(report_path, 'r') as f:
            print("\n" + f.read())


def main():
    parser = argparse.ArgumentParser(
        description='Process formulary files and generate delta changes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a new carrier file
  python formulary_delta_processor.py new_file.csv --carrier "CarrierA" --keys NDC PLAN_ID
  
  # Process Excel file
  python formulary_delta_processor.py new_file.xlsx --carrier "CarrierB" --keys DRUG_ID
  
  # Process pipe-delimited file
  python formulary_delta_processor.py new_file.txt --carrier "CarrierC" --keys NDC
        """
    )
    
    parser.add_argument('input_file', help='Path to new formulary file')
    parser.add_argument('--carrier', required=True, help='Carrier name (e.g., "UHC", "Aetna")')
    parser.add_argument('--keys', nargs='+', help='Key columns for comparison (e.g., NDC PLAN_ID)')
    parser.add_argument('--archive-dir', default='./archive', help='Directory for archived files')
    parser.add_argument('--output-dir', default='./output', help='Directory for output files')
    
    args = parser.parse_args()
    
    processor = FormularyDeltaProcessor(
        archive_dir=args.archive_dir,
        output_dir=args.output_dir
    )
    
    processor.compare_and_generate_delta(
        new_file=args.input_file,
        carrier_name=args.carrier,
        key_columns=args.keys
    )


if __name__ == '__main__':
    main()
