import { useMemo, useRef, useState } from "react";
import { predictRisk } from "../api/client.js";
import {
  Button,
  Card,
  NumberField,
  SegmentedField,
  Skeleton,
  ToggleField,
  cx,
} from "../components/ui.jsx";

/* ------------------------------------------------------------------ */
/* Field schema: one source of truth for the form, validation, payload */
/* ------------------------------------------------------------------ */

const FIELDS = [
  { key: "age", label: "Age", unit: "years", kind: "number", min: 1, max: 120, step: 1 },
  { key: "anaemia", label: "Anaemia", kind: "toggle" },
  { key: "creatinine_phosphokinase", label: "Creatinine Phosphokinase", unit: "mcg/L", kind: "number", min: 1, max: 10000, step: 1 },
  { key: "diabetes", label: "Diabetes", kind: "toggle" },
  { key: "ejection_fraction", label: "Ejection Fraction", unit: "%", kind: "number", min: 1, max: 100, step: 1 },
  { key: "high_blood_pressure", label: "High Blood Pressure", kind: "toggle" },
  { key: "platelets", label: "Platelets", unit: "×10³/µL", kind: "number", min: 25, max: 850, step: 1 },
  { key: "serum_creatinine", label: "Serum Creatinine", unit: "mg/dL", kind: "number", min: 0.1, max: 15, step: 0.1 },
  { key: "serum_sodium", label: "Serum Sodium", unit: "mEq/L", kind: "number", min: 100, max: 160, step: 1 },
  { key: "sex", label: "Sex", kind: "sex" },
  { key: "smoking", label: "Smoking", kind: "toggle" },
  { key: "time", label: "Follow-up Time", unit: "days", kind: "number", min: 1, max: 400, step: 1 },
];

const INITIAL_VALUES = {
  age: "60",
  anaemia: false,
  creatinine_phosphokinase: "250",
  diabetes: false,
  ejection_fraction: "38",
  high_blood_pressure: false,
  platelets: "263",
  serum_creatinine: "1.1",
  serum_sodium: "137",
  sex: "male",
  smoking: false,
  time: "120",
};

const DEFAULT_THRESHOLD = 0.42;

const rangeHint = (f) => `Range ${f.min}–${f.max}`;

function validate(values) {
  const errors = {};
  for (const f of FIELDS) {
    if (f.kind !== "number") continue;
    const raw = values[f.key];
    const n = Number(raw);
    if (raw === "" || Number.isNaN(n)) errors[f.key] = "Enter a value";
    else if (n < f.min || n > f.max) errors[f.key] = `Must be between ${f.min} and ${f.max}`;
  }
  return errors;
}

/** Convert form state to the payload shape the backend expects. */
function toPayload(values, threshold) {
  const features = {};
  for (const f of FIELDS) {
    const v = values[f.key];
    if (f.kind === "number") {
      features[f.key] = f.key === "platelets" ? Number(v) * 1000 : Number(v);
    }
    else if (f.kind === "toggle") features[f.key] = v ? 1 : 0;
    else if (f.kind === "sex") features[f.key] = v === "male" ? 1 : 0;
  }
  return { features, threshold };
}

/* ------------------------------------------------------------------ */
/* Sections                                                            */
/* ------------------------------------------------------------------ */

function ThresholdControl({ value, onChange }) {
  const fill = ((value - 0.01) / (0.99 - 0.01)) * 100;
  return (
    <Card className="p-6">
      <div className="flex flex-col gap-1">
        <h2 className="text-title">Clinical Diagnostic Settings</h2>
        <p className="text-body-sm text-muted">
          A case is flagged high risk when the predicted probability is above the decision
          threshold. Lower values flag more cases; higher values flag fewer.
        </p>
      </div>

      <div className="mt-6 flex flex-col gap-4">
        <div className="flex items-baseline justify-between">
          <label htmlFor="threshold" className="text-body-sm font-medium">
            Decision Threshold
          </label>
          <output htmlFor="threshold" className="font-heading text-title tabular-nums">
            {value.toFixed(2)}
          </output>
        </div>
        <input
          id="threshold"
          type="range"
          className="range"
          min={0.01}
          max={0.99}
          step={0.01}
          value={value}
          style={{ "--fill": `${fill}%` }}
          onChange={(e) => onChange(Number(e.target.value))}
        />
        <div className="flex justify-between text-caption text-subtle tabular-nums">
          <span>0.01</span>
          <span>0.99</span>
        </div>
      </div>
    </Card>
  );
}

function ResultSkeleton() {
  return (
    <Card className="flex flex-col gap-6 p-6" aria-label="Calculating risk" aria-busy="true">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-16 w-48" />
      <Skeleton className="h-2 w-full" />
      <Skeleton className="h-16 w-full" />
    </Card>
  );
}

function ResultCard({ result }) {
  const pct = result.probability * 100;
  const high = result.isHighRisk;
  return (
    <Card className="animate-fade-up p-6" aria-live="polite">
      <p className="text-body-sm text-muted">Calculated Risk Probability</p>
      <p className="mt-2 font-heading text-metric font-semibold tabular-nums">
        {pct.toFixed(1)}%
      </p>

      {/* Probability bar with the threshold marked on it */}
      <div className="mt-6">
        <div className="relative h-2 rounded-full bg-line-strong">
          <div
            className={cx(
              "h-full rounded-full transition-[width] duration-700 ease-calm",
              high ? "bg-risk-high" : "bg-risk-low"
            )}
            style={{ width: `${pct}%` }}
          />
          <div
            className="absolute -top-1 h-4 w-0.5 rounded-full bg-fg"
            style={{ left: `${result.threshold * 100}%` }}
            aria-hidden="true"
          />
        </div>
        <div className="mt-2 flex justify-between text-caption text-subtle tabular-nums">
          <span>0%</span>
          <span>Threshold {(result.threshold * 100).toFixed(0)}%</span>
          <span>100%</span>
        </div>
      </div>

      <div
        role="status"
        className={cx(
          "mt-6 flex items-start gap-4 rounded-xl border p-4",
          high
            ? "border-risk-high/40 bg-risk-high-wash"
            : "border-risk-low/40 bg-risk-low-wash"
        )}
      >
        <span
          className={cx("mt-2 h-2 w-2 shrink-0 rounded-full", high ? "bg-risk-high" : "bg-risk-low")}
          aria-hidden="true"
        />
        <div className="flex flex-col gap-1">
          <p className={cx("text-body-sm font-semibold tracking-wide", high ? "text-risk-high" : "text-risk-low")}>
            {high ? "HIGH RISK" : "LOW RISK"}
          </p>
          <p className="text-body-sm text-muted">
            {high
              ? `Predicted probability is above the ${result.threshold.toFixed(2)} decision threshold. Clinical follow-up is recommended.`
              : `Predicted probability is at or below the ${result.threshold.toFixed(2)} decision threshold.`}
          </p>
        </div>
      </div>
    </Card>
  );
}

/* ------------------------------------------------------------------ */
/* Module                                                              */
/* ------------------------------------------------------------------ */

export default function RiskPredictor() {
  const [values, setValues] = useState(INITIAL_VALUES);
  const [threshold, setThreshold] = useState(DEFAULT_THRESHOLD);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const resultRef = useRef(null);
  const abortRef = useRef(null);

  const setField = (key) => (value) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const isDirty = useMemo(
    () =>
      threshold !== DEFAULT_THRESHOLD ||
      Object.keys(INITIAL_VALUES).some((k) => values[k] !== INITIAL_VALUES[k]),
    [values, threshold]
  );

  const handleReset = () => {
    abortRef.current?.abort();
    setValues(INITIAL_VALUES);
    setThreshold(DEFAULT_THRESHOLD);
    setErrors({});
    setResult(null);
    setStatus("idle");
  };

  const handlePredict = async () => {
    const found = validate(values);
    setErrors(found);
    if (Object.keys(found).length > 0) {
      document.getElementById(`field-${Object.keys(found)[0]}`)?.focus();
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setStatus("loading");
    setErrorMessage("");
    requestAnimationFrame(() =>
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" })
    );

    try {
      const data = await predictRisk(toPayload(values, threshold), controller.signal);
      setResult(data);
      setStatus("success");
    } catch (err) {
      if (err.name === "AbortError") return;
      setErrorMessage(err.message || "Something went wrong.");
      setStatus("error");
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-8 sm:px-8 lg:py-12">
      <header className="flex flex-col gap-2">
        <h1 className="text-display">Heart Failure Risk Predictor</h1>
        <p className="max-w-2xl text-body text-muted">
          Enter the patient&rsquo;s clinical measurements to estimate the probability of a heart
          failure event, then compare it against your chosen decision threshold.
        </p>
      </header>

      <section aria-labelledby="inputs-heading" className="flex flex-col gap-4">
        <h2 id="inputs-heading" className="text-title">
          Patient Features
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FIELDS.map((f) => {
            if (f.kind === "number")
              return (
                <NumberField
                  key={f.key}
                  id={`field-${f.key}`}
                  label={f.label}
                  unit={f.unit}
                  min={f.min}
                  max={f.max}
                  step={f.step}
                  hint={rangeHint(f)}
                  error={errors[f.key]}
                  value={values[f.key]}
                  onChange={setField(f.key)}
                />
              );
            if (f.kind === "sex")
              return (
                <SegmentedField
                  key={f.key}
                  label={f.label}
                  hint="Biological sex"
                  value={values[f.key]}
                  onChange={setField(f.key)}
                  options={[
                    { value: "male", label: "Male" },
                    { value: "female", label: "Female" },
                  ]}
                />
              );
            return (
              <ToggleField
                key={f.key}
                label={f.label}
                hint="Present at assessment"
                checked={values[f.key]}
                onChange={setField(f.key)}
              />
            );
          })}
        </div>
      </section>

      <ThresholdControl value={threshold} onChange={setThreshold} />

      <div className="flex flex-col-reverse gap-4 sm:flex-row sm:items-center sm:justify-end">
        <Button variant="secondary" onClick={handleReset} disabled={!isDirty && status === "idle"}>
          Reset
        </Button>
        <Button onClick={handlePredict} loading={status === "loading"} className="sm:min-w-[192px]">
          {status === "loading" ? "Calculating" : "Predict Risk"}
        </Button>
      </div>

      <div ref={resultRef} className="scroll-mt-8">
        {status === "loading" && <ResultSkeleton />}
        {status === "success" && result && <ResultCard result={result} />}
        {status === "error" && (
          <div
            role="alert"
            className="animate-fade-in rounded-xl border border-risk-high/40 bg-risk-high-wash p-4 text-body-sm text-risk-high"
          >
            {errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}
