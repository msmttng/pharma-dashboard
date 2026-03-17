import re

def normalize_units(name):
    if not name: return ""
    def replacer_multi(match):
        num = match.group(1)
        space = match.group(2)
        unit = match.group(3).upper()
        if unit == 'MG': unit = 'mg'
        elif unit == 'ML': unit = 'mL'
        elif unit == 'KG': unit = 'kg'
        elif unit == 'UG': unit = 'μg'
        elif unit == 'MCG': unit = 'μg'
        elif unit == 'G': unit = 'g'
        return f"{num}{space}{unit}"

    # Match unit (MG|ML|KG|UG|MCG|G) if it's followed by a non-letter, 'X', 'x', or end of string.
    # We use a positive lookahead (?=[^A-Za-z]|[Xx]|$)
    name = re.sub(r'(\d+(?:\.\d+)?)(\s*)(MG|ML|KG|UG|MCG|G)(?=[^A-Za-z]|[Xx]|$)', replacer_multi, name, flags=re.IGNORECASE)

    return name

tests = [
    '20MG', '5MLX10', '5mLx10', '100T', '18G', 
    'NIG 20MG PTP', 'アムロジピン 10mg 100T', '10.5MG', 
    '5MLボトル', '18G×5', 'NIG', 'JG'
]
for t in tests:
    print(f'{t} -> {normalize_units(t)}')
