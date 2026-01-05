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
}

export default function ChatInterface({ sessionId, suggestedQueries = [] }: ChatInterfaceProps) {
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
                        <p className="text-dark-400 mb-6">
                            I'll translate your questions into SQL and execute them
                        </p>

                        {suggestedQueries.length > 0 && (
                            <div className="max-w-2xl mx-auto">
                                <p className="text-sm text-dark-500 mb-3">Suggested queries:</p>
                                <div className="grid gap-2">
                                    {suggestedQueries.map((query, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => handleSuggestedQuery(query)}
                                            className="text-left p-3 rounded-lg glass hover-lift transition-all text-dark-300 hover:text-white"
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
                            className={`max-w-[80%] rounded-2xl p-4 animate-slide-up ${message.type === 'user'
                                    ? 'bg-primary-600 text-white'
                                    : message.type === 'error'
                                        ? 'glass-dark border-red-500/30'
                                        : 'glass'
                                }`}
                        >
                            <div className="flex items-start gap-2 mb-2">
                                {message.type === 'assistant' && (
                                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                                )}
                                {message.type === 'error' && (
                                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                                )}
                                <p className="text-sm">{message.content}</p>
                            </div>

                            {message.queryResult?.sql_query && (
                                <div className="mt-3 p-3 rounded-lg bg-black/30 border border-dark-700">
                                    <p className="text-xs text-dark-400 mb-1">Generated SQL:</p>
                                    <code className="text-xs text-primary-300 font-mono">
                                        {message.queryResult.sql_query}
                                    </code>
                                </div>
                            )}

                            {message.queryResult?.execution_time_ms && (
                                <div className="flex items-center gap-1 mt-2 text-xs text-dark-400">
                                    <Clock className="w-3 h-3" />
                                    {message.queryResult.execution_time_ms.toFixed(2)}ms
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="glass rounded-2xl p-4 flex items-center gap-3">
                            <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                            <span className="text-dark-300">Analyzing query...</span>
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
                        className="flex-1 px-4 py-3 rounded-xl glass text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="px-6 py-3 rounded-xl bg-primary-600 hover:bg-primary-700 text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
