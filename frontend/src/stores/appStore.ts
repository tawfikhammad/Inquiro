import React from 'react';
import { Project, Paper, Summary, AppConfig, ChatMessage } from '../types';

// Simple state management without external dependencies
type StateListener = () => void;

class Store<T> {
    private state: T;
    private listeners: StateListener[] = [];

    constructor(initialState: T) {
        this.state = initialState;
    }

    getState(): T {
        return this.state;
    }

    setState(newState: Partial<T>): void {
        this.state = { ...this.state, ...newState };
        this.listeners.forEach(listener => listener());
    }

    subscribe(listener: StateListener): () => void {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }
}

// App State Interface
interface AppState {
    // Configuration
    config: AppConfig | null;
    isConfigured: boolean;

    // Current Project
    currentProject: Project | null;
    projects: Project[];

    // Papers and Summaries
    papers: Paper[];
    summaries: Summary[];
    currentPaper: Paper | null;
    currentSummary: Summary | null;

    // Chat
    chatMessages: ChatMessage[];
    isIndexed: boolean;
    indexInfo: any;

    // UI State
    isLoading: boolean;
    error: string | null;
    selectedText: string | null;
    showTranslateModal: boolean;
    showExplainModal: boolean;
}

const initialState: AppState = {
    config: null,
    isConfigured: false,
    currentProject: null,
    projects: [],
    papers: [],
    summaries: [],
    currentPaper: null,
    currentSummary: null,
    chatMessages: [],
    isIndexed: false,
    indexInfo: null,
    isLoading: false,
    error: null,
    selectedText: null,
    showTranslateModal: false,
    showExplainModal: false
};

export const appStore = new Store<AppState>(initialState);

// Helper functions for common operations
export const useAppState = () => {
    const [state, setState] = React.useState(appStore.getState());

    React.useEffect(() => {
        const unsubscribe = appStore.subscribe(() => {
            setState(appStore.getState());
        });
        return unsubscribe;
    }, []);

    return state;
};

export const setLoading = (isLoading: boolean) => {
    appStore.setState({ isLoading });
};

export const setError = (error: string | null) => {
    appStore.setState({ error });
};

export const setConfig = (config: AppConfig) => {
    appStore.setState({ config, isConfigured: true });
};

export const setCurrentProject = (project: Project | null) => {
    appStore.setState({ currentProject: project });
};

export const setProjects = (projects: Project[]) => {
    appStore.setState({ projects });
};

export const setPapers = (papers: Paper[]) => {
    appStore.setState({ papers });
};

export const setSummaries = (summaries: Summary[]) => {
    appStore.setState({ summaries });
};

export const setCurrentPaper = (paper: Paper | null) => {
    appStore.setState({ currentPaper: paper });
};

export const setCurrentSummary = (summary: Summary | null) => {
    appStore.setState({ currentSummary: summary });
};

export const addChatMessage = (message: ChatMessage) => {
    const state = appStore.getState();
    appStore.setState({
        chatMessages: [...state.chatMessages, message]
    });
};

export const clearChatMessages = () => {
    appStore.setState({ chatMessages: [] });
};

export const setSelectedText = (text: string | null) => {
    appStore.setState({ selectedText: text });
};

export const setShowTranslateModal = (show: boolean) => {
    appStore.setState({ showTranslateModal: show });
};

export const setShowExplainModal = (show: boolean) => {
    appStore.setState({ showExplainModal: show });
};

export const setIndexed = (isIndexed: boolean) => {
    appStore.setState({ isIndexed });
};

export const setIndexInfo = (indexInfo: any) => {
    appStore.setState({ indexInfo });
};