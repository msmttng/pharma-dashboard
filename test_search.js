
const toHalfWidth = (str) => {
  if (!str) return "";
  return str.replace(/[！-～]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xfee0))
            .replace(/　/g, " ")
            .replace(/[ァ-ン]/g, s => {
              const map = {
                "ァ":"ｧ","ィ":"ｨ","ゥ":"ｩ","ェ":"ｪ","ォ":"ｫ","ッ":"ｯ","ャ":"ｬ","ュ":"ｭ","ョ":"ｮ",
                "ア":"ｱ","イ":"ｲ","ウ":"ｳ","エ":"ｴ","オ":"ｵ","カ":"ｶ","キ":"ｷ","ク":"ｸ","ケ":"ｹ","コ":"ｺ",
                "サ":"ｻ","シ":"ｼ","ス":"ｽ","セ":"ｾ","ソ":"ｿ","タ":"ﾀ","チ":"ﾁ","ツ":"ﾂ","テ":"ﾃ","ト":"ﾄ",
                "ナ":"ﾅ","ニ":"ﾆ","ヌ":"ﾇ","ネ":"ﾈ","ノ":"ﾉ","ハ":"ﾊ","ヒ":"ﾋ","フ":"ﾌ","ヘ":"ﾍ","ホ":"ﾎ",
                "マ":"ﾏ","ミ":"ﾐ","ム":"ﾑ","メ":"ﾒ","モ":"ﾓ","ヤ":"ﾔ","ユ":"ﾕ","ヨ":"ﾖ","ラ":"ﾗ","リ":"ﾘ",
                "ル":"ﾙ","レ":"ﾚ","ロ":"ﾛ","ワ":"ﾜ","ヲ":"ｦ","ン":"ﾝ"
              };
              return map[s] || s;
            })
            .replace(/ガ/g,"ｶﾞ").replace(/ギ/g,"ｷﾞ").replace(/グ/g,"ｸﾞ").replace(/ゲ/g,"ｹﾞ").replace(/ゴ/g,"ｺﾞ")
            .replace(/ザ/g,"ｻﾞ").replace(/ジ/g,"ｼﾞ").replace(/ズ/g,"ｽﾞ").replace(/ゼ/g,"ｾﾞ").replace(/ゾ/g,"ｿﾞ")
            .replace(/ダ/g,"ﾀﾞ").replace(/ヂ/g,"ﾁﾞ").replace(/ヅ/g,"ﾂﾞ").replace(/デ/g,"ﾃﾞ").replace(/ド/g,"ﾄﾞ")
            .replace(/バ/g,"ﾊﾞ").replace(/ビ/g,"ﾋﾞ").replace(/ブ/g,"ﾌﾞ").replace(/ベ/g,"ﾍﾞ").replace(/ボ/g,"ﾎﾞ")
            .replace(/パ/g,"ﾊﾟ").replace(/ピ/g,"ﾋﾟ").replace(/プ/g,"ﾌﾟ").replace(/ペ/g,"ﾍﾟ").replace(/ポ/g,"ﾎﾟ")
            .replace(/ヴ/g,"ｳﾞ");
};

const items = [
  { name: "ｱﾑﾛｼﾞﾋﾟﾝOD錠2.5mgﾄ-ﾜ     　     2.5mg PTP  100T" },
  { name: "ﾍﾞﾗﾊﾟﾐﾙ塩酸塩錠40MG ｢ﾀｲﾖ-｣   PTP   40MG    100T" }
];

const queries = ["アムロジピン", "PTP", "ptp"];

queries.forEach(q => {
  const normQ = toHalfWidth(q).toLowerCase();
  console.log(`Query: ${q} -> Normalized: ${normQ}`);
  items.forEach(item => {
    const normName = toHalfWidth(item.name).toLowerCase();
    const match = normName.indexOf(normQ) !== -1;
    console.log(`  Target: ${item.name}`);
    console.log(`  Match: ${match}`);
  });
});
