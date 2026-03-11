#!/usr/bin/env python3
"""
Demo script showing how the formulary delta processor works
Creates sample data and runs through the workflow
"""

import pandas as pd
import os
from pathlib import Path

# Create sample directories
Path('./demo_input').mkdir(exist_ok=True)
Path('./archive').mkdir(exist_ok=True)
Path('./output').mkdir(exist_ok=True)

print("Creating sample formulary data...\n")

# Create January file (baseline)
january_data = {
    'NDC': ['12345-678-90', '23456-789-01', '34567-890-12', '45678-901-23', '56789-012-34'],
    'PLAN_ID': ['PLAN001', 'PLAN001', 'PLAN002', 'PLAN002', 'PLAN003'],
    'DRUG_NAME': ['Lipitor 10mg', 'Metformin 500mg', 'Lisinopril 10mg', 'Omeprazole 20mg', 'Atorvastatin 20mg'],
    'TIER': [2, 1, 1, 1, 2],
    'COPAY': [25.00, 10.00, 10.00, 10.00, 25.00],
    'PRIOR_AUTH': ['N', 'N', 'N', 'N', 'Y']
}

jan_df = pd.DataFrame(january_data)
jan_df.to_csv('./demo_input/UHC_January_2024.csv', index=False)
print("✓ Created January file (5 drugs)")

# Create February file with changes
february_data = {
    'NDC': [
        '12345-678-90',  # Unchanged
        '23456-789-01',  # Modified (copay changed)
        '34567-890-12',  # Unchanged
        # '45678-901-23' - DELETED
        '56789-012-34',  # Modified (tier changed)
        '67890-123-45',  # NEW DRUG
        '78901-234-56',  # NEW DRUG
    ],
    'PLAN_ID': ['PLAN001', 'PLAN001', 'PLAN002', 'PLAN003', 'PLAN001', 'PLAN002'],
    'DRUG_NAME': [
        'Lipitor 10mg',
        'Metformin 500mg',
        'Lisinopril 10mg',
        'Atorvastatin 20mg',
        'Gabapentin 300mg',  # New
        'Amlodipine 5mg'     # New
    ],
    'TIER': [2, 1, 1, 3, 1, 1],  # Atorvastatin tier changed from 2 to 3
    'COPAY': [25.00, 15.00, 10.00, 35.00, 10.00, 10.00],  # Metformin copay changed from 10 to 15
    'PRIOR_AUTH': ['N', 'N', 'N', 'Y', 'N', 'N']
}

feb_df = pd.DataFrame(february_data)
feb_df.to_csv('./demo_input/UHC_February_2024.csv', index=False)
print("✓ Created February file (6 drugs)")

print("\nChanges in February file:")
print("  - 1 deleted: Omeprazole")
print("  - 2 added: Gabapentin, Amlodipine")
print("  - 2 modified: Metformin (copay), Atorvastatin (tier)")
print("  - 2 unchanged: Lipitor, Lisinopril")

print("\n" + "="*70)
print("DEMO: First Month Processing (January)")
print("="*70)
print("\nRun this command:")
print("python formulary_delta_processor.py demo_input/UHC_January_2024.csv --carrier UHC --keys NDC PLAN_ID")

print("\n" + "="*70)
print("DEMO: Second Month Processing (February)")
print("="*70)
print("\nThen run this command:")
print("python formulary_delta_processor.py demo_input/UHC_February_2024.csv --carrier UHC --keys NDC PLAN_ID")

print("\n" + "="*70)
print("Expected Results:")
print("="*70)
print("""
The second run will generate delta files:
- UHC_added_*.csv: 2 rows (Gabapentin, Amlodipine)
- UHC_deleted_*.csv: 1 row (Omeprazole)
- UHC_modified_*.csv: 2 rows (Metformin, Atorvastatin)
- UHC_unchanged_*.csv: 2 rows (Lipitor, Lisinopril)

Instead of loading all 6 rows, you only need to process 5 (2+1+2).
For larger files with millions of rows, this saves significant time!
""")

print("\n" + "="*70)
print("Try it now! Run the commands above to see the delta processor in action.")
print("="*70)
