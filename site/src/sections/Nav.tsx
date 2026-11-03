import { content } from "../data/content";

export function Nav() {
  return (
    <nav className="top" aria-label="Main">
      <div className="wrap nav-inner">
        <a className="brand" href="#top">
          <img src={`${import.meta.env.BASE_URL}readme-icon.png`} alt="CipherScope" width={22} height={22} />
          {content.name}
        </a>
        <div className="links">
          {content.nav.links.map((l) => (
            <a key={l.href} href={l.href}>{l.label}</a>
          ))}
        </div>
        <div className="sp">
          <a className="pill" href="https://github.com/nihalmachhi/CipherScope">{content.nav.githubLabel}</a>
          <a className="pill w" href="#start">{content.nav.runLabel}</a>
        </div>
      </div>
    </nav>
  );
}
