export interface Project {
    _id: string;
    project_title: string;
    created_at?: string;
    updated_at?: string;
}

export interface Paper {
    _id: string;
    paper_project_id: string;
    paper_name: string;
    paper_type: string;
    paper_size: number;
    created_at?: string;
    updated_at?: string;
}

export interface Summary {
    _id: string;
    summary_project_id: string;
    summary_paper_id: string;
    summary_name: string;
    summary_type: string;
    summary_size: number;
    created_at?: string;
    updated_at?: string;
}

export interface Chunk {
    _id: string;
    chunk_project_id: string;
    chunk_paper_id: string;
    chunk_section_id: string;
    chunk_text: string;
    chunk_metadata: any;
    chunk_index_in_paper: number;
}

export interface ChatMessage {
    id: string;
    type: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export interface SearchResult {
    chunk_text: string;
    chunk_metadata: any;
    score: number;
}

export interface AppConfig {
    generationModel: string;
    embeddingModel: string;
    geminiApiKey: string;
    temperature: number;
    maxTokens: number;
}

export interface TranslateRequest {
    text: string;
    target_language: string;
}

export interface ExplainRequest {
    text: string;
    context?: string;
}

export interface SearchRequest {
    query: string;
    limit?: number;
    RAGFusion?: boolean;
}

export interface ProjectRequest {
    project_title: string;
}

export interface PushRequest {
    do_reset?: number;
}

export interface FileUploadStatus {
    isUploading: boolean;
    progress: number;
    error: string | null;
}

// Backend response types
export interface ApiResponse<T> {
    message?: string;
    signal?: string;
    data?: T;
}

export interface ProjectAssetsResponse {
    "papers number": number;
    "summaries number": number;
}

export interface VDBIndexResponse {
    signal: string;
    inserted_items_count: number;
}

export interface VDBInfoResponse {
    signal: string;
    collection_info: {
        vectors_count?: number;
        indexed_vectors_count?: number;
        points_count?: number;
        segments_count?: number;
    };
}

export interface VDBSearchResponse {
    signal: string;
    results: SearchResult[];
}

export interface RAGAnswerResponse {
    signal: string;
    answer: string;
}

export interface TranslateResponse {
    translated_text: string;
}

export interface ExplainResponse {
    explanation: string;
}