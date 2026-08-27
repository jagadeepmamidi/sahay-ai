"use client";

import { Fragment, useEffect, useRef, useState } from "react";
import { ArrowUp, CircleNotch } from "@phosphor-icons/react";
import { ChatMessage, ChatResponse, SchemeCard } from "@/types";
import { sendMessage as sendChatMessage } from "@/lib/api";
import { VoiceInputButton, synthesizeSpeech } from "./VoiceInput";
import { LanguageSelector } from "./LanguageSelector";

interface Message extends ChatMessage {
  schemes?: SchemeCard[];
  suggestedQuestions?: string[];
}

function dedupeSchemes(schemes: SchemeCard[]) {
  const seen = new Set<string>();
  return schemes.filter((scheme) => {
    const key = scheme.id || scheme.name;
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

const LINK_PATTERN =
  /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|(https?:\/\/[^\s]+)/gi;

function renderMessageContent(content: string) {
  const lines = content.split("\n");
  return lines.map((line, lineIndex) => {
    const parts = [];
    let lastIndex = 0;
    for (const match of line.matchAll(LINK_PATTERN)) {
      const matchIndex = match.index ?? 0;
      const label = match[1];
      const url = match[2] || match[3];
      if (matchIndex > lastIndex) parts.push(line.slice(lastIndex, matchIndex));
      if (url) {
        parts.push(
          <a
            key={`${lineIndex}-${matchIndex}`}
            href={url}
            target="_blank"
            rel="noreferrer"
            className="underline underline-offset-4 decoration-[var(--amber)]"
          >
            {label || url}
          </a>,
        );
      }
      lastIndex = matchIndex + match[0].length;
    }
    if (lastIndex < line.length) parts.push(line.slice(lastIndex));
    return (
      <Fragment key={lineIndex}>
        {parts}
        {lineIndex < lines.length - 1 && <br />}
      </Fragment>
    );
  });
}

const STARTERS = [
  { text: "I am a farmer with land. What can I apply for?" },
  { text: "How do I get an Ayushman Bharat card?" },
  { text: "Is there a loan for a small shop?" },
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [language, setLanguage] = useState("en");
  const [voiceState, setVoiceState] = useState<"idle" | "recording" | "transcribing">("idle");
  const [voiceError, setVoiceError] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const ttsAudioRef = useRef<HTMLAudioElement | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    return () => {
      ttsAudioRef.current?.pause();
      if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    };
  }, []);

  const stopSpeaking = () => {
    if (ttsAudioRef.current) {
      ttsAudioRef.current.pause();
      ttsAudioRef.current = null;
    }
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    const userMessage: Message = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setVoiceError("");
    setIsLoading(true);

    try {
      const data = (await sendChatMessage(
        text,
        sessionId || undefined,
        language,
      )) as ChatResponse;
      if (!sessionId) setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.message,
          timestamp: data.timestamp,
          language: data.response_language,
          schemes: data.schemes,
          suggestedQuestions: data.suggested_questions,
        },
      ]);

      if (data.message) {
        const responseLang = data.response_language || language || "en";
        if (responseLang !== "en") {
          try {
            const audioUrl = await synthesizeSpeech(data.message, responseLang);
            stopSpeaking();
            const audio = new Audio(audioUrl);
            audio.onended = () => setIsSpeaking(false);
            ttsAudioRef.current = audio;
            setIsSpeaking(true);
            await audio.play();
          } catch {
            setIsSpeaking(false);
          }
        } else if ("speechSynthesis" in window) {
          stopSpeaking();
          const utterance = new SpeechSynthesisUtterance(data.message);
          utterance.lang = "en-IN";
          utterance.onstart = () => setIsSpeaking(true);
          utterance.onend = () => setIsSpeaking(false);
          window.speechSynthesis.speak(utterance);
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Connection failed. Check that the API is running, then try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bezel">
      <div className="bezel-inner flex h-[calc(100dvh-14rem)] flex-col">
        <div className="flex items-center justify-between gap-3 border-b border-[var(--line)] px-4 py-3">
          <LanguageSelector value={language} onChange={setLanguage} compact />
          <p className="text-xs text-[var(--faint)]">
            {sessionId ? `Session ${sessionId.slice(0, 8)}` : "New conversation"}
          </p>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto px-4 py-5">
          {messages.length === 0 && (
            <div className="mx-auto max-w-xl py-8">
              <p className="text-lg font-semibold">Ask about a scheme or your situation.</p>
              <p className="mt-2 text-sm text-[var(--muted)]">
                Retrieval uses the curated catalog first. Confirm the last step on the official site.
              </p>
              <div className="mt-6 grid gap-2">
                {STARTERS.map((item) => (
                  <button
                    key={item.text}
                    type="button"
                    onClick={() => sendMessage(item.text)}
                    className="rounded-2xl border border-[var(--line)] bg-[var(--paper)] px-4 py-3 text-left text-sm hover:border-[var(--forest)]"
                  >
                    {item.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={`${message.timestamp}-${index}`}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[min(40rem,92%)] rounded-[1.4rem] px-4 py-3 ${
                  message.role === "user"
                    ? "bg-[var(--forest)] text-[#f6f3ea]"
                    : "bg-[var(--paper)] text-[var(--ink)]"
                }`}
              >
                <div className="text-sm leading-7">{renderMessageContent(message.content)}</div>
                {message.schemes && message.schemes.length > 0 && (
                  <div className="mt-4 grid gap-2">
                    {dedupeSchemes(message.schemes).map((scheme) => (
                      <div
                        key={scheme.id}
                        className="rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-3 text-[var(--ink)]"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <p className="font-semibold">{scheme.name}</p>
                          <span className="scheme-chip">{scheme.category}</span>
                        </div>
                        {scheme.benefit_summary && (
                          <p className="mt-2 text-sm text-[var(--muted)]">{scheme.benefit_summary}</p>
                        )}
                        {scheme.apply_url && (
                          <a
                            href={scheme.apply_url}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-3 inline-flex text-sm font-semibold text-[var(--forest)]"
                          >
                            Official page
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                {message.suggestedQuestions && message.suggestedQuestions.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.suggestedQuestions.map((question) => (
                      <button
                        key={question}
                        type="button"
                        onClick={() => sendMessage(question)}
                        className="rounded-full border border-[var(--line)] px-3 py-1.5 text-xs"
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
              <CircleNotch size={16} className="animate-spin" />
              Looking up scheme records
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form
          onSubmit={(event) => {
            event.preventDefault();
            sendMessage(input);
          }}
          className="flex items-end gap-2 border-t border-[var(--line)] p-3"
        >
          <VoiceInputButton
            language={language}
            onTranscription={(text) => {
              setInput(text);
              setVoiceError("");
              inputRef.current?.focus();
            }}
            onError={setVoiceError}
            onStateChange={(state) => {
              setVoiceState(state);
              if (state !== "idle") setVoiceError("");
            }}
            size="md"
          />
          <input
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={
              voiceState === "recording"
                ? "Listening..."
                : voiceState === "transcribing"
                  ? "Transcribing..."
                  : "Ask about a scheme"
            }
            disabled={isLoading}
            autoComplete="off"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="icon-btn bg-[var(--forest)] text-[#f6f3ea] disabled:opacity-40"
            aria-label="Send"
          >
            <ArrowUp size={18} />
          </button>
        </form>
        {(isSpeaking || voiceError || voiceState !== "idle") && (
          <div className="px-4 pb-3 text-center text-xs text-[var(--muted)]">
            {isSpeaking && (
              <button type="button" onClick={stopSpeaking} className="underline">
                Stop voice
              </button>
            )}
            {voiceState !== "idle" && <p>{voiceState === "recording" ? "Listening" : "Transcribing"}</p>}
            {voiceError && <p className="text-red-700">{voiceError}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
