import { Nav } from "./sections/Nav";
import { Hero } from "./sections/Hero";
import { Pipeline } from "./sections/Pipeline";
import { lazy, Suspense } from "react";
const Simulator = lazy(() => import("./sections/Simulator").then((module) => ({ default: module.Simulator })));
import { Results } from "./sections/Results";
import { Features } from "./sections/Features";
import { Architecture } from "./sections/Architecture";
import { QuickStart } from "./sections/QuickStart";
import { Scope } from "./sections/Scope";
import { Faq } from "./sections/Faq";
import { Cta } from "./sections/Cta";
import { Footer } from "./sections/Footer";

export default function App() {
  return (
    <>
      <a className="skip-link" href="#main">Skip to content</a>
      <Nav />
      <main id="main">
        <Hero />
        <Pipeline />
        <Suspense fallback={<section className="sec" id="try"><div className="wrap">Loading the local simulator…</div></section>}><Simulator /></Suspense>
        <Results />
        <Features />
        <Architecture />
        <QuickStart />
        <Scope />
        <Faq />
        <Cta />
      </main>
      <Footer />
    </>
  );
}
