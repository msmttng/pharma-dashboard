import re

tests = [
    "ﾚﾎﾞｾﾁﾘｼﾞﾝ塩酸塩錠5MGﾄ-ﾜ 5mg PTP 500T",
    "ﾋﾞｵﾌｪﾙﾐﾝR散 ﾊﾞﾗ 500g",
    "ﾐｺﾝﾋﾞ配合錠BP 100T",
    "薬 5mL×5",
    "別の薬 9mg 18GX5",
    "ｾｲﾌﾙﾄ錠 250mg",
    "薬名 100管",
    "アムロジピン 10mg カプセル 100T",
    "(先) ﾛｷｿﾆﾝ錠 60mg PTP 100T",
    "テスト薬 10ﾎﾝ",
    "カプセルテスト 100カプセル",
    "パッチ 7ﾏｲX10",
    "シロップ 2.5mlX5"
]

for s in tests:
    orig = s
    
    # 1. (先)や(後)などの接頭辞を削除するパターン (JavaScript: /^\\([前後]\\)\\s*/ )
    cleaned = re.sub(r'^[（(][前後][)）]\s*', '', s)
    
    # 2. PTPやﾊﾞﾗ以降を削除 (JavaScript: /\s+(?:PTP|ﾊﾞﾗ)\s*.*$/i )
    cleaned = re.sub(r'\s+(?:PTP|ﾊﾞﾗ)\s*.*$', '', cleaned, flags=re.IGNORECASE)
    
    # 3. 末尾の数量・単位の連続を削除
    # 単位: mg, g, mL, ml, T, 管, カプセル, カプ, 錠, 包, 瓶, 本, ﾎﾝ, 枚, ﾏｲ, キット, シリンジ, V
    # x/X/×/* による掛け算に対応
    unit_pattern = r'(?:mg|g|mL|ml|T|管|カプセル|カプ|錠|包|瓶|本|ﾎﾝ|枚|ﾏｲ|キット|シリンジ|V)'
    cleaned = re.sub(rf'(?:\s+\d+(?:\.\d+)?{unit_pattern}?(?:\s*[×xX*]\s*\d+)?)+$', '', cleaned, flags=re.IGNORECASE)
    
    # 4. 前後の空白文字を削除
    cleaned = cleaned.strip()
    
    print(f"Original: {orig}")
    print(f"Cleaned:  '{cleaned}'\n")
