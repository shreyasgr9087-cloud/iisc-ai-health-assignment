import { useEffect, useState } from "react";
import Sidebar, { MODULES } from "./components/Sidebar.jsx";
import RiskPredictor from "./modules/RiskPredictor.jsx";
import HealthAssistant from "./modules/HealthAssistant.jsx";
import { cx } from "./components/ui.jsx";

export default function App() {
  const [active, setActive] = useState("risk");
  const [menuOpen, setMenuOpen] = useState(false);

  const current = MODULES.find((m) => m.id === active);

  useEffect(() => {
    document.title = `${current.label} · Clarity Health`;
  }, [current]);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e) => e.key === "Escape" && setMenuOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  return (
    <div className="flex h-dvh bg-canvas">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-line bg-canvas lg:block">
        <Sidebar active={active} onSelect={setActive} />
      </aside>

      {/* Mobile drawer */}
      <div
        className={cx(
          "fixed inset-0 z-40 lg:hidden",
          menuOpen ? "pointer-events-auto" : "pointer-events-none"
        )}
        aria-hidden={!menuOpen}
      >
        <div
          className={cx(
            "absolute inset-0 bg-black/60 transition-opacity duration-300 ease-calm",
            menuOpen ? "opacity-100" : "opacity-0"
          )}
          onClick={() => setMenuOpen(false)}
        />
        <aside
          className={cx(
            "absolute inset-y-0 left-0 w-64 border-r border-line bg-canvas transition-transform duration-300 ease-calm",
            menuOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <Sidebar active={active} onSelect={setActive} onNavigate={() => setMenuOpen(false)} />
        </aside>
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Mobile top bar */}
        <div className="flex h-16 shrink-0 items-center gap-4 border-b border-line px-4 lg:hidden">
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            aria-label="Open navigation"
            className="flex h-10 w-10 items-center justify-center rounded-xl text-muted transition-colors duration-200 ease-calm hover:bg-surface hover:text-fg"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" aria-hidden="true">
              <path d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
          <span className="font-heading text-body font-semibold">{current.label}</span>
        </div>

        {/* Both modules stay mounted so form values and chat history survive navigation. */}
        <main className="min-h-0 flex-1">
          <div className={cx("h-full overflow-y-auto", active !== "risk" && "hidden")}>
            <RiskPredictor />
          </div>
          <div className={cx("h-full", active !== "assistant" && "hidden")}>
            <HealthAssistant />
          </div>
        </main>
      </div>
    </div>
  );
}
