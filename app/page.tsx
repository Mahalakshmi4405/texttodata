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
    Trash2,
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
    const [isVizExpanded, setIsVizExpanded] = useState(false);
    const [theme] = useState('aurora');
    const { currentSession, setCurrentSession, dataProfile, setDataProfile } = useAppStore();

    // Set theme on mount
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', 'aurora');
        localStorage.setItem('talktodata-theme', 'aurora');
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
        // If empty, generate a default name
        const nameToUse = newSessionName.trim() || `New Session ${sessions.length + 1}`;

        try {
            const session = await sessionsAPI.create(nameToUse);
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

    const handleDeleteSession = async (sessionId: number) => {
        if (!confirm('Are you sure you want to delete this session?')) return;

        try {
            await sessionsAPI.delete(sessionId);
            setSessions((prev) => prev.filter((s) => s.id !== sessionId));

            if (currentSession?.id === sessionId) {
                setCurrentSession(null);
                setQueryResult(null);
                setDataProfile(null);
            }
        } catch (error) {
            console.error('Failed to delete session:', error);
        }
    };

    const hasData = currentSession?.data_sources && currentSession.data_sources.length > 0;

    return (
        <div className="min-h-screen flex flex-col transition-colors duration-300">
            {/* Header */}
            <header className="bg-[#0F172A]/80 backdrop-blur-md sticky top-0 z-50 border-b border-white/5">
                <div className="max-w-[1800px] mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 rounded-xl bg-primary/10 border border-primary/20 text-primary">
                                <Sparkles className="w-5 h-5" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold tracking-tight">
                                    <span className="text-gradient">
                                        Talk-to-Data
                                    </span>
                                </h1>
                            </div>
                        </div>

                        {/* Controls */}
                        <div className="flex items-center gap-4">

                            {/* Session Selector */}
                            <div className="flex items-center gap-2">
                                <select
                                    value={currentSession?.id || ''}
                                    onChange={(e) => handleSelectSession(Number(e.target.value))}
                                    className="select select-bordered select-sm w-full max-w-xs bg-[#1E293B] text-white border-white/10 focus:outline-none focus:border-primary"
                                >
                                    <option value="">Select Session</option>
                                    {sessions.map((session) => (
                                        <option key={session.id} value={session.id}>
                                            {session.name}
                                        </option>
                                    ))}
                                </select>

                                {currentSession && (
                                    <button
                                        onClick={() => handleDeleteSession(currentSession.id)}
                                        className="btn btn-square btn-sm btn-ghost text-error hover:bg-error/10"
                                        title="Delete Session"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                )}
                            </div>

                            {/* Divider matching reference image */}
                            <div className="h-8 w-px bg-white/10 mx-2" />

                            <div className="flex items-center gap-2">
                                <input
                                    type="text"
                                    value={newSessionName}
                                    onChange={(e) => setNewSessionName(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleCreateSession()}
                                    placeholder="New session name"
                                    className="input input-bordered input-sm w-40 bg-[#1E293B] text-white border-white/10 placeholder-slate-500 focus:outline-none focus:border-primary"
                                />
                                <button
                                    onClick={handleCreateSession}
                                    className="btn btn-sm btn-primary"
                                >
                                    <Plus className="w-4 h-4" />
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
                    <div className={`w-80 flex flex-col gap-6 overflow-y-auto transition-all duration-300 ${isVizExpanded ? 'w-0 opacity-0 overflow-hidden p-0 m-0' : ''}`}>
                        {/* Session Info */}
                        {currentSession && (
                            <div className="card bg-neutral shadow-lg border border-white/5 p-6 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-primary/20 transition-all"></div>

                                <div className="flex items-center gap-2 mb-3 relative z-10">
                                    <Database className="w-4 h-4 text-primary" />
                                    <h2 className="text-sm font-bold opacity-70 tracking-wider uppercase">
                                        Active Session
                                    </h2>
                                </div>
                                <h3 className="text-xl font-bold mb-4 relative z-10 text-white">
                                    {currentSession.name}
                                </h3>

                                {hasData ? (
                                    <div className="space-y-3 text-sm">
                                        <div className="flex justify-between">
                                            <span className="opacity-60">Data Source:</span>
                                            <span className="font-medium text-white">
                                                {currentSession.data_sources[0].name}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="opacity-60">Rows:</span>
                                            <span className="font-medium text-white">
                                                {currentSession.data_sources[0].row_count.toLocaleString()}
                                            </span>
                                        </div>
                                    </div>
                                ) : (
                                    <p className="opacity-50 text-sm">No data uploaded yet</p>
                                )}
                            </div>
                        )}

                        {/* Data Quality */}
                        {dataProfile && (
                            <div className="card bg-neutral shadow-lg border-l-4 border-success p-6">
                                <div className="flex items-center gap-2 mb-4">
                                    <TrendingUp className="w-5 h-5 text-success" />
                                    <h2 className="text-lg font-semibold text-white">Data Quality</h2>
                                </div>

                                <div className="mb-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="opacity-70 text-sm">Overall Score</span>
                                        <span className="font-bold text-lg text-success">
                                            {dataProfile.quality_score.toFixed(0)}/100
                                        </span>
                                    </div>
                                    <div className="h-3 w-full bg-base-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-success to-secondary transition-all duration-1000"
                                            style={{ width: `${dataProfile.quality_score}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Insights */}
                        {dataProfile?.insights && (
                            <div className="card bg-neutral shadow-lg border border-accent/30 p-6 relative">
                                <div className="absolute top-0 right-0 p-4 opacity-20">
                                    <Sparkles className="w-12 h-12 text-accent" />
                                </div>
                                <div className="flex items-center gap-2 mb-4">
                                    <FileText className="w-5 h-5 text-accent" />
                                    <h2 className="text-lg font-semibold text-white">AI Insights</h2>
                                </div>

                                <div className="text-sm opacity-90 whitespace-pre-line leading-relaxed">
                                    {dataProfile.insights}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Main Area */}
                    <div className="flex-1 flex flex-col gap-6 min-w-0">
                        {!currentSession ? (
                            <div className="flex-1 flex items-center justify-center bg-[#1E293B] border border-white/10 rounded-3xl border-dashed m-6">
                                <div className="text-center p-10 max-w-md w-full">
                                    <AlertCircle className="w-16 h-16 text-primary mx-auto mb-4" />
                                    <h3 className="text-2xl font-bold mb-2 text-white">
                                        No Session Selected
                                    </h3>
                                    <p className="text-slate-400 mb-6">
                                        Create a new session to access Data Quality, AI Insights, and Chat features.
                                    </p>

                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            value={newSessionName}
                                            onChange={(e) => setNewSessionName(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && handleCreateSession()}
                                            placeholder="Enter session name..."
                                            className="input input-bordered w-full bg-[#0F172A] border-white/10 text-white focus:outline-none focus:border-primary"
                                        />
                                        <button
                                            onClick={handleCreateSession}
                                            className="btn btn-primary"
                                        >
                                            <Plus className="w-4 h-4 mr-2" />
                                            Create
                                        </button>
                                    </div>
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
                                <div className={`flex-1 overflow-hidden bg-neutral rounded-3xl p-6 flex flex-col transition-all duration-300 shadow-xl border border-secondary/20`}>
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="text-sm font-bold text-secondary uppercase tracking-widest">Data Visualization</h3>
                                        {queryResult && (
                                            <button
                                                onClick={() => setIsVizExpanded(!isVizExpanded)}
                                                className="btn btn-xs btn-ghost text-secondary hover:bg-secondary/10"
                                            >
                                                {isVizExpanded ? 'Collapse View' : 'Expand View'}
                                            </button>
                                        )}
                                    </div>

                                    {queryResult ? (
                                        <DataVisualization
                                            data={queryResult.result || []}
                                            visualizationType={queryResult.visualization_type as any}
                                            sqlQuery={queryResult.sql_query}
                                        />
                                    ) : (
                                        <div className="h-full flex flex-col items-center justify-center opacity-40 gap-4">
                                            <Sparkles className="w-12 h-12 text-secondary" />
                                            <p className="text-lg font-medium">Ask a question to see results Visualized</p>
                                        </div>
                                    )}
                                </div>

                                {/* Chat Area */}
                                <div className={`bg-neutral rounded-3xl overflow-hidden shrink-0 transition-all duration-300 shadow-xl border border-white/5 ${isVizExpanded ? 'h-0 opacity-0 overflow-hidden m-0 p-0' : 'h-80'}`}>
                                    <ChatInterface
                                        sessionId={currentSession.id}
                                        suggestedQueries={dataProfile?.suggested_queries}
                                        onQuerySuccess={setQueryResult}
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
