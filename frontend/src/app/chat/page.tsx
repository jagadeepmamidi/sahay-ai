import { ChatInterface } from '@/components/ChatInterface';

export const metadata = {
    title: 'Chat — SAHAY.AI',
    description: 'Ask about government schemes in any Indian language',
};

export default function ChatPage() {
    return (
        <div className="max-w-4xl mx-auto px-6 py-8">
            <div className="mb-6">
                <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-2xl font-semibold text-slate-950">Chat with Sahay AI</h1>
                    <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 border border-emerald-200 rounded-full">
                        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                        <span className="text-emerald-700 text-xs font-medium">Online</span>
                    </div>
                </div>
                <p className="text-slate-500 text-sm">Ask in English, Hindi, or any Indian language</p>
            </div>
            <ChatInterface />
        </div>
    );
}
