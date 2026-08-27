export const metadata = { title: "Privacy" };

export default function PrivacyPage() {
  return (
    <div className="shell py-14">
      <h1 className="text-4xl font-semibold tracking-tight">Privacy</h1>
      <p className="lede mt-4">
        Chat messages are processed to retrieve scheme records and generate an answer. We do not sell personal data. Do not send Aadhaar numbers, bank details, or passwords in chat.
      </p>
      <p className="mt-6 max-w-2xl text-sm leading-7 text-[var(--muted)]">
        Voice features send audio to the configured speech provider only when you use the microphone. Eligibility forms stay in your browser until you submit them to the API.
      </p>
    </div>
  );
}
