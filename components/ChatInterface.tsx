// Chat Interface for Natural Language Queries

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, CheckCircle, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { dataAPI, QueryResult } from '@/lib/api';
import InlineChart from './InlineChart';

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

    const handleSend = async () => {
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
                    ? (result.ai_explanation || `Query executed successfully in ${result.execution_time_ms.toFixed(2)}ms`)
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
                            I'll analyze your data and provide insights with visualizations
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
                    <ChatMessage key={message.id} message={message} />
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="glass rounded-2xl p-4 flex items-center gap-3">
                            <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                            <span className="text-dark-300">Analyzing your question...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-dark-800 p-4">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask a question about your data..."
                        className="flex-1 px-4 py-3 rounded-lg glass border border-dark-700 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all text-white placeholder-dark-400"
                        disabled={isLoading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-700 disabled:cursor-not-allowed rounded-lg transition-all hover-lift flex items-center gap-2"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}

// Separate component for chat messages
function ChatMessage({ message }: { message: Message }) {
    const [showSQL, setShowSQL] = useState(false);

    return (
        <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`max-w-[85%] rounded-2xl p-4 animate-slide-up ${message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : message.type === 'error'
                        ? 'glass-dark border-red-500/30'
                        : 'glass'
                    }`}
            >
                {/* AI/Error Icon + Message */}
                <div className="flex items-start gap-2">
                    {message.type === 'assistant' && (
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    )}
                    {message.type === 'error' && (
                        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    )}
                    <p className="text-sm leading-relaxed whitespace-pre-line flex-1">
                        {message.content}
                    </p>
                </div>

                {/* Inline Visualization */}
                {message.queryResult?.success && message.queryResult.result_data && message.queryResult.result_data.length > 0 && (
                    <div className="mt-4">
                        <InlineChart
                            type={message.queryResult.visualization_type as 'bar' | 'line' | 'pie' | 'table'}
                            data={message.queryResult.result_data}
                            columns={message.queryResult.columns || []}
                        />
                    </div>
                )}

                {/* Collapsible SQL Query (Optional) */}
                {message.queryResult?.sql_query && (
                    <div className="mt-3">
                        <button
                            onClick={() => setShowSQL(!showSQL)}
                            className="flex items-center gap-1 text-xs text-dark-400 hover:text-dark-200 transition-colors"
                        >
                            {showSQL ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                            {showSQL ? 'Hide' : 'View'} SQL Query
                        </button>
                        {showSQL && (
                            <div className="mt-2 p-3 rounded-lg bg-black/30 border border-dark-700">
                                <code className="text-xs text-primary-300 font-mono block whitespace-pre-wrap break-all">
                                    {message.queryResult.sql_query}
                                </code>
                            </div>
                        )}
                    </div>
                )}

                {/* Execution Time */}
                {message.queryResult?.execution_time_ms !== undefined && (
                    <div className="flex items-center gap-1 mt-2 text-xs text-dark-500">
                        <Clock className="w-3 h-3" />
                        {message.queryResult.execution_time_ms.toFixed(0)}ms
                    </div>
                )}
            </div>
        </div>
    );
}
