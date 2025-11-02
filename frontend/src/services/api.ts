// Simple API client without external dependencies
const API_BASE_URL = 'http://localhost:5000';

class ApiClient {
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;

        const defaultHeaders = {
            'Content-Type': 'application/json',
        };

        const config: RequestInit = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({
                    message: `HTTP error! status: ${response.status}`
                }));
                throw new Error(errorData.message || errorData.detail || 'Request failed');
            }

            // Handle different response types
            const contentType = response.headers.get('content-type');
            if (contentType?.includes('application/json')) {
                return await response.json();
            } else if (contentType?.includes('text/')) {
                return await response.text() as T;
            } else {
                return await response.blob() as T;
            }
        } catch (error) {
            console.error(`API request failed: ${config.method} ${url}`, error);
            throw error;
        }
    }

    async get<T>(endpoint: string, options?: RequestInit): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'GET' });
    }

    async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
        return this.request<T>(endpoint, {
            ...options,
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    async postfile<T>(endpoint: string, file: File, options?: RequestInit): Promise<T> {
        const formData = new FormData();
        formData.append('file', file);

        // 🪵 Log all key-value pairs before sending
        // Use FormData.forEach to avoid downlevelIteration/target TS issues
        formData.forEach((value, key) => {
            console.log(key, value);
        });
        return this.request<T>(endpoint, {
            ...options,
            method: 'POST',
            body: formData,
        });
    }

    async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
        return this.request<T>(endpoint, {
            ...options,
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'DELETE' });
    }

    async upload<T>(endpoint: string, file: File, options?: RequestInit): Promise<T> {
        const formData = new FormData();
        formData.append('file', file);

        return this.request<T>(endpoint, {
            ...options,
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData, let browser set it
                ...options?.headers,
                "Content-Type": "multipart/form-data; boundary=<calculated when request is sent>",
            },
        });
    }
}

export const apiClient = new ApiClient();