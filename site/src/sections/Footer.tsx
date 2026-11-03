import { content } from "../data/content";

export function Footer() {
  return <footer className="wrap"><div className="foot">
    <div className="fcols">
      <div><a className="brand" href="#top"><img src={`${import.meta.env.BASE_URL}readme-icon.png`} alt="" width={24} height={24} />{content.name}</a><p className="tg">{content.footer.blurb}</p></div>
      <div><h5>{content.footer.explore}</h5><ul>{content.footer.columns[0].map((label, index) => <li key={label}><a href={["#how", "#try", "#results"][index]}>{label}</a></li>)}</ul></div>
      <div><h5>{content.footer.project}</h5><ul>{content.footer.columns[1].map((label, index) => <li key={label}><a href={["#features", "#start", "#faq"][index]}>{label}</a></li>)}</ul></div>
      <div><h5>{content.footer.source}</h5><ul>{content.footer.columns[2].map((label, index) => <li key={label}><a href={["https://github.com/nihalmachhi/CipherScope", "https://github.com/nihalmachhi/CipherScope/tree/main/docs", "https://github.com/nihalmachhi/CipherScope/tree/main/src", "https://github.com/nihalmachhi/CipherScope/issues"][index]}>{label}</a></li>)}</ul></div>
    </div>
    <div className="fbot"><span>{content.footer.note}</span><span>{content.footer.mit}</span></div>
    <div className="mark" aria-hidden="true">CipherScope</div>
  </div></footer>;
}
