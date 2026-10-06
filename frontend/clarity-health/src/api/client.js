/**
 * API layer. The two exported functions are the only place the UI talks to a backend.
 *
 * To go live:
 *   1. Set VITE_API_BASE_URL (e.g. http://localhost:8000) and VITE_USE_MOCK=false in .env
 *   2. Make sure the response shapes below match what your Python service returns
 *      (or adapt them inside the `fetch` branches, so components never change).
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? "true") !== "false";

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function post(path, body, signal) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    throw new Error(`Request failed (${res.status}). Please try again.`);
  }
  return res.json();
}

/* ------------------------------------------------------------------ */
/* Module 1: Heart failure risk                                        */
/* ------------------------------------------------------------------ */

/**
 * @param {{
 *   features: {
 *     age: number, anaemia: 0|1, creatinine_phosphokinase: number, diabetes: 0|1,
 *     ejection_fraction: number, high_blood_pressure: 0|1, platelets: number,
 *     serum_creatinine: number, serum_sodium: number, sex: 0|1, smoking: 0|1, time: number
 *   },
 *   threshold: number
 * }} payload   sex: 1 = male, 0 = female
 * @returns {Promise<{ probability: number, threshold: number, isHighRisk: boolean }>}
 *          probability is a fraction between 0 and 1.
 */
export async function predictRisk(payload, signal) {
  if (!USE_MOCK) {
    // Expected backend response: { probability: 0.824 }
    const data = await post("/predict", payload, signal);
    return {
      probability: data.probability,
      threshold: payload.threshold,
      isHighRisk: data.probability > payload.threshold,
    };
  }

  await wait(1100);
  const f = payload.features;
  // Deterministic stand-in so the UI responds to inputs. Not a clinical model.
  const z =
    -4.2 +
    0.045 * f.age +
    -0.07 * (f.ejection_fraction - 38) +
    0.55 * f.serum_creatinine +
    -0.06 * (f.serum_sodium - 137) +
    0.35 * f.anaemia +
    0.25 * f.high_blood_pressure +
    0.15 * f.diabetes +
    -0.008 * (f.time - 120);
  const probability = Math.min(0.99, Math.max(0.01, 1 / (1 + Math.exp(-z))));
  return {
    probability,
    threshold: payload.threshold,
    isHighRisk: probability > payload.threshold,
  };
}

/* ------------------------------------------------------------------ */
/* Module 2: WHO-grounded assistant                                    */
/* ------------------------------------------------------------------ */

/**
 * @param {{ question: string, history: Array<{ role: "user"|"assistant", content: string }> }} payload
 * @returns {Promise<{
 *   answer: string,
 *   sources: Array<{ id: string, document: string, page: number|null, excerpt: string }>
 * }>}
 */
export async function askAssistant(payload, signal) {
  if (!USE_MOCK) {
    // Expected backend response: { answer: string, sources: [{ id, document, page, excerpt }] }
    return post("/chat", payload, signal);
  }

  await wait(1400);
  return {
    answer:
      "According to the WHO guidance retrieved for this question, adults should aim for at least 150 minutes of moderate-intensity aerobic activity per week, or 75 minutes of vigorous-intensity activity, plus muscle-strengthening on two or more days. Any amount of movement is better than none.",
    sources: [
      {
        id: "chunk-0412",
        document: "WHO Guidelines on Physical Activity and Sedentary Behaviour (2020)",
        page: 24,
        excerpt:
          "For substantial health benefits, adults should do at least 150–300 minutes of moderate-intensity aerobic physical activity; or at least 75–150 minutes of vigorous-intensity aerobic physical activity throughout the week.",
      },
      {
        id: "chunk-0418",
        document: "WHO Guidelines on Physical Activity and Sedentary Behaviour (2020)",
        page: 25,
        excerpt:
          "Adults should also do muscle-strengthening activities at moderate or greater intensity that involve all major muscle groups on 2 or more days a week.",
      },
    ],
  };
}
