import { apiClient } from './api';
import {
    Project,
    Paper,
    Summary,
    SearchRequest,
    SearchResult,
    TranslateRequest,
    ExplainRequest,
    ProjectRequest
} from '../types';

export const projectService = {
    async getAll(): Promise<Project[]> {
        return apiClient.get('/projects/');
    },

    async getById(id: string): Promise<Project> {
        return apiClient.get(`/projects/${id}`);
    },

    async create(data: ProjectRequest): Promise<{ message: string; project: Project }> {
        return apiClient.post('/projects/create', data);
    },

    async delete(id: string): Promise<void> {
        return apiClient.delete(`/projects/${id}`);
    },

    async deleteAll(): Promise<void> {
        return apiClient.delete('/projects/');
    },

    async getAssets(id: string): Promise<{ "papers number": number; "summaries number": number }> {
        return apiClient.get(`/projects/${id}/assets`);
    }
};

export const paperService = {
    async getByProject(projectId: string): Promise<Paper[]> {
        return apiClient.get(`/projects/${projectId}/papers/`);
    },

    async getById(projectId: string, paperId: string): Promise<Paper> {
        return apiClient.get(`/projects/${projectId}/papers/${paperId}`);
    },

    async upload(projectId: string, file: File): Promise<{ message: string; paper: Paper; inserted_chunks_count: number }> {
        return apiClient.upload(`/projects/${projectId}/papers/upload-paper`, file);
    },

    async delete(projectId: string, paperId: string): Promise<void> {
        return apiClient.delete(`/projects/${projectId}/papers/${paperId}`);
    },

    async view(projectId: string, paperId: string): Promise<Blob> {
        const response = await fetch(`/projects/${projectId}/papers/view/${paperId}`);
        if (!response.ok) {
            throw new Error('Failed to load paper');
        }
        return response.blob();
    }
};

export const summaryService = {
    async getByProject(projectId: string, paperId: string): Promise<Summary[]> {
        return apiClient.get(`/projects/${projectId}/papers/${paperId}/summaries/`);
    },

    async create(projectId: string, paperId: string): Promise<{ message: string; summary: Summary }> {
        return apiClient.post(`/projects/${projectId}/papers/${paperId}/summaries/create`);
    },

    async getById(projectId: string, paperId: string, summaryId: string): Promise<Summary> {
        return apiClient.get(`/projects/${projectId}/papers/${paperId}/summaries/${summaryId}`);
    },

    async delete(projectId: string, paperId: string, summaryId: string): Promise<void> {
        return apiClient.delete(`/projects/${projectId}/papers/${paperId}/summaries/${summaryId}`);
    },

    async view(projectId: string, paperId: string, summaryId: string): Promise<string> {
        const response = await fetch(`/projects/${projectId}/papers/${paperId}/summaries/view/${summaryId}`);
        if (!response.ok) {
            throw new Error('Failed to load summary');
        }
        return response.text();
    },

    async update(projectId: string, paperId: string, summaryId: string, content: string): Promise<string> {
        const response = await fetch(`/projects/${projectId}/papers/${paperId}/summaries/${summaryId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'text/markdown' },
            body: content
        });
        if (!response.ok) {
            throw new Error('Failed to update summary');
        }
        return response.text();
    }
};

export const ragService = {
    async indexProject(projectId: string, doReset: boolean = false): Promise<{ signal: string; inserted_items_count: number }> {
        return apiClient.post(`/projects/${projectId}/vdb/index/`, { do_reset: doReset ? 1 : 0 });
    },

    async getIndexInfo(projectId: string): Promise<{ signal: string; collection_info: any }> {
        return apiClient.get(`/projects/${projectId}/vdb/info`);
    },

    async search(projectId: string, request: SearchRequest): Promise<{ signal: string; results: SearchResult[] }> {
        return apiClient.post(`/projects/${projectId}/vdb/search`, request);
    },

    async answer(projectId: string, request: SearchRequest): Promise<{ signal: string; answer: string }> {
        return apiClient.post(`/projects/${projectId}/chat/answer`, request);
    }
};

export const translatorService = {
    async translate(request: TranslateRequest): Promise<{ translated_text: string }> {
        return apiClient.post('/translator/translate', request);
    }
};

export const explainerService = {
    async explain(request: ExplainRequest): Promise<{ explanation: string }> {
        return apiClient.post('/explainer/explain', request);
    }
};

export const welcomeService = {
    async getWelcome(): Promise<{ message: string }> {
        return apiClient.get('/');
    }
};

export interface ConfigurationRequest {
    generation_backend: string;
    embedding_backend: string;
    summary_backend: string;
    gemini_api_key: string;
    generation_model_id: string;
    embedding_model_id: string;
    embedding_size: number;
    summary_model_id: string;
}

export interface ConfigurationResponse {
    message: string;
    status: string;
}

export interface ConfigurationStatus {
    generation_backend: string;
    embedding_backend: string;
    summary_backend: string;
    generation_model_id: string;
    embedding_model_id: string;
    embedding_size: number;
    summary_model_id: string;
    gemini_api_key_configured: boolean;
    status: 'configured' | 'not_configured';
}

export const configService = {
    async configure(config: ConfigurationRequest): Promise<ConfigurationResponse> {
        return apiClient.post('/api/config/configure', config);
    },

    async getStatus(): Promise<ConfigurationStatus> {
        return apiClient.get('/api/config/configuration');
    }
};