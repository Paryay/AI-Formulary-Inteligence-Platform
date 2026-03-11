#!/usr/bin/env python3
"""
SQL Generator for Delta Files
Generates SQL statements to load delta files into your database
"""

import pandas as pd
import argparse
from pathlib import Path


class DeltaSQLGenerator:
    """Generate SQL statements for loading delta files"""
    
    def __init__(self, table_name='formulary'):
        self.table_name = table_name
    
    def generate_insert_sql(self, csv_file, batch_size=1000):
        """Generate INSERT statements for added records"""
        df = pd.read_csv(csv_file)
        
        if len(df) == 0:
            return "-- No records to insert"
        
        columns = ', '.join(df.columns)
        sql_statements = []
        
        sql_statements.append(f"-- Inserting {len(df)} new records")
        sql_statements.append(f"INSERT INTO {self.table_name} ({columns}) VALUES")
        
        # Generate value rows
        for i, row in df.iterrows():
            values = ', '.join([self._format_value(v) for v in row.values])
            sql_statements.append(f"  ({values}){',' if i < len(df)-1 else ';'}")
            
            # Create batches for large inserts
            if (i + 1) % batch_size == 0 and i < len(df) - 1:
                sql_statements.append(f"\n-- Batch {(i+1)//batch_size}")
                sql_statements.append(f"INSERT INTO {self.table_name} ({columns}) VALUES")
        
        return '\n'.join(sql_statements)
    
    def generate_update_sql(self, csv_file, key_columns):
        """Generate UPDATE statements for modified records"""
        df = pd.read_csv(csv_file)
        
        if len(df) == 0:
            return "-- No records to update"
        
        sql_statements = [f"-- Updating {len(df)} modified records"]
        
        for i, row in df.iterrows():
            # Build SET clause (all non-key columns)
            set_clause = []
            for col in df.columns:
                if col not in key_columns:
                    set_clause.append(f"{col} = {self._format_value(row[col])}")
            
            # Build WHERE clause (key columns)
            where_clause = []
            for key in key_columns:
                where_clause.append(f"{key} = {self._format_value(row[key])}")
            
            sql = f"UPDATE {self.table_name} SET {', '.join(set_clause)} WHERE {' AND '.join(where_clause)};"
            sql_statements.append(sql)
        
        return '\n'.join(sql_statements)
    
    def generate_delete_sql(self, csv_file, key_columns, soft_delete=False):
        """Generate DELETE statements for removed records"""
        df = pd.read_csv(csv_file)
        
        if len(df) == 0:
            return "-- No records to delete"
        
        sql_statements = [f"-- Deleting {len(df)} removed records"]
        
        for i, row in df.iterrows():
            where_clause = []
            for key in key_columns:
                where_clause.append(f"{key} = {self._format_value(row[key])}")
            
            if soft_delete:
                # Soft delete - just mark as inactive
                sql = f"UPDATE {self.table_name} SET ACTIVE = 'N', DELETED_DATE = CURRENT_DATE WHERE {' AND '.join(where_clause)};"
            else:
                # Hard delete
                sql = f"DELETE FROM {self.table_name} WHERE {' AND '.join(where_clause)};"
            
            sql_statements.append(sql)
        
        return '\n'.join(sql_statements)
    
    def generate_merge_sql(self, added_file, modified_file, deleted_file, key_columns, soft_delete=False):
        """Generate complete MERGE or combined SQL script"""
        sql = []
        
        sql.append("-- =====================================================")
        sql.append("-- FORMULARY DELTA LOAD SCRIPT")
        sql.append(f"-- Generated: {pd.Timestamp.now()}")
        sql.append(f"-- Table: {self.table_name}")
        sql.append("-- =====================================================")
        sql.append("")
        sql.append("BEGIN TRANSACTION;")
        sql.append("")
        
        # Step 1: Delete
        if Path(deleted_file).exists():
            sql.append("-- Step 1: Remove deleted records")
            sql.append(self.generate_delete_sql(deleted_file, key_columns, soft_delete))
            sql.append("")
        
        # Step 2: Update
        if Path(modified_file).exists():
            sql.append("-- Step 2: Update modified records")
            sql.append(self.generate_update_sql(modified_file, key_columns))
            sql.append("")
        
        # Step 3: Insert
        if Path(added_file).exists():
            sql.append("-- Step 3: Insert new records")
            sql.append(self.generate_insert_sql(added_file))
            sql.append("")
        
        sql.append("COMMIT;")
        sql.append("")
        sql.append("-- =====================================================")
        sql.append("-- END OF SCRIPT")
        sql.append("-- =====================================================")
        
        return '\n'.join(sql)
    
    def _format_value(self, value):
        """Format a value for SQL"""
        if pd.isna(value):
            return 'NULL'
        elif isinstance(value, str):
            # Escape single quotes
            escaped = str(value).replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return f"'{str(value)}'"


def main():
    parser = argparse.ArgumentParser(description='Generate SQL for loading delta files')
    parser.add_argument('--carrier', required=True, help='Carrier name')
    parser.add_argument('--timestamp', required=True, help='Timestamp from delta files (e.g., 20240215_103045)')
    parser.add_argument('--table', default='formulary', help='Target table name')
    parser.add_argument('--keys', nargs='+', required=True, help='Key columns')
    parser.add_argument('--soft-delete', action='store_true', help='Use soft delete (set ACTIVE=N)')
    parser.add_argument('--output-dir', default='./output', help='Output directory')
    
    args = parser.parse_args()
    
    # Build filenames
    added_file = f"{args.output_dir}/{args.carrier}_added_{args.timestamp}.csv"
    modified_file = f"{args.output_dir}/{args.carrier}_modified_{args.timestamp}.csv"
    deleted_file = f"{args.output_dir}/{args.carrier}_deleted_{args.timestamp}.csv"
    
    # Generate SQL
    generator = DeltaSQLGenerator(table_name=args.table)
    
    sql_script = generator.generate_merge_sql(
        added_file=added_file,
        modified_file=modified_file,
        deleted_file=deleted_file,
        key_columns=args.keys,
        soft_delete=args.soft_delete
    )
    
    # Save to file
    output_file = f"{args.output_dir}/{args.carrier}_LOAD_{args.timestamp}.sql"
    with open(output_file, 'w') as f:
        f.write(sql_script)
    
    print(f"✓ Generated SQL script: {output_file}")
    print("\nYou can now execute this SQL script in your database.")
    
    # Also print preview
    print("\n" + "="*70)
    print("SQL PREVIEW:")
    print("="*70)
    lines = sql_script.split('\n')
    print('\n'.join(lines[:50]))  # Show first 50 lines
    if len(lines) > 50:
        print("\n... (truncated, see full file for complete script)")


if __name__ == '__main__':
    main()
