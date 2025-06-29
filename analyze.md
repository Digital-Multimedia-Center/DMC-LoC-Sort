# DMC LCC Sort
Many library databases have LCC call numbers stored as string literals which cannot be sorted with a simple sort since LCC reads left to right and normal sorts would go right to left. Even reversing the string, there's deficiencies.

This project will probably contain an API that takes in a file and sorts by the LCC classification system and a frontend to upload files to get sorted.

![LCC Classification System](https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/G%26G_LCC_Call_number.png/1599px-G%26G_LCC_Call_number.png)

Importing and inspecting our input data and expected sort


```python
import pandas as pd
import re

raw_df = pd.read_csv("data/input.csv")
expected_df = pd.read_csv("data/expected.csv")
```


```python
raw_call_numbers = raw_df["item_effective_call_number"]
expected_call_numbers = expected_df["item_effective_call_number"]
```

Attempting a simple sort


```python
sorted_call_numbers = raw_call_numbers.sort_values().reset_index(drop=True)

simple_sort = pd.DataFrame({
    "sorted_call_numbers": sorted_call_numbers,
    "expected_call_numbers": expected_call_numbers 
})
```

A simple sort doesn't work, as we can see here on `index 9`, call number `B105` is mismatched with the expected `B72`, because the regular sort goes right to left and puts `2004` before `2008`.

`simple_sort`

| Index | Raw Call Number              | Expected Call Number        |
|-------|------------------------------|-----------------------------|
| 9     | B105.A8 E24 2004 VideoDVD, 1 | B72.G73 A7 2008 VideoDVD, 1 |
| 10    | B105.W6 F465 2009 VideoDVD, 1 | B105.A8 E24 2004 VideoDVD, 1 |
| 11    | B105.W6 F465 2009 VideoDVD, 1 | B105.W6 F465 2009 VideoDVD, 1 |
| 12    | B105.W6 F465 2009 VideoDVD, 1 | B105.W6 F465 2009 VideoDVD, 1 |
| 13    | B105.W6 F465 2009 VideoDVD, 1 | B105.W6 F465 2009 VideoDVD, 1 |
| 14    | B105.W6 F465 2009 VideoDVD, 1 | B105.W6 F465 2009 VideoDVD, 1 |
| 15    | B105.W6 F465 2009 VideoDVD, 1 | B105.W6 F465 2009 VideoDVD, 1 |
| 16    | B108 .R66 2002 VideoDVD, 1   | B105.W6 F465 2009 VideoDVD, 1 |
| 17    | B108 .R66 2002 VideoDVD, 1   | B108.R66 2002 VideoDVD, 1   |


The raw call numbers need cleaning. When comparing values, some have missing decimal places, like this:

`simple_sort`

| Index | Raw Call Number         | Expected Call Number    |
|-------|-------------------------|-------------------------|
| 0     | 137 529 THS, 1          | 137.529 THS, 1         |
| 1     | 138 093 THS, 1          | 138.093 THS, 1         |


Normalizing our call numbers


```python
def normalize_call_number(call_number):
    call_number = re.sub(r'([A-Z]+) (\d+)', r'\1\2', call_number)
    call_number = re.sub(r'(\d) \.', r'\1.', call_number)

    return call_number

raw_call_number = "137 529 THS, 1"
fixed_call_number = normalize_call_number(raw_call_number)

print(raw_call_number)
print(fixed_call_number)
```

    137 529 THS, 1
    137 529 THS, 1



```python
normalized_raw_callnumbers = raw_call_numbers.apply(normalize_call_number)

raw_vs_normalized = pd.DataFrame({
    "raw": raw_call_numbers,
    "normalized": normalized_raw_callnumbers
})

raw_vs_normalized_different = raw_vs_normalized[raw_vs_normalized["raw"] != raw_vs_normalized["normalized"]]

raw_vs_normalized_different.reset_index(drop=True, inplace=True)
```

`raw_vs_normalized_different`, shows all rows that have been been changed after normalization. Now that the rows have been normalized, we need a comparator made for the LoC classification.


```python
# Regex updated to capture trailing media or extra info as a literal group
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
        print(f"Warning: Couldn't parse call number: {call_number}")
        return [call_number]

    groups = match.groups()

    class_letters     = groups[0] or ''
    class_number      = int(groups[1]) if groups[1] else 0
    decimal_part      = int(groups[2]) if groups[2] else -1
    cutter1_letter    = groups[3] or ''
    cutter1_number    = int(groups[4]) if groups[4] else 0
    cutter2_letter    = groups[5] or ''
    cutter2_number    = int(groups[6]) if groups[6] else 0
    year              = int(groups[7]) if groups[7] else 0
    trailing_info     = groups[8].strip() if groups[8] else ''

    return [
        class_letters,
        class_number,
        decimal_part,
        cutter1_letter,
        cutter1_number,
        cutter2_letter,
        cutter2_number,
        year,
        trailing_info
    ]

print(raw_call_number, loc_sort_key(raw_call_number))
print("HV6049.O437 2005 VideoDVD, 1", loc_sort_key("HV6049.O437 2005 VideoDVD, 1"))
print("PS3563.C3868 H68 1998 VideoDVD, 1", loc_sort_key("PS3563.C3868 H68 1998 VideoDVD, 1"))
```

    Warning: Couldn't parse call number: 137 529 THS, 1
    137 529 THS, 1 ['137 529 THS, 1']
    HV6049.O437 2005 VideoDVD, 1 ['HV', 6049, -1, 'O', 437, '', 0, 2005, 'VideoDVD, 1']
    PS3563.C3868 H68 1998 VideoDVD, 1 ['PS', 3563, -1, 'C', 3868, 'H', 68, 1998, 'VideoDVD, 1']


That first call number is a dewey decimal call number and therefore doesn't get parsed.


```python
raw_vs_normalized["loc_sort_key"] = raw_vs_normalized["normalized"].apply(loc_sort_key)
raw_vs_normalized["sort_key_len"] = raw_vs_normalized["loc_sort_key"].apply(len)

raw_vs_normalized.groupby("sort_key_len", group_keys=False).apply(
    lambda x: x.sample(n=min(len(x), 5), random_state=42)
)

normalized_sort = raw_vs_normalized.sort_values(by="loc_sort_key", key=lambda x: x.apply(tuple))
```

The above sort works for almost all values, barring 52 call number which is a small percentage.
