import { cx } from "./ui.jsx";

const HeartPulseIcon = () => (
  <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M3 12h4l2.5-5 4 10 2.5-5H21" />
  </svg>
);

const ChatIcon = () => (
  <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12Z" />
  </svg>
);

export const MODULES = [
  {
    id: "risk",
    label: "Risk Predictor",
    description: "Heart failure assessment",
    Icon: HeartPulseIcon,
  },
  {
    id: "assistant",
    label: "Health Assistant",
    description: "Answers sourced from WHO",
    Icon: ChatIcon,
  },
];

export default function Sidebar({ active, onSelect, onNavigate }) {
  return (
    <div className="flex h-full flex-col gap-8 p-4">
      <div className="flex items-center gap-3 px-2 pt-2">
        <img src="/favicon.svg" alt="" className="h-8 w-8 rounded-xl" />
        <span className="font-heading text-body font-semibold">Clarity Health</span>
      </div>

      <nav aria-label="Modules" className="flex flex-col gap-1">
        {MODULES.map(({ id, label, description, Icon }) => {
          const isActive = id === active;
          return (
            <button
              key={id}
              type="button"
              aria-current={isActive ? "page" : undefined}
              onClick={() => {
                onSelect(id);
                onNavigate?.();
              }}
              className={cx(
                "flex items-center gap-3 rounded-xl px-3 py-3 text-left transition-colors duration-200 ease-calm",
                isActive ? "bg-raised text-fg" : "text-muted hover:bg-surface hover:text-fg"
              )}
            >
              <span className={cx("transition-colors duration-200", isActive && "text-accent")}>
                <Icon />
              </span>
              <span className="flex flex-col">
                <span className="text-body-sm font-medium">{label}</span>
                <span className="text-caption text-subtle">{description}</span>
              </span>
            </button>
          );
        })}
      </nav>

      <p className="mt-auto px-2 pb-2 text-caption text-subtle">
        For clinical decision support and general information only. Not a substitute for
        professional medical judgement.
      </p>
    </div>
  );
}
