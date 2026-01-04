// Main Dashboard Page

'use client';

import React, { useState, useEffect } from 'react';
import {
    Database,
    Plus,
    Sparkles,
    TrendingUp,
    FileText,
    AlertCircle,
} from 'lucide-react';
import { sessionsAPI, Session, QueryResult } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import DataUpload from '@/components/DataUpload';
import ChatInterface from '@/components/ChatInterface';
import DataVisualization from '@/components/DataVisualization';

export default function Home() {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [newSessionName, setNewSessionName] = useState('');
    const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
    const { currentSession, setCurrentSession, dataProfile, setDataProfile } = useAppStore();

    // Load sessions on mount
    useEffect(() => {
        loadSessions();
    }, []);

    const loadSessions = async () => {
        try {
            const data = await sessionsAPI.list();
            setSessions(data);

            // Auto-select first session if none selected
            if (!currentSession && data.length > 0) {
                handleSelectSession(data[0].id);
            }
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    };

    const handleCreateSession = async () => {
        if (!newSessionName.trim()) return;

        try {
            const session = await sessionsAPI.create(newSessionName);
            setSessions((prev) => [session, ...prev]);
            setCurrentSession(session);
            setNewSessionName('');
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    };

    const handleSelectSession = async (sessionId: number) => {
        try {
            const session = await sessionsAPI.get(sessionId);
            setCurrentSession(session);

            // Load data profile if available
            if (session.data_sources.length > 0 && session.data_sources[0].profile) {
                setDataProfile(session.data_sources[0].profile);
            } else {
                setDataProfile(null);
            }

            setQueryResult(null);
        } catch (error) {
            console.error('Failed to load session:', error);
        }
    };

    const hasData = currentSession?.data_sources && currentSession.data_sources.length > 0;

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="glass-dark border-b border-dark-800 sticky top-0 z-50">
                <div className="max-w-[1800px] mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600">
                                <Sparkles className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-white">Talk-to-Data AI</h1>
                                <p className="text-xs text-dark-400">
                                    Natural Language Data Analysis Platform
                                </p>
                            </div>
                        </div>

                        {/* Session Selector */}
                        <div className="flex items-center gap-3">
                            <select
                                value={currentSession?.id || ''}
                                onChange={(e) => handleSelectSession(Number(e.target.value))}
                                className="px-4 py-2 rounded-lg glass text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                            >
                                <option value="">Select Session</option>
                                {sessions.map((session) => (
                                    <option key={session.id} value={session.id}>
                                        {session.name}
                                    </option>
                                ))}
                            </select>

                            <div className="flex items-center gap-2">
                                <input
                                    type="text"
                                    value={newSessionName}
                                    onChange={(e) => setNewSessionName(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleCreateSession()}
                                    placeholder="New session name"
                                    className="px-4 py-2 rounded-lg glass text-white placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                                <button
                                    onClick={handleCreateSession}
                                    className="p-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white transition-colors"
                                >
                                    <Plus className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex">
                <div className="max-w-[1800px] w-full mx-auto flex gap-6 p-6 h-[calc(100vh-88px)]">
                    {/* Sidebar - Data Profile */}
                    <div className="w-80 flex flex-col gap-6 overflow-y-auto">
                        {/* Session Info */}
                        {currentSession && (
                            <div className="glass rounded-xl p-6">
                                <div className="flex items-center gap-2 mb-4">
                                    <Database className="w-5 h-5 text-primary-400" />
                                    <h2 className="text-lg font-semibold text-white">
                                        {currentSession.name}
                                    </h2>
                                </div>

                                {hasData ? (
                                    <div className="space-y-3 text-sm">
                                        <div>
                                            <span className="text-dark-400">Data Source:</span>
                                            <p className="text-white font-medium">
                                                {currentSession.data_sources[0].name}
                                            </p>
                                        </div>
                                        <div>
                                            <span className="text-dark-400">Rows:</span>
                                            <p className="text-white font-medium">
                                                {currentSession.data_sources[0].row_count.toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                ) : (
                                    <p className="text-dark-500 text-sm">No data uploaded yet</p>
                                )}
                            </div>
                        )}

                        {/* Data Quality */}
                        {dataProfile && (
                            <div className="glass rounded-xl p-6">
                                <div className="flex items-center gap-2 mb-4">
                                    <TrendingUp className="w-5 h-5 text-green-400" />
                                    <h2 className="text-lg font-semibold text-white">Data Quality</h2>
                                </div>

                                <div className="mb-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-dark-400 text-sm">Overall Score</span>
                                        <span className="text-white font-bold text-lg">
                                            {dataProfile.quality_score.toFixed(0)}/100
                                        </span>
                                    </div>
                                    <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-green-500 to-primary-500 transition-all duration-500"
                                            style={{ width: `${dataProfile.quality_score}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Insights */}
                        {dataProfile?.insights && (
                            <div className="glass rounded-xl p-6">
                                <div className="flex items-center gap-2 mb-4">
                                    <FileText className="w-5 h-5 text-purple-400" />
                                    <h2 className="text-lg font-semibold text-white">AI Insights</h2>
                                </div>

                                <div className="text-sm text-dark-300 whitespace-pre-line">
                                    {dataProfile.insights}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Main Area */}
                    <div className="flex-1 flex flex-col gap-6 min-w-0">
                        {!currentSession ? (
                            <div className="flex-1 flex items-center justify-center glass rounded-xl">
                                <div className="text-center">
                                    <AlertCircle className="w-16 h-16 text-dark-600 mx-auto mb-4" />
                                    <h3 className="text-xl font-semibold text-white mb-2">
                                        No Session Selected
                                    </h3>
                                    <p className="text-dark-400">
                                        Create or select a session to get started
                                    </p>
                                </div>
                            </div>
                        ) : !hasData ? (
                            <div className="flex-1 flex items-center justify-center">
                                <div className="max-w-2xl w-full">
                                    <DataUpload
                                        sessionId={currentSession.id}
                                        onUploadComplete={() => handleSelectSession(currentSession.id)}
                                    />
                                </div>
                            </div>
                        ) : (
                            <>
                                {/* Visualization Area */}
                                <div className="flex-1 overflow-auto glass rounded-xl p-6">
                                    {queryResult ? (
                                        <DataVisualization
                                            data={queryResult.result || []}
                                            visualizationType={queryResult.visualization_type as any}
                                            sqlQuery={queryResult.sql_query}
                                        />
                                    ) : (
                                        <div className="h-full flex items-center justify-center text-dark-500">
                                            <p>Ask a question to see results visualized here</p>
                                        </div>
                                    )}
                                </div>

                                {/* Chat Area */}
                                <div className="h-96 glass rounded-xl overflow-hidden">
                                    <ChatInterface
                                        sessionId={currentSession.id}
                                        suggestedQueries={dataProfile?.suggested_queries}
                                    />
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
