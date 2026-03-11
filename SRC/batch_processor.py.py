#!/usr/bin/env python3
"""
Batch Formulary Processor
Process multiple carrier files in one go
"""

import yaml
import sys
from pathlib import Path
from formulary_delta_processor import FormularyDeltaProcessor

# Example configuration
CARRIER_CONFIG = {
    'UnitedHealthcare': {
        'file_pattern': '*UHC*.csv',
        'key_columns': ['NDC', 'PLAN_ID'],
        'delimiter': ','
    },
    'Aetna': {
        'file_pattern': '*Aetna*.txt',
        'key_columns': ['NDC', 'NETWORK'],
        'delimiter': '|'
    },
    'Cigna': {
        'file_pattern': '*Cigna*.xlsx',
        'key_columns': ['DRUG_ID'],
        'delimiter': None  # Excel
    },
    'Humana': {
        'file_pattern': '*Humana*.csv',
        'key_columns': ['NDC', 'FORMULARY_ID'],
        'delimiter': ','
    }
}


def process_batch(input_dir, config=CARRIER_CONFIG):
    """Process all carrier files in a directory"""
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Error: Directory {input_dir} not found")
        return
    
    processor = FormularyDeltaProcessor(
        archive_dir='./archive',
        output_dir='./output'
    )
    
    results = {}
    
    print("\n" + "="*70)
    print("BATCH FORMULARY PROCESSING")
    print("="*70)
    
    for carrier, cfg in config.items():
        print(f"\n\nSearching for {carrier} files...")
        files = list(input_path.glob(cfg['file_pattern']))
        
        if not files:
            print(f"  ⚠ No files found matching pattern: {cfg['file_pattern']}")
            continue
        
        # Process most recent file if multiple found
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        print(f"  ✓ Found: {latest_file.name}")
        
        try:
            output = processor.compare_and_generate_delta(
                new_file=latest_file,
                carrier_name=carrier,
                key_columns=cfg['key_columns']
            )
            results[carrier] = {
                'status': 'success',
                'file': latest_file.name,
                'output': output
            }
        except Exception as e:
            print(f"  ✗ Error processing {carrier}: {e}")
            results[carrier] = {
                'status': 'error',
                'file': latest_file.name,
                'error': str(e)
            }
    
    # Summary
    print("\n\n" + "="*70)
    print("BATCH PROCESSING SUMMARY")
    print("="*70)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    error_count = sum(1 for r in results.values() if r['status'] == 'error')
    
    print(f"\nTotal Carriers: {len(results)}")
    print(f"Successful:     {success_count}")
    print(f"Errors:         {error_count}")
    
    if error_count > 0:
        print("\nErrors:")
        for carrier, result in results.items():
            if result['status'] == 'error':
                print(f"  ✗ {carrier}: {result['error']}")
    
    print("\n" + "="*70)


def create_config_template():
    """Create a YAML configuration template"""
    template = """
# Carrier Configuration Template
# Customize this for your specific carriers and file formats

carriers:
  UnitedHealthcare:
    file_pattern: "*UHC*.csv"
    key_columns:
      - NDC
      - PLAN_ID
    
  Aetna:
    file_pattern: "*Aetna*.txt"
    key_columns:
      - NDC
      - NETWORK
    
  Cigna:
    file_pattern: "*Cigna*.xlsx"
    key_columns:
      - DRUG_ID
    
  Humana:
    file_pattern: "*Humana*.csv"
    key_columns:
      - NDC
      - FORMULARY_ID

# Add more carriers as needed
"""
    
    with open('carrier_config.yaml', 'w') as f:
        f.write(template)
    
    print("✓ Created carrier_config.yaml template")
    print("  Customize this file with your carrier specifications")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch process multiple carrier formulary files')
    parser.add_argument('input_dir', nargs='?', help='Directory containing carrier files')
    parser.add_argument('--create-config', action='store_true', 
                       help='Create configuration template')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_config_template()
    elif args.input_dir:
        process_batch(args.input_dir)
    else:
        parser.print_help()
