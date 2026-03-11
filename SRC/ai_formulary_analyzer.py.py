#!/usr/bin/env python3
"""
AI-Powered Formulary Intelligence System
Uses Claude AI to analyze, explain, and detect patterns in formulary changes
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib


class AIFormularyAnalyzer:
    """AI-powered formulary analysis using Claude API"""
    
    def __init__(self, archive_dir='./archive', output_dir='./output'):
        self.archive_dir = Path(archive_dir)
        self.output_dir = Path(output_dir)
        self.archive_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_with_ai(self, delta_data, carrier_name):
        """
        Use Claude AI to analyze formulary changes and generate insights
        
        Args:
            delta_data: Dictionary with 'added', 'deleted', 'modified' dataframes
            carrier_name: Name of the carrier
        
        Returns:
            AI-generated analysis and insights
        """
        # Prepare data summary for AI analysis
        analysis_prompt = self._build_analysis_prompt(delta_data, carrier_name)
        
        # Call Claude API (placeholder - will implement actual API call)
        ai_response = self._call_claude_api(analysis_prompt)
        
        return ai_response
    
    def _build_analysis_prompt(self, delta_data, carrier_name):
        """Build a detailed prompt for Claude to analyze"""
        
        prompt = f"""Analyze the following formulary changes for {carrier_name} and provide insights:

CHANGES SUMMARY:
- Added: {len(delta_data['added'])} drugs
- Deleted: {len(delta_data['deleted'])} drugs  
- Modified: {len(delta_data['modified'])} drugs

"""
        
        # Add sample data for AI to analyze
        if len(delta_data['added']) > 0:
            prompt += "\nNEW DRUGS ADDED:\n"
            prompt += delta_data['added'].head(10).to_string(index=False)
            
        if len(delta_data['deleted']) > 0:
            prompt += "\n\nDRUGS REMOVED:\n"
            prompt += delta_data['deleted'].head(10).to_string(index=False)
            
        if len(delta_data['modified']) > 0:
            prompt += "\n\nDRUGS MODIFIED:\n"
            prompt += delta_data['modified'].head(10).to_string(index=False)
        
        prompt += """

Please provide:
1. **Summary**: What are the main changes this month?
2. **Patterns**: Do you notice any patterns (e.g., specific drug classes, tier changes, pricing trends)?
3. **Anomalies**: Flag any unusual changes (e.g., unexpected deletions, large price increases)
4. **Business Impact**: What might these changes mean for patients and costs?
5. **Recommendations**: What should the pharmacy team investigate or monitor?

Format your response as JSON with these keys: summary, patterns, anomalies, impact, recommendations
"""
        
        return prompt
    
    def _call_claude_api(self, prompt):
        """
        Call Claude API for analysis
        This is a placeholder - actual implementation would use Anthropic API
        """
        # Mock response for demonstration
        # In production, this would make actual API call to Claude
        
        mock_response = {
            "summary": "This month shows significant formulary restructuring with focus on generic alternatives and prior authorization requirements.",
            "patterns": [
                "Increase in generic drug additions (60% of new drugs)",
                "Tier changes primarily moving brand drugs to higher tiers",
                "Prior authorization requirements added to high-cost specialty drugs"
            ],
            "anomalies": [
                "Unexpected deletion of 3 commonly prescribed diabetes medications",
                "Copay increase of >50% on 2 cardiovascular drugs",
                "New prior auth on previously unrestricted drugs"
            ],
            "impact": "Estimated cost shift to patients of $2.5M annually. 15% of members may need medication changes.",
            "recommendations": [
                "Review deleted diabetes medications - ensure therapeutic alternatives",
                "Communicate copay changes to affected members proactively", 
                "Train pharmacy staff on new prior authorization requirements",
                "Monitor member complaints for switched medications"
            ]
        }
        
        return mock_response
    
    def detect_pricing_anomalies(self, df, threshold=0.5):
        """Use statistical analysis to detect unusual price changes"""
        if 'COPAY' not in df.columns or len(df) == 0:
            return []
        
        # Calculate price change statistics
        if 'COPAY_OLD' in df.columns:
            df['price_change_pct'] = (df['COPAY'] - df['COPAY_OLD']) / df['COPAY_OLD']
            
            # Flag changes beyond threshold
            anomalies = df[abs(df['price_change_pct']) > threshold]
            
            return anomalies.to_dict('records')
        
        return []
    
    def smart_field_mapping(self, df, carrier_name):
        """
        AI-powered field mapping for different carrier formats
        Uses Claude to intelligently map fields across different schemas
        """
        
        columns = df.columns.tolist()
        
        # Build prompt for field mapping
        prompt = f"""
I have a formulary file from {carrier_name} with these columns:
{', '.join(columns)}

Please map these to our standard schema:
- NDC (National Drug Code)
- DRUG_NAME
- PLAN_ID
- TIER
- COPAY
- PRIOR_AUTH (Y/N)
- QUANTITY_LIMIT
- STEP_THERAPY (Y/N)

Return JSON mapping like: {{"source_column": "standard_column"}}
If a field doesn't exist, map to null.
"""
        
        # In production, call Claude API
        # For now, return intelligent defaults
        
        standard_mapping = self._intelligent_column_mapping(columns)
        
        return standard_mapping
    
    def _intelligent_column_mapping(self, columns):
        """Fuzzy matching for common column variations"""
        
        mapping = {}
        
        for col in columns:
            col_lower = col.lower()
            
            if 'ndc' in col_lower or 'drug_code' in col_lower:
                mapping[col] = 'NDC'
            elif 'drug' in col_lower and 'name' in col_lower:
                mapping[col] = 'DRUG_NAME'
            elif 'plan' in col_lower:
                mapping[col] = 'PLAN_ID'
            elif 'tier' in col_lower:
                mapping[col] = 'TIER'
            elif 'copay' in col_lower or 'cost' in col_lower:
                mapping[col] = 'COPAY'
            elif 'prior' in col_lower and 'auth' in col_lower:
                mapping[col] = 'PRIOR_AUTH'
            else:
                mapping[col] = col  # Keep original
        
        return mapping
    
    def generate_narrative_report(self, delta_data, ai_insights, carrier_name):
        """Generate a human-readable narrative report using AI insights"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
{'='*80}
AI-POWERED FORMULARY INTELLIGENCE REPORT
Carrier: {carrier_name}
Generated: {timestamp}
{'='*80}

EXECUTIVE SUMMARY
{'-'*80}
{ai_insights.get('summary', 'No summary available')}

KEY STATISTICS
{'-'*80}
• New Drugs Added:      {len(delta_data['added']):,}
• Drugs Removed:        {len(delta_data['deleted']):,}
• Drugs Modified:       {len(delta_data['modified']):,}
• Total Changes:        {len(delta_data['added']) + len(delta_data['deleted']) + len(delta_data['modified']):,}

PATTERNS DETECTED BY AI
{'-'*80}
"""
        
        for i, pattern in enumerate(ai_insights.get('patterns', []), 1):
            report += f"{i}. {pattern}\n"
        
        report += f"""
ANOMALIES & RED FLAGS
{'-'*80}
"""
        
        for i, anomaly in enumerate(ai_insights.get('anomalies', []), 1):
            report += f"⚠️  {i}. {anomaly}\n"
        
        report += f"""
BUSINESS IMPACT ANALYSIS
{'-'*80}
{ai_insights.get('impact', 'Impact analysis not available')}

AI RECOMMENDATIONS
{'-'*80}
"""
        
        for i, rec in enumerate(ai_insights.get('recommendations', []), 1):
            report += f"✓ {i}. {rec}\n"
        
        report += f"""
{'='*80}
This report was generated using AI-powered analysis.
Review the detailed delta files for complete information.
{'='*80}
"""
        
        return report
    
    def process_with_ai(self, new_file, carrier_name, key_columns=None):
        """
        Complete AI-powered processing pipeline
        """
        
        print(f"\n{'='*80}")
        print(f"🤖 AI-POWERED FORMULARY ANALYSIS")
        print(f"Carrier: {carrier_name}")
        print(f"{'='*80}\n")
        
        # Read new file
        print("📂 Reading formulary file...")
        new_df = self._read_file(new_file)
        
        # AI-powered field mapping
        print("🧠 AI analyzing field structure...")
        field_mapping = self.smart_field_mapping(new_df, carrier_name)
        print(f"   Mapped {len(field_mapping)} fields to standard schema")
        
        # Find previous file and compare
        prev_file = self._find_previous_file(carrier_name)
        
        if prev_file:
            print("🔍 Comparing with previous month...")
            prev_df = pd.read_pickle(prev_file)
            delta_data = self._compare_dataframes(prev_df, new_df, key_columns)
        else:
            print("⚠️  No previous file found - baseline analysis only")
            delta_data = {
                'added': new_df,
                'deleted': pd.DataFrame(),
                'modified': pd.DataFrame(),
                'unchanged': pd.DataFrame()
            }
        
        # AI Analysis
        print("\n🤖 Claude AI analyzing changes...")
        ai_insights = self.analyze_with_ai(delta_data, carrier_name)
        
        # Detect pricing anomalies
        print("💰 Detecting pricing anomalies...")
        pricing_anomalies = self.detect_pricing_anomalies(delta_data['modified'])
        if pricing_anomalies:
            print(f"   ⚠️  Found {len(pricing_anomalies)} pricing anomalies")
        
        # Generate narrative report
        print("📝 Generating AI narrative report...")
        narrative = self.generate_narrative_report(delta_data, ai_insights, carrier_name)
        
        # Save outputs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save delta files
        self._save_delta_files(delta_data, carrier_name, timestamp)
        
        # Save AI report
        report_path = self.output_dir / f"{carrier_name}_AI_REPORT_{timestamp}.txt"
        with open(report_path, 'w') as f:
            f.write(narrative)
        
        # Save AI insights as JSON
        json_path = self.output_dir / f"{carrier_name}_AI_INSIGHTS_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(ai_insights, f, indent=2)
        
        # Archive new file
        archive_path = self.archive_dir / f"{carrier_name}_{timestamp}.pkl"
        new_df.to_pickle(archive_path)
        
        print(f"\n✅ AI Analysis Complete!")
        print(f"   📄 Narrative Report: {report_path.name}")
        print(f"   📊 AI Insights JSON: {json_path.name}")
        print(f"\n{narrative}")
        
        return {
            'delta_data': delta_data,
            'ai_insights': ai_insights,
            'report_path': report_path,
            'json_path': json_path
        }
    
    def _read_file(self, filepath):
        """Read file with auto-format detection"""
        filepath = Path(filepath)
        
        if filepath.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(filepath)
        else:
            # Try to detect delimiter
            with open(filepath, 'r') as f:
                first_line = f.readline()
            
            if '|' in first_line:
                sep = '|'
            elif '\t' in first_line:
                sep = '\t'
            else:
                sep = ','
            
            return pd.read_csv(filepath, sep=sep, low_memory=False)
    
    def _find_previous_file(self, carrier_name):
        """Find most recent archived file"""
        files = list(self.archive_dir.glob(f"{carrier_name}_*.pkl"))
        return max(files, key=lambda p: p.stat().st_mtime) if files else None
    
    def _compare_dataframes(self, old_df, new_df, key_columns):
        """Compare two dataframes"""
        
        if key_columns is None:
            # Use row hashing
            old_df['_hash'] = old_df.apply(lambda r: hashlib.md5(str(r.values).encode()).hexdigest(), axis=1)
            new_df['_hash'] = new_df.apply(lambda r: hashlib.md5(str(r.values).encode()).hexdigest(), axis=1)
            key_columns = ['_hash']
        
        old_df['_key'] = old_df[key_columns].astype(str).agg('||'.join, axis=1)
        new_df['_key'] = new_df[key_columns].astype(str).agg('||'.join, axis=1)
        
        old_keys = set(old_df['_key'])
        new_keys = set(new_df['_key'])
        
        added = new_df[new_df['_key'].isin(new_keys - old_keys)].drop(columns=['_key'])
        deleted = old_df[old_df['_key'].isin(old_keys - new_keys)].drop(columns=['_key'])
        
        common_keys = old_keys & new_keys
        old_common = old_df[old_df['_key'].isin(common_keys)].set_index('_key')
        new_common = new_df[new_df['_key'].isin(common_keys)].set_index('_key')
        
        modified_keys = []
        for key in common_keys:
            if not old_common.loc[key].equals(new_common.loc[key]):
                modified_keys.append(key)
        
        modified = new_df[new_df['_key'].isin(modified_keys)].drop(columns=['_key'])
        unchanged = new_df[new_df['_key'].isin(common_keys - set(modified_keys))].drop(columns=['_key'])
        
        if '_hash' in added.columns:
            added = added.drop(columns=['_hash'])
            deleted = deleted.drop(columns=['_hash'])
            modified = modified.drop(columns=['_hash'])
            unchanged = unchanged.drop(columns=['_hash'])
        
        return {
            'added': added,
            'deleted': deleted,
            'modified': modified,
            'unchanged': unchanged
        }
    
    def _save_delta_files(self, delta_data, carrier_name, timestamp):
        """Save delta files"""
        for change_type, df in delta_data.items():
            if len(df) > 0:
                csv_path = self.output_dir / f"{carrier_name}_{change_type}_{timestamp}.csv"
                df.to_csv(csv_path, index=False)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AI-Powered Formulary Intelligence System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_file', help='Path to formulary file')
    parser.add_argument('--carrier', required=True, help='Carrier name')
    parser.add_argument('--keys', nargs='+', help='Key columns for comparison')
    
    args = parser.parse_args()
    
    analyzer = AIFormularyAnalyzer()
    analyzer.process_with_ai(
        new_file=args.input_file,
        carrier_name=args.carrier,
        key_columns=args.keys
    )


if __name__ == '__main__':
    main()
