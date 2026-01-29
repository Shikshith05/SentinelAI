"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type Message = {
  sender: string;
  text: string;
  timestamp: string;
  severity: "low" | "medium" | "high";
};

type Analysis = {
  conflict_score: number;
  severity: "low" | "medium" | "high";
  flags: string[];
  suggestion: string;
  word_count: number;
  triggered_rules: string[];
  model: {
    sentiment: string;
    sentiment_score: number;
    toxicity: number;
  };
  model_error?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const defaultUsers = ["Alice", "Bob", "Manager"];

const demoMessages: Record<string, Message[]> = {
  Alice: [
    { sender: "Alice", text: "This project is going nowhere!", timestamp: "10:23", severity: "high" },
    { sender: "Bob", text: "I disagree. We're making progress.", timestamp: "10:24", severity: "medium" },
    { sender: "Alice", text: "Your idea is completely useless.", timestamp: "10:25", severity: "high" },
    { sender: "Manager", text: "Let's discuss this constructively.", timestamp: "10:26", severity: "medium" }
  ],
  Bob: [
    { sender: "Bob", text: "You never listen to my ideas!", timestamp: "14:05", severity: "high" },
    { sender: "Manager", text: "Let's take a step back and discuss.", timestamp: "14:06", severity: "low" },
    { sender: "Bob", text: "I appreciate your feedback on this.", timestamp: "14:07", severity: "low" },
    { sender: "Alice", text: "Good point, let's work together.", timestamp: "14:08", severity: "low" }
  ],
  Manager: [
    { sender: "Manager", text: "Both of you need to communicate better.", timestamp: "09:15", severity: "medium" },
    { sender: "Alice", text: "Understood. I'll make more effort.", timestamp: "09:16", severity: "low" },
    { sender: "Bob", text: "Thanks for the guidance.", timestamp: "09:17", severity: "low" },
    { sender: "Manager", text: "Great! Let's continue working as a team.", timestamp: "09:18", severity: "low" }
  ]
};

const userDescriptions: Record<string, string> = {
  Alice: "Assertive, sometimes aggressive communicator",
  Bob: "Analytical, can be dismissive of others",
  Manager: "Mediator focused on resolution"
};

const sentimentLabelMap: Record<string, string> = {
  LABEL_0: "Neutral",
  LABEL_1: "Positive",
  LABEL_2: "Negative",
  NEUTRAL: "Neutral",
  POSITIVE: "Positive",
  NEGATIVE: "Negative"
};

export default function Home() {
  const [users, setUsers] = useState<string[]>([]);
  const [currentUser, setCurrentUser] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const analysisCache = useRef<Map<string, Analysis>>(new Map());

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/users`);
        const data = await res.json();
        setUsers(data.users || []);
      } catch (err) {
        setUsers(defaultUsers);
        setError("Using demo data. Connect the API for live insights.");
      }
    };

    loadUsers();
  }, []);

  useEffect(() => {
    const loadMessages = async () => {
      setLoading(true);
      setError("");

      try {
        const res = await fetch(`${API_BASE}/api/messages`);
        if (!res.ok) {
          throw new Error("Failed to load messages");
        }
        const data = await res.json();
        const items: Message[] = data.messages || [];
        setMessages(items);

        if (items.length > 0) {
          const last = items[items.length - 1];
          const cacheKey = last.text.trim();
          const cached = analysisCache.current.get(cacheKey);
          if (cached) {
            setAnalysis(cached);
          } else {
            const analyzeRes = await fetch(`${API_BASE}/api/analyze`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ text: last.text })
            });
            if (analyzeRes.ok) {
              const analyzeData = await analyzeRes.json();
              analysisCache.current.set(cacheKey, analyzeData);
              setAnalysis(analyzeData);
            }
          }
        } else {
          setAnalysis(null);
        }
      } catch (err) {
        const allDemoMessages = [
          ...demoMessages.Manager,
          ...demoMessages.Alice,
          ...demoMessages.Bob
        ];
        setMessages(allDemoMessages);
        setAnalysis(null);
        setError("Showing demo conversation. Connect the API for real-time analysis.");
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const counts = useMemo(() => {
    const high = messages.filter((m) => m.severity === "high").length;
    const medium = messages.filter((m) => m.severity === "medium").length;
    const low = messages.filter((m) => m.severity === "low").length;
    return { high, medium, low, total: messages.length };
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || !currentUser) {
      return;
    }

    setLoading(true);
    setError("");

    const cacheKey = input.trim();
    const cached = analysisCache.current.get(cacheKey);

    try {
      const res = await fetch(`${API_BASE}/api/send-message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user: currentUser, text: input })
      });

      if (!res.ok) {
        throw new Error("Failed to send message");
      }

      const data = await res.json();
      
      // Add new message(s) to the list
      const newMessages = [data.message];
      if (data.intervention) {
        newMessages.push(data.intervention);
      }
      setMessages((prev) => [...prev, ...newMessages]);
      
      const resolvedAnalysis = cached ?? data.analysis;
      analysisCache.current.set(cacheKey, resolvedAnalysis);
      setAnalysis(resolvedAnalysis);
      setInput("");
    } catch (err) {
      setError("Unable to send message.");
    } finally {
      setLoading(false);
    }
  };

  const getSentimentLabel = (label?: string) => {
    if (!label) {
      return "Neutral";
    }
    return sentimentLabelMap[label.toUpperCase()] ?? "Neutral";
  };

  const severityStyles = (severity: Message["severity"]) => {
    if (severity === "high") {
      return "border-red-400/60 bg-slate-900/70 text-red-100";
    }
    if (severity === "medium") {
      return "border-slate-500/60 bg-slate-900/70 text-slate-100";
    }
    return "border-emerald-400/60 bg-slate-900/70 text-emerald-100";
  };

  const alignmentStyles = (sender: string) => {
    if (sender === "Bob") {
      return "justify-end";
    }
    if (sender === "Manager") {
      return "justify-center";
    }
    return "justify-start";
  };

  const avatarStyles = (sender: string) => {
    if (sender === "Bob") {
      return "bg-sky-500/20 text-sky-200";
    }
    if (sender === "Manager") {
      return "bg-purple-500/20 text-purple-200";
    }
    return "bg-emerald-500/20 text-emerald-200";
  };

  const riskInfo = () => {
    if (!analysis) {
      return {
        label: "Select a user to start analyzing",
        badge: "bg-slate-800/80 text-slate-200"
      };
    }

    if (analysis.conflict_score < 40) {
      return {
        label: "LOW RISK: Conversation is constructive and positive",
        badge: "bg-emerald-900/70 text-emerald-100"
      };
    }

    if (analysis.conflict_score < 70) {
      return {
        label: "MEDIUM RISK: Some tension present, needs monitoring",
        badge: "bg-amber-900/70 text-amber-100"
      };
    }

    return {
      label: "HIGH RISK: Significant conflict escalation detected",
      badge: "bg-red-900/70 text-red-100"
    };
  };

  const risk = riskInfo();

  const scoreValue = analysis?.conflict_score ?? 0;
  const scoreLabel = scoreValue < 40 ? "Safe" : scoreValue < 70 ? "Warning" : "Critical";
  const scoreColor =
    scoreValue < 40 ? "#2dd4bf" : scoreValue < 70 ? "#f59e0b" : "#ef4444";
  const scoreTrack = `conic-gradient(${scoreColor} ${scoreValue * 3.6}deg, rgba(148, 163, 184, 0.15) 0deg)`;

  const indicatorTags = analysis?.flags?.length
    ? analysis.flags
    : ["Harsh Language", "Repeated Negation", "Blame Language", "Rapid Replies"];

  const metrics = [
    { label: "Message Intensity", value: scoreValue ? `${Math.round(scoreValue / 7)} / 10` : "—" },
    { label: "Emotional Tone", value: getSentimentLabel(analysis?.model?.sentiment) },
    { label: "Risk Signals", value: analysis?.flags?.length ?? 0 },
    { label: "Response Tempo", value: analysis ? "High" : "—" }
  ];

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header className="flex flex-col items-center gap-4 text-center">
        <div className="w-full">
          <h2 className="text-2xl uppercase tracking-[0.25em] font-bold text-slate-300">SENTINELAI</h2>
          <h1 className="mt-2 text-5xl font-semibold text-white">Sentinel</h1>
          <p className="mt-2 text-lg text-brand-400">
            Real-time Conflict Detection & De-escalation Assistant
          </p>
          <p className="mt-2 text-sm text-slate-400">
            Monitor tension signals and receive AI-guided de-escalation insights.
          </p>
        </div>
        <div className="flex items-center justify-center gap-2 md:justify-end">
          <span className="rounded-full border border-emerald-400/40 bg-emerald-400/10 px-4 py-1 text-xs font-semibold text-emerald-200">
            System Active
          </span>
          <span className="rounded-full border border-purple-400/30 bg-purple-400/10 px-4 py-1 text-xs text-purple-200">
            Monitoring
          </span>
        </div>
      </header>

      <section className="mt-10 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="glass-card rounded-3xl p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">Chat Section</h2>
              <p className="text-sm text-slate-400">
                Live conversation feed with real-time conflict indicators
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">User</span>
              <select
                value={currentUser}
                onChange={(event) => setCurrentUser(event.target.value)}
                className="glass-border rounded-full bg-slate-950/70 px-4 py-2 text-sm text-slate-200"
              >
                <option value="">Select user</option>
                {users.length ? (
                  users.map((user) => (
                    <option key={user} value={user}>
                      {user}
                    </option>
                  ))
                ) : (
                  defaultUsers.map((user) => (
                    <option key={user} value={user}>
                      {user}
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>

          {currentUser && (
            <p className="mt-3 text-sm text-slate-400">
              {currentUser}: {userDescriptions[currentUser] || ""}
            </p>
          )}

          <div className="scrollbar-slim mt-6 max-h-[420px] space-y-4 overflow-y-auto pr-2">
            {messages.length === 0 && (
              <div className="rounded-2xl border border-dashed border-slate-700/60 p-8 text-center text-sm text-slate-400">
                Start a conversation to see real-time conflict insights.
              </div>
            )}
            {messages.map((message, index) => (
              <div key={`${message.timestamp}-${index}`} className={`flex ${alignmentStyles(message.sender)}`}>
                <div className={`fade-in w-full max-w-[78%] rounded-2xl border ${severityStyles(message.severity)} p-4`}>
                  <div className="flex items-center gap-3">
                    <div
                      className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${avatarStyles(message.sender)}`}
                    >
                      {message.sender.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-100">{message.sender}</p>
                      <p className="text-xs text-slate-400">{message.timestamp}</p>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-200">{message.text}</p>
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div className="mt-6 grid grid-cols-3 gap-3 text-center text-sm">
            <div className="rounded-2xl border border-slate-800/70 bg-slate-950/70 p-3">
              <p className="text-xs text-slate-400">Messages</p>
              <p className="text-lg font-semibold text-white">{counts.total}</p>
            </div>
            <div className="rounded-2xl border border-slate-800/70 bg-slate-950/70 p-3">
              <p className="text-xs text-slate-400">Tense</p>
              <p className="text-lg font-semibold text-red-200">{counts.high}</p>
            </div>
            <div className="rounded-2xl border border-slate-800/70 bg-slate-950/70 p-3">
              <p className="text-xs text-slate-400">Neutral</p>
              <p className="text-lg font-semibold text-amber-200">{counts.medium}</p>
            </div>
          </div>

          <div className="mt-6 border-t border-slate-800/60 pt-5">
            <p className="text-sm font-medium text-slate-200">Send a message</p>
            <div className="mt-3 flex flex-col gap-3 md:flex-row">
              <select
                value={currentUser}
                onChange={(event) => setCurrentUser(event.target.value)}
                className="glass-border rounded-full bg-slate-950/70 px-4 py-2 text-sm text-slate-200"
              >
                <option value="">Select user</option>
                {defaultUsers.map((user) => (
                  <option key={user} value={user}>
                    {user}
                  </option>
                ))}
              </select>
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Type your message here..."
                className="flex-1 rounded-full border border-slate-700/60 bg-slate-950/70 px-4 py-2 text-sm text-slate-200"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !currentUser}
                className="rounded-full bg-brand-500 px-6 py-2 text-sm font-semibold text-white transition hover:bg-brand-400 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        <div className="glass-card rounded-3xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">Conflict Analysis Panel</h2>
              <p className="text-sm text-slate-400">AI-powered insights into conversation dynamics</p>
            </div>
            <span className="rounded-full border border-purple-400/30 bg-purple-400/10 px-4 py-1 text-xs text-purple-200">
              AI Assistant
            </span>
          </div>

          <div className="mt-6 rounded-2xl border border-slate-800/60 bg-slate-950/40 p-5">
            <div className="flex flex-wrap items-center justify-between gap-6">
              <div>
                <p className="text-sm font-medium text-slate-200">Conflict Score</p>
                <p className="text-xs text-slate-400">Safe / Warning / Critical</p>
              </div>
              <div className="relative h-28 w-28">
                <div
                  className="flex h-full w-full items-center justify-center rounded-full"
                  style={{ background: scoreTrack }}
                >
                  <div className="flex h-20 w-20 flex-col items-center justify-center rounded-full bg-slate-950">
                    <span className="text-xl font-semibold text-white">{scoreValue}%</span>
                    <span className="text-xs text-slate-400">{scoreLabel}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className={`mt-4 rounded-lg px-3 py-2 text-xs font-semibold ${risk.badge}`}>
              {risk.label}
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-slate-200">Detected Conflict Indicators</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              {indicatorTags.map((flag, index) => (
                <span
                  key={`${flag}-${index}`}
                  className="rounded-full border border-slate-700/60 bg-slate-900/70 px-3 py-1 text-xs text-slate-200"
                >
                  ⚡ {flag}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-purple-400/30 bg-purple-500/10 p-5 soft-glow">
            <div className="flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-purple-500/20 text-purple-200">
                🤖
              </span>
              <div>
                <h3 className="text-sm font-semibold text-purple-200">AI-Powered Suggestion</h3>
                <p className="text-xs text-purple-100/70">Mediator guidance for de-escalation</p>
              </div>
            </div>
            <p className="mt-3 text-sm text-purple-100">
              {analysis?.suggestion ||
                "This conversation shows rising tension. Consider rephrasing to focus on the issue, not the person."}
            </p>
            <button className="mt-4 rounded-full border border-purple-400/40 px-4 py-2 text-xs font-semibold text-purple-200 transition hover:bg-purple-500/20">
              Rewrite message neutrally
            </button>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            {metrics.map((metric) => (
              <div key={metric.label} className="rounded-2xl border border-slate-800/70 bg-slate-950/70 p-4">
                <p className="text-xs text-slate-400">{metric.label}</p>
                <p className="mt-2 text-lg font-semibold text-white">{metric.value}</p>
              </div>
            ))}
          </div>

          {analysis?.model_error && (
            <div className="mt-4 rounded-lg border border-amber-500/50 bg-amber-500/10 px-4 py-3 text-xs text-amber-200">
              Model fallback used. Check model dependencies or download status.
            </div>
          )}

          {error && (
            <div className="mt-4 rounded-lg border border-slate-700/60 bg-slate-900/60 px-4 py-3 text-xs text-slate-300">
              {error}
            </div>
          )}
        </div>
      </section>

      <footer className="mt-10 text-center text-xs text-slate-500">
        Demo UI • SentinalAI • Minimal enterprise AI aesthetic
      </footer>
    </main>
  );
}
