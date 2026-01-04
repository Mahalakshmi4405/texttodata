// API Client for Talk-to-Data Backend

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface Session {
    id: number;
    name: string;
    created_at: string;
    data_sources: DataSource[];
}

export interface DataSource {
    id: number;
    name: string;
    type: string;
    row_count: number;
    schema?: Record<string, string>;
    profile?: DataProfile;
}

export interface DataProfile {
    statistics: any;
    insights: string;
    quality_score: number;
    suggested_queries: string[];
}

export interface QueryResult {
    success: boolean;
    sql_query?: string;
    result?: any[];
    error?: string;
    visualization_type: string;
    execution_time_ms: number;
}

export interface QueryHistoryItem {
    id: number;
    question: string;
    sql: string;
    status: string;
    error?: string;
    visualization_type: string;
    execution_time_ms: number;
    created_at: string;
}

// API Methods

export const sessionsAPI = {
    list: async (): Promise<Session[]> => {
        const response = await api.get<Session[]>('/sessions');
        return response.data;
    },

    create: async (name: string): Promise<Session> => {
        const response = await api.post<Session>('/sessions', { name });
        return response.data;
    },

    get: async (sessionId: number): Promise<Session> => {
        const response = await api.get<Session>(`/sessions/${sessionId}`);
        return response.data;
    },

    delete: async (sessionId: number): Promise<void> => {
        await api.delete(`/sessions/${sessionId}`);
    },

    getHistory: async (sessionId: number): Promise<QueryHistoryItem[]> => {
        const response = await api.get<QueryHistoryItem[]>(`/sessions/${sessionId}/history`);
        return response.data;
    },
};

export const dataAPI = {
    upload: async (sessionId: number, file: File): Promise<any> => {
        const formData = new FormData();
        formData.append('session_id', sessionId.toString());
        formData.append('file', file);

        const response = await api.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    query: async (sessionId: number, question: string): Promise<QueryResult> => {
        const response = await api.post<QueryResult>('/query', {
            session_id: sessionId,
            question,
        });
        return response.data;
    },
};
