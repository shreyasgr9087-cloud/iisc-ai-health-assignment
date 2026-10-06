import { useId } from "react";

/** Join class names, skipping falsy values. */
export const cx = (...parts) => parts.filter(Boolean).join(" ");

/* ------------------------------------------------------------------ */
/* Shared surface tokens: one radius (xl), one border, one padding.    */
/* ------------------------------------------------------------------ */

export function Card({ as: Tag = "section", className, children, ...rest }) {
  return (
    <Tag
      className={cx("rounded-xl border border-line bg-surface", className)}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export function Spinner({ className }) {
  return (
    <svg
      className={cx("h-4 w-4 animate-spin", className)}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

const buttonVariants = {
  primary:
    "bg-accent text-canvas hover:bg-accent-strong disabled:bg-accent/40 disabled:text-canvas/70",
  secondary:
    "border border-line-strong bg-transparent text-fg hover:bg-raised disabled:text-subtle",
};

export function Button({
  variant = "primary",
  loading = false,
  disabled,
  className,
  children,
  ...rest
}) {
  return (
    <button
      type="button"
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={cx(
        "inline-flex h-12 items-center justify-center gap-2 rounded-xl px-6 text-body-sm font-medium",
        "transition-colors duration-200 ease-calm disabled:cursor-not-allowed",
        buttonVariants[variant],
        className
      )}
      {...rest}
    >
      {loading && <Spinner />}
      {children}
    </button>
  );
}

/* ------------------------------------------------------------------ */
/* Form controls                                                       */
/* ------------------------------------------------------------------ */

/** Labelled cell used by every field so the grid stays uniform. */
export function FieldShell({ label, hint, error, htmlFor, children }) {
  return (
    <div
      className={cx(
        "flex min-h-[104px] flex-col justify-between gap-2 rounded-xl border bg-surface p-4",
        "transition-colors duration-200 ease-calm",
        error ? "border-risk-high/60" : "border-line focus-within:border-line-strong"
      )}
    >
      <label htmlFor={htmlFor} className="text-body-sm font-medium text-fg">
        {label}
      </label>
      {children}
      <p
        className={cx("text-caption", error ? "text-risk-high" : "text-subtle")}
        role={error ? "alert" : undefined}
      >
        {error || hint}
      </p>
    </div>
  );
}

export function NumberField({ id: idProp, label, unit, hint, error, value, onChange, min, max, step = 1 }) {
  const generated = useId();
  const id = idProp ?? generated;
  return (
    <FieldShell label={label} hint={hint} error={error} htmlFor={id}>
      <div className="flex items-baseline gap-2">
        <input
          id={id}
          type="number"
          inputMode="decimal"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(e) => onChange(e.target.value)}
          aria-invalid={Boolean(error)}
          className="w-full min-w-0 bg-transparent text-title font-heading font-medium text-fg tabular-nums placeholder:text-subtle focus:outline-none"
          style={{ outline: "none" }}
        />
        <span className="shrink-0 text-caption text-muted">{unit}</span>
      </div>
    </FieldShell>
  );
}

export function ToggleField({ label, hint, checked, onChange, offLabel = "No", onLabel = "Yes" }) {
  const id = useId();
  return (
    <FieldShell label={label} hint={hint} htmlFor={id}>
      <div className="flex items-center justify-between gap-4">
        <span className="text-body-sm text-muted" aria-hidden="true">
          {checked ? onLabel : offLabel}
        </span>
        <button
          id={id}
          type="button"
          role="switch"
          aria-checked={checked}
          onClick={() => onChange(!checked)}
          className={cx(
            "relative h-6 w-10 shrink-0 rounded-full transition-colors duration-200 ease-calm",
            checked ? "bg-accent" : "bg-line-strong"
          )}
        >
          <span
            className={cx(
              "absolute left-1 top-1 h-4 w-4 rounded-full bg-fg transition-transform duration-200 ease-calm",
              checked && "translate-x-4 bg-canvas"
            )}
          />
        </button>
      </div>
    </FieldShell>
  );
}

/** Two-option segmented control, used for Sex. */
export function SegmentedField({ label, hint, value, onChange, options }) {
  const id = useId();
  return (
    <FieldShell label={label} hint={hint} htmlFor={id}>
      <div
        id={id}
        role="radiogroup"
        aria-label={label}
        className="grid grid-cols-2 gap-1 rounded-xl border border-line bg-canvas p-1"
      >
        {options.map((opt) => {
          const active = opt.value === value;
          return (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => onChange(opt.value)}
              className={cx(
                "h-8 rounded-lg text-body-sm font-medium transition-colors duration-200 ease-calm",
                active ? "bg-raised text-fg" : "text-muted hover:text-fg"
              )}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </FieldShell>
  );
}

export function Skeleton({ className }) {
  return <div className={cx("animate-shimmer rounded-xl bg-raised", className)} aria-hidden="true" />;
}
