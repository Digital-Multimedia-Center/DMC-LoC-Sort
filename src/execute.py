import pandas as pd
import re
import sys

def normalize_call_number(call_number):
    if pd.isna(call_number):
        return ''
    call_number = re.sub(r'([A-Z]+) (\d+)', r'\1\2', call_number)
    call_number = re.sub(r'(\d) \.', r'\1.', call_number)
    return call_number.strip()

loc_regex = re.compile(r'''
    ^\s*
    ([A-Z]{1,3})              # Class letters
    ([0-9]{1,4})              # Class number
    \.?
    ([0-9]{1,3})?             # Decimal subdivision (optional)
    \s*\.?
    ([A-Z]{1})                # First cutter letter
    ([0-9]{1,})               # First cutter number
    \s*
    (?:
        ([A-Z]{1,2})          # Optional second cutter letter
        ([0-9]{1,})?          # Optional second cutter number
    )?
    \s*
    ([0-9]{4})?               # Optional year
    (.*)?                     # Trailing media
''', re.VERBOSE)

def loc_sort_key(call_number):
    match = loc_regex.match(call_number)
    if not match:
        return [call_number]
    groups = match.groups()
    return [
        groups[0] or '',
        int(groups[1]) if groups[1] else 0,
        int(groups[2]) if groups[2] else -1,
        groups[3] or '',
        int(groups[4]) if groups[4] else 0,
        groups[5] or '',
        int(groups[6]) if groups[6] else 0,
        int(groups[7]) if groups[7] else 0,
        (groups[8] or '').strip()
    ]

def main(input_file, column_name, output_file):
    df = pd.read_csv(input_file)
    if column_name not in df.columns:
        print(f"Error: Column '{column_name}' not found in {input_file}")
        return
    df['normalized'] = df[column_name].apply(normalize_call_number)
    df['loc_sort_key'] = df['normalized'].apply(loc_sort_key)
    df_sorted = df.sort_values(by='loc_sort_key')
    df_sorted.drop(columns=['loc_sort_key'], inplace=True)
    df_sorted.to_csv(output_file, index=False)
    print(f"Sorted file written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sort_call_numbers.py input.csv column_name [output.csv]")
    else:
        input_csv = sys.argv[1]
        column_name = sys.argv[2]
        output_csv = sys.argv[3] if len(sys.argv) > 3 else "sorted_output.csv"
        main(input_csv, column_name, output_csv)
