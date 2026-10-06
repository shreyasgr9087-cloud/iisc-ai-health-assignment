import { useCallback, useEffect, useId, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { askAssistant } from "../api/client.js";
import { Skeleton, Spinner, cx } from "../components/ui.jsx";

const SUGGESTIONS = [
  "How much physical activity do adults need each week?",
  "What are the WHO recommendations on salt intake?",
  "What counts as high blood pressure in adults?",
];

let nextId = 0;
const makeId = () => `msg-${++nextId}`;

/* ------------------------------------------------------------------ */
/* Retrieved context accordion                                         */
/* ------------------------------------------------------------------ */

function RetrievedContext({ sources }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  if (!sources?.length) return null;

  return (
    <div className="mt-4 border-t border-line pt-2">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
        className="-mx-2 flex items-center gap-2 rounded-xl px-2 py-2 text-caption font-medium text-muted transition-colors duration-200 ease-calm hover:text-fg"
      >
        <svg
          viewBox="0 0 24 24"
          className={cx("h-4 w-4 transition-transform duration-200 ease-calm", open && "rotate-90")}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="m9 6 6 6-6 6" />
        </svg>
        View Retrieved Context
        <span className="rounded-full bg-raised px-2 text-subtle tabular-nums">{sources.length}</span>
      </button>

      {/* grid-rows trick animates height without measuring */}
      <div
        id={panelId}
        role="region"
        className={cx(
          "grid transition-[grid-template-rows,opacity] duration-300 ease-calm",
          open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        )}
      >
        <div className="overflow-hidden">
          <ul className="flex flex-col gap-2 pt-2">
            {sources.map((s, i) => (
              <li key={s.id} className="rounded-xl border border-line bg-canvas p-4">
                <div className="flex items-start justify-between gap-4">
                  <p className="text-caption font-medium text-fg">
                    [{i + 1}] {s.document}
                  </p>
                  {s.page != null && (
                    <span className="shrink-0 text-caption text-subtle tabular-nums">p. {s.page}</span>
                  )}
                </div>
                <p className="mt-2 border-l-2 border-accent/50 pl-4 text-body-sm text-muted">
                  {s.excerpt}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Messages                                                            */
/* ------------------------------------------------------------------ */

function Message({ message }) {
  if (message.role === "user") {
    return (
      <div className="flex animate-fade-up justify-end">
        <p className="max-w-[85%] whitespace-pre-wrap rounded-xl bg-raised px-4 py-3 text-body-sm">
          {message.content}
        </p>
      </div>
    );
  }

  return (
    <div className="flex animate-fade-up justify-start">
      <div
        className={cx(
          "w-full max-w-[85%] rounded-xl border px-4 py-4",
          message.isError ? "border-risk-high/40 bg-risk-high-wash" : "border-line bg-surface"
        )}
      >
        <div className={cx("whitespace-pre-wrap text-body-sm overflow-x-auto", message.isError && "text-risk-high")}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
        <RetrievedContext sources={message.sources} />
      </div>
    </div>
  );
}

function PendingMessage() {
  return (
    <div className="flex animate-fade-in justify-start" role="status" aria-label="Assistant is responding">
      <div className="w-full max-w-[85%] rounded-xl border border-line bg-surface p-4">
        <div className="flex flex-col gap-2">
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-3/5" />
        </div>
      </div>
    </div>
  );
}

function EmptyState({ onPick }) {
  return (
    <div className="mx-auto flex max-w-xl animate-fade-up flex-col gap-8 pt-8">
      <div className="flex flex-col gap-2">
        <h2 className="text-title">Ask a health question</h2>
        <p className="text-body-sm text-muted">
          Answers are drawn only from official WHO documents. Every reply lists the passages it
          relied on, so you can check the source yourself.
        </p>
      </div>
      <ul className="flex flex-col gap-2">
        {SUGGESTIONS.map((s) => (
          <li key={s}>
            <button
              type="button"
              onClick={() => onPick(s)}
              className="w-full rounded-xl border border-line bg-surface px-4 py-3 text-left text-body-sm text-muted transition-colors duration-200 ease-calm hover:border-line-strong hover:text-fg"
            >
              {s}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Module                                                              */
/* ------------------------------------------------------------------ */

export default function HealthAssistant() {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);
  const textareaRef = useRef(null);
  const abortRef = useRef(null);

  // Keep the newest message in view.
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  // Auto-grow the textarea up to 6 lines (24px each).
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 144)}px`;
  }, [draft]);

  const send = useCallback(
    async (text) => {
      const question = text.trim();
      if (!question || loading) return;

      const history = messages
        .filter((m) => !m.isError)
        .map(({ role, content }) => ({ role, content }));

      setMessages((prev) => [...prev, { id: makeId(), role: "user", content: question }]);
      setDraft("");
      setLoading(true);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const { answer, sources } = await askAssistant({ question, history }, controller.signal);
        setMessages((prev) => [...prev, { id: makeId(), role: "assistant", content: answer, sources }]);
      } catch (err) {
        if (err.name === "AbortError") return;
        setMessages((prev) => [
          ...prev,
          {
            id: makeId(),
            role: "assistant",
            isError: true,
            content: err.message || "The assistant could not be reached. Please try again.",
          },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [messages, loading]
  );

  useEffect(() => () => abortRef.current?.abort(), []);

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      send(draft);
    }
  };

  const canSend = draft.trim().length > 0 && !loading;

  return (
    <div className="relative flex h-full flex-col">
      <div ref={scrollRef} className="scroll-quiet flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 pb-48 pt-8 sm:px-8 lg:pt-12">
          <header className="flex flex-col gap-2">
            <h1 className="text-display">Trusted Health Assistant</h1>
            <p className="text-body text-muted">Grounded strictly in official WHO documents.</p>
          </header>

          <div role="log" aria-live="polite" className="flex flex-col gap-6">
            {messages.length === 0 && !loading && <EmptyState onPick={send} />}
            {messages.map((m) => (
              <Message key={m.id} message={m} />
            ))}
            {loading && <PendingMessage />}
          </div>
        </div>
      </div>

      {/* Floating composer */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-canvas via-canvas to-transparent px-4 pb-6 pt-12 sm:px-8">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(draft);
          }}
          className="pointer-events-auto mx-auto flex w-full max-w-3xl items-end gap-2 rounded-xl border border-line-strong bg-surface p-2 shadow-float transition-colors duration-200 ease-calm focus-within:border-accent/60"
        >
          <label htmlFor="chat-input" className="sr-only">
            Ask a health question
          </label>
          <textarea
            id="chat-input"
            ref={textareaRef}
            rows={1}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask about a WHO guideline"
            className="scroll-quiet max-h-36 min-h-[40px] flex-1 resize-none bg-transparent px-2 py-2 text-body-sm placeholder:text-subtle"
            style={{ outline: "none" }}
          />
          <button
            type="submit"
            disabled={!canSend}
            aria-label="Send message"
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-canvas transition-colors duration-200 ease-calm hover:bg-accent-strong disabled:bg-raised disabled:text-subtle"
          >
            {loading ? (
              <Spinner />
            ) : (
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M12 19V5M5 12l7-7 7 7" />
              </svg>
            )}
          </button>
        </form>
        <p className="mx-auto mt-2 max-w-3xl text-center text-caption text-subtle">
          Enter to send &middot; Shift+Enter for a new line
        </p>
      </div>
    </div>
  );
}
