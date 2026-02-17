// Chat Interface for Natural Language Queries

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { dataAPI, QueryResult } from '@/lib/api';

interface Message {
    id: string;
    type: 'user' | 'assistant' | 'error';
    content: string;
    queryResult?: QueryResult;
    timestamp: Date;
}

interface ChatInterfaceProps {
    sessionId: number;
    suggestedQueries?: string[];
    onQuerySuccess?: (result: QueryResult) => void;
}

export default function ChatInterface({ sessionId, suggestedQueries = [], onQuerySuccess }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            type: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const result = await dataAPI.query(sessionId, input);

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: result.success ? 'assistant' : 'error',
                content: result.success
                    ? `Query executed successfully in ${result.execution_time_ms.toFixed(2)}ms`
                    : result.error || 'Query failed',
                queryResult: result,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);

            if (result.success && onQuerySuccess) {
                onQuerySuccess(result);
            }
        } catch (error: any) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'error',
                content: error.response?.data?.detail || 'Failed to execute query',
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestedQuery = (query: string) => {
        setInput(query);
    };

    return (
        <div className="flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center py-12">
                        <h3 className="text-xl font-semibold text-white mb-4">
                            Ask me anything about your data
                        </h3>
                        <p className="text-slate-400 mb-6">
                            I'll translate your questions into SQL and execute them
                        </p>

                        {suggestedQueries.length > 0 && (
                            <div className="max-w-2xl mx-auto">
                                <p className="text-sm text-slate-500 mb-3">Suggested queries:</p>
                                <div className="grid gap-2">
                                    {suggestedQueries.map((query, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => handleSuggestedQuery(query)}
                                            className="text-left p-3 bg-[#1E293B]/80 backdrop-blur-md border border-white/10 shadow-lg rounded-2xl hover-lift transition-all text-slate-300 hover:text-white hover:bg-[#1E293B]"
                                        >
                                            💡 {query}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[85%] rounded-2xl p-4 shadow-lg ${message.type === 'user'
                                ? 'bg-gradient-to-br from-primary to-[#06B6D4] text-white'
                                : message.type === 'error'
                                    ? 'bg-red-500/10 border border-red-500/20 text-red-200'
                                    : 'bg-[#1E293B] border border-white/5 text-slate-100'
                                }`}
                        >
                            <div className="flex items-start gap-2 mb-2">
                                {message.type === 'assistant' && (
                                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                                )}
                                {message.type === 'error' && (
                                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                                )}
                                <p className="text-sm leading-relaxed">{message.content}</p>
                            </div>

                            {message.queryResult?.sql_query && (
                                <div className="mt-3 p-3 rounded-lg bg-black/30 border border-white/10">
                                    <p className="text-xs text-slate-400 mb-1">Generated SQL:</p>
                                    <code className="text-xs text-primary font-mono block overflow-x-auto">
                                        {message.queryResult.sql_query}
                                    </code>
                                </div>
                            )}

                            {message.queryResult?.execution_time_ms && (
                                <div className="flex items-center gap-1 mt-2 text-xs text-slate-400">
                                    <Clock className="w-3 h-3" />
                                    {message.queryResult.execution_time_ms.toFixed(2)}ms
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-[#1E293B] rounded-2xl p-4 flex items-center gap-3 border border-white/5">
                            <Loader2 className="w-5 h-5 text-primary animate-spin" />
                            <span className="text-slate-300">Analyzing query...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-dark-800 p-4">
                <form onSubmit={handleSubmit} className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your data..."
                        disabled={isLoading}
                        className="flex-1 px-4 py-3 rounded-xl bg-[#1E293B] border border-white/10 shadow-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="px-6 py-3 rounded-xl bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-500 hover:to-secondary-500 text-white font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/40 transform hover:-translate-y-0.5"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Send className="w-5 h-5" />
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
