'use client';

import { useState, useRef, useEffect } from 'react';
import { ChatMessage, ChatResponse, SchemeCard } from '@/types';
import { sendMessage as sendChatMessage } from '@/lib/api';
import { VoiceInputButton } from './VoiceInput';
import { LanguageSelector } from './LanguageSelector';

interface Message extends ChatMessage {
    schemes?: SchemeCard[];
    suggestedQuestions?: string[];
}

const LANGUAGE_QUESTIONS: Record<string, { text: string; english: string }[]> = {
    'hi': [
        { text: 'मैं पीएम किसान के लिए पात्र हूं क्या?', english: 'Am I eligible for PM-KISAN?' },
        { text: 'आयुष्मान भारत कार्ड कैसे बनवाएं?', english: 'How to get Ayushman Bharat card?' },
        { text: 'कौन सी योजनाएं मेरे लिए उपलब्ध हैं?', english: 'Which schemes are available for me?' },
    ],
    'te': [
        { text: 'నేను PM-KISAN కు అర్హుడినా?', english: 'Am I eligible for PM-KISAN?' },
        { text: 'ఆయుష్మాన్ భారత్ కార్డ్ ఎలా పొందాలి?', english: 'How to get Ayushman Bharat card?' },
        { text: 'నాకు ఏ పథకాలు అందుబాటులో ఉన్నాయి?', english: 'Which schemes are available for me?' },
    ],
    'ta': [
        { text: 'நான் PM-KISAN க்கு தகுதியானவரா?', english: 'Am I eligible for PM-KISAN?' },
        { text: 'ஆயுஷ்மான் பாரத் அட்டை எப்படி பெறுவது?', english: 'How to get Ayushman Bharat card?' },
        { text: 'எனக்கு என்ன திட்டங்கள் உள்ளன?', english: 'Which schemes are available for me?' },
    ],
    'bn': [
        { text: 'আমি কি PM-KISAN এর জন্য যোগ্য?', english: 'Am I eligible for PM-KISAN?' },
        { text: 'আয়ুষ্মান ভারত কার্ড কিভাবে পাব?', english: 'How to get Ayushman Bharat card?' },
        { text: 'আমার জন্য কোন প্রকল্প আছে?', english: 'Which schemes are available for me?' },
    ],
};

const DEFAULT_QUESTIONS = [
    'Am I eligible for PM-KISAN?',
    'Tell me about Ayushman Bharat',
    'What documents do I need?',
];

export function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [language, setLanguage] = useState('en');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const getCurrentQuestions = () => {
        if (language === 'auto' || language === 'en') {
            return DEFAULT_QUESTIONS.map(q => ({ text: q, english: q }));
        }
        return LANGUAGE_QUESTIONS[language] || DEFAULT_QUESTIONS.map(q => ({ text: q, english: q }));
    };

    const sendMessage = async (text: string) => {
        if (!text.trim() || isLoading) return;

        const userMessage: Message = {
            role: 'user',
            content: text,
            timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const data = await sendChatMessage(
                text,
                sessionId || undefined,
                language === 'auto' ? 'auto' : language
            ) as ChatResponse;

            if (!sessionId) {
                setSessionId(data.session_id);
            }

            const aiMessage: Message = {
                role: 'assistant',
                content: data.message,
                timestamp: data.timestamp,
                language: data.response_language,
                schemes: data.schemes,
                suggestedQuestions: data.suggested_questions,
            };
            setMessages(prev => [...prev, aiMessage]);

            if (data.message && 'speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(data.message);
                utterance.lang = data.response_language === 'hi' ? 'hi-IN' :
                               data.response_language === 'te' ? 'te-IN' :
                               data.response_language === 'ta' ? 'ta-IN' : 'en-IN';
                window.speechSynthesis.speak(utterance);
            }
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Connection error. Please check if the backend server is running.',
                timestamp: new Date().toISOString(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-12rem)] max-w-3xl mx-auto">
            {/* Language Selector */}
            <div className="flex justify-between items-center mb-4 px-1">
                <div className="flex items-center gap-3">
                    <label htmlFor="language-select" className="text-slate-500 text-sm">Language:</label>
                    <LanguageSelector
                        value={language}
                        onChange={setLanguage}
                        compact
                    />
                </div>
                {sessionId && (
                    <span className="text-slate-400 text-xs">
                        Session: {sessionId.slice(0, 8)}
                    </span>
                )}
            </div>

            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto space-y-4 px-1 pb-4 scrollbar-hide">
                {messages.length === 0 && (
                    <div className="text-center py-12">
                        <div className="glass-card p-6 max-w-md mx-auto text-left mb-6">
                            <div className="flex items-center gap-2 mb-4">
                                <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                                <span className="text-sm text-slate-500">Sahay AI Ready</span>
                            </div>
                            <p className="text-slate-700 mb-4">Welcome! I can help you:</p>
                            <ul className="space-y-2 text-slate-600 text-sm">
                                <li className="flex items-center gap-2">
                                    <span className="text-emerald-600">•</span>
                                    Discover 500+ government schemes
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-emerald-600">•</span>
                                    Check your eligibility instantly
                                </li>
                                <li className="flex items-center gap-2">
                                    <span className="text-emerald-600">•</span>
                                    Guide you through applications
                                </li>
                            </ul>
                        </div>

                        {/* Suggested Questions */}
                        <div className="flex flex-col gap-2 max-w-md mx-auto">
                            {getCurrentQuestions().map((q, i) => (
                                <button
                                    key={i}
                                    onClick={() => sendMessage(q.text)}
                                    className="w-full px-4 py-3 glass-card text-left hover:border-emerald-300 transition-all group"
                                >
                                    <span className="text-slate-700 text-sm">{q.text}</span>
                                    {q.text !== q.english && (
                                        <span className="block text-slate-400 text-xs mt-1">{q.english}</span>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[85%] px-4 py-3 rounded-2xl ${
                                message.role === 'user'
                                    ? 'bg-emerald-50 border border-emerald-200 rounded-br-sm text-slate-800'
                                    : 'glass-card rounded-bl-sm'
                            }`}
                        >
                            {message.role === 'assistant' && (
                                <div className="flex items-center gap-2 mb-2">
                                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                                    <span className="text-xs text-slate-400">Sahay AI</span>
                                </div>
                            )}
                            <div className="whitespace-pre-wrap text-sm text-slate-700 leading-relaxed">
                                {message.content}
                            </div>

                            {message.schemes && message.schemes.length > 0 && (
                                <div className="mt-4 space-y-2">
                                    <p className="text-xs text-slate-400 uppercase tracking-wider">Related Schemes</p>
                                    {message.schemes.map((scheme) => (
                                        <div key={scheme.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                                            <div className="flex justify-between items-start mb-1">
                                                <h4 className="font-medium text-slate-800 text-sm">{scheme.name}</h4>
                                                <span className="text-xs px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded border border-emerald-200">
                                                    {scheme.category}
                                                </span>
                                            </div>
                                            {scheme.benefit_summary && (
                                                <p className="text-xs text-emerald-700">{scheme.benefit_summary}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {message.suggestedQuestions && message.suggestedQuestions.length > 0 && (
                                <div className="mt-4 flex flex-wrap gap-2">
                                    {message.suggestedQuestions.map((q, i) => (
                                        <button
                                            key={i}
                                            onClick={() => sendMessage(q)}
                                            className="text-xs px-3 py-1.5 bg-slate-50 text-slate-600 rounded-lg hover:bg-slate-100 hover:text-slate-800 transition-colors border border-slate-200"
                                        >
                                            {q}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="glass-card px-4 py-3 rounded-2xl rounded-bl-sm">
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-slate-400">Thinking</span>
                                <div className="flex gap-1">
                                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="pt-4 border-t border-slate-200">
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        sendMessage(input);
                    }}
                    className="flex gap-3"
                >
                    <VoiceInputButton
                        language={language}
                        onTranscription={(text) => {
                            setInput(text);
                            sendMessage(text);
                        }}
                        onError={(error) => {
                            console.error('Voice error:', error);
                        }}
                        size="md"
                    />
                    
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about schemes..."
                        className="flex-1 px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-100 text-sm transition-colors"
                        disabled={isLoading}
                        autoComplete="off"
                    />
                    
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="px-5 py-3 bg-emerald-600 text-white rounded-xl font-medium text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:bg-emerald-500 transition-colors"
                    >
                        Send
                    </button>
                </form>
                <p className="text-slate-400 text-xs mt-3 text-center">
                    Speak or type in any language • Data is secure
                </p>
            </div>
        </div>
    );
}
