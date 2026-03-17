let tests = [
  "ﾚﾎﾞｾﾁﾘｼﾞﾝ塩酸塩錠5MGﾄ-ﾜ 5mg PTP 500T",
  "ﾋﾞｵﾌｪﾙﾐﾝR散 ﾊﾞﾗ 500g",
  "ﾐｺﾝﾋﾞ配合錠BP 100T",
  "薬 5mL×5",
  "別の薬 9mg 18g×5",
  "ｾｲﾌﾙﾄ錠 250mg",
  "薬名 100管",
  "アムロジピン 10mg 100T",
  "(先) ﾛｷｿﾆﾝ錠 60mg PTP 100T"
];

for (let s of tests) {
    let orig = s;
    // (先)や(後)などの接頭辞を削除
    let cleaned = s.replace(/^\\([前後]\\)\\s*/, '');
    
    // PTPやバラなどの包装形態以降を削除
    cleaned = cleaned.replace(/\\s+(?:PTP|ﾊﾞﾗ)\\s*.*$/i, '');
    
    // 末尾の数量・単位の連続を削除 (例: " 9mg 18g×5", " 100T", " 5mL×5")
    cleaned = cleaned.replace(/(?:\\s+\\d+(?:\\.\\d+)?(?:mg|g|mL|T|管|カプセル|錠|包|瓶|本|枚|キット|シリンジ|V)?(?:[×x*]\\s*\\d+)?)+$/i, '');
    
    // 余分な末尾の空白を削除
    cleaned = cleaned.trim();
    
    console.log(`Original: ${orig}\nCleaned:  ${cleaned}\n`);
}
