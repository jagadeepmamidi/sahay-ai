import { ChatInterface } from "@/components/ChatInterface";

export const metadata = {
  title: "Ask Sahay",
  description: "Ask about government schemes in English or an Indian language.",
};

export default function ChatPage() {
  return (
    <div className="shell py-8 md:py-10">
      <div className="mb-6 max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight">Ask Sahay</h1>
        <p className="mt-2 text-[var(--muted)]">
          Scheme names, work, or a situation. Answers stay tied to official records.
        </p>
      </div>
      <ChatInterface />
    </div>
  );
}
