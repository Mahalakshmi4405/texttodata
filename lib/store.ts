// Global State Management with Zustand

import { create } from 'zustand';
import { Session, DataProfile } from '@/lib/api';

interface AppState {
    currentSession: Session | null;
    dataProfile: DataProfile | null;
    isLoading: boolean;
    error: string | null;

    setCurrentSession: (session: Session | null) => void;
    setDataProfile: (profile: DataProfile | null) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
    currentSession: null,
    dataProfile: null,
    isLoading: false,
    error: null,

    setCurrentSession: (session) => set({ currentSession: session }),
    setDataProfile: (profile) => set({ dataProfile: profile }),
    setLoading: (loading) => set({ isLoading: loading }),
    setError: (error) => set({ error }),
}));
