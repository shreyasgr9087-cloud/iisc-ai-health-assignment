/**
 * Design tokens
 * - Spacing: Tailwind's 4px scale, used in 8px steps for layout (2, 4, 6, 8, 12, 16)
 *   and 4px steps only inside compact controls.
 * - Radius: a single radius (rounded-xl, 12px) for every surface and control.
 * - Type: one heading family, one body family, five sizes with fixed line heights.
 * - Colour: neutral ink scale + one teal accent + two semantic risk colours.
 */
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    fontFamily: {
      heading: ['"Inter Tight"', "ui-sans-serif", "system-ui", "sans-serif"],
      sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
    },
    fontSize: {
      caption: ["12px", { lineHeight: "16px", letterSpacing: "0.01em" }],
      "body-sm": ["14px", { lineHeight: "20px" }],
      body: ["16px", { lineHeight: "24px" }],
      title: ["20px", { lineHeight: "28px", letterSpacing: "-0.01em" }],
      display: ["32px", { lineHeight: "40px", letterSpacing: "-0.02em" }],
      metric: ["56px", { lineHeight: "64px", letterSpacing: "-0.03em" }],
    },
    extend: {
      colors: {
        canvas: "#0B0C0E",
        surface: "#111316",
        raised: "#171A1E",
        line: "#242830",
        "line-strong": "#323843",
        fg: "#ECEEF0",
        muted: "#9AA1AB",
        subtle: "#6B727C",
        accent: {
          DEFAULT: "#5EC4B6",
          strong: "#7AD4C8",
          wash: "rgba(94, 196, 182, 0.12)",
        },
        risk: {
          high: "#F0626A",
          "high-wash": "rgba(240, 98, 106, 0.12)",
          low: "#4CC38A",
          "low-wash": "rgba(76, 195, 138, 0.12)",
        },
      },
      borderRadius: {
        xl: "12px",
      },
      boxShadow: {
        // One elevation level, used only for floating elements.
        float: "0 8px 32px rgba(0, 0, 0, 0.4)",
      },
      transitionTimingFunction: {
        calm: "cubic-bezier(0.2, 0, 0, 1)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%": { opacity: "0.4" },
          "50%": { opacity: "0.9" },
          "100%": { opacity: "0.4" },
        },
      },
      animation: {
        "fade-up": "fade-up 320ms cubic-bezier(0.2, 0, 0, 1) both",
        "fade-in": "fade-in 240ms cubic-bezier(0.2, 0, 0, 1) both",
        shimmer: "shimmer 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
