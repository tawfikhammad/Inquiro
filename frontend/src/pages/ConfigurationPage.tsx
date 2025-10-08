import React from 'react';

// Configuration setup page
interface ConfigurationPageProps { }

interface ConfigForm {
    provider: string;
    generationModelId: string;
    embeddingModelId: string;
    summaryModelId: string;
    geminiApiKey: string;
    embeddingSize: number;
}

const ConfigurationPage: React.FC<ConfigurationPageProps> = () => {
    const [form, setForm] = React.useState<ConfigForm>({
        provider: '',
        generationModelId: '',
        embeddingModelId: '',
        summaryModelId: '',
        geminiApiKey: '',
        embeddingSize: 1024,
    });

    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const providerOptions = [
        { value: '', label: 'Select a Provider' },
        { value: 'gemini', label: 'Google Gemini' }
    ];

    // Gemini model options - only shown when provider is 'gemini'
    const geminiGenerationModels = [
        { value: '', label: 'Select Generation Model' },
        { value: 'gemini-2.0-flash-exp', label: 'Gemini 2.0 Flash (Experimental)' },
        { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
        { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash' },
    ];

    const geminiEmbeddingModels = [
        { value: '', label: 'Select Embedding Model' },
        { value: 'text-embedding-004', label: 'Text Embedding 004' },
        { value: 'text-embedding-003', label: 'Text Embedding 003' },
        { value: 'gemini-embedding-001', label: 'Gemini Embedding 001' }
    ];

    const geminiSummaryModels = [
        { value: '', label: 'Select Summary Model' },
        { value: 'gemini-2.0-flash-exp', label: 'Gemini 2.0 Flash (Experimental)' },
        { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
        { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash' },
    ];

    const handleProviderChange = (provider: string) => {
        setForm(prev => ({
            ...prev,
            provider,
            // Reset model selections when provider changes
            generationModelId: '',
            embeddingModelId: '',
            summaryModelId: '',
            geminiApiKey: ''
        }));
    };

    const handleInputChange = (field: keyof ConfigForm, value: string | number) => {
        setForm(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError(null);

        try {
            // Validate form
            if (!form.provider) {
                throw new Error('Please select a provider');
            }
            if (!form.generationModelId) {
                throw new Error('Please select a generation model');
            }
            if (!form.embeddingModelId) {
                throw new Error('Please select an embedding model');
            }
            if (!form.summaryModelId) {
                throw new Error('Please select a summary model');
            }
            if (form.provider === 'gemini' && !form.geminiApiKey.trim()) {
                throw new Error('Gemini API key is required');
            }

            // Create .env content
            const envContent = `# LLM Configuration
GENERATION_BACKEND="${form.provider}"
EMBEDDING_BACKEND="${form.provider}"
SUMMARY_BACKEND="${form.provider}"

GEMINI_API_KEY="${form.geminiApiKey}"

GENERATION_MODEL_ID="${form.generationModelId}"
EMBEDDING_MODEL_ID="${form.embeddingModelId}"
EMBEDDING_SIZE=${form.embeddingSize}
SUMMARY_MODEL_ID="${form.summaryModelId}"
`;

            // Store configuration
            const config = {
                generationModelId: form.generationModelId,
                embeddingModelId: form.embeddingModelId,
                summaryModelId: form.summaryModelId,
                geminiApiKey: form.geminiApiKey,
                embeddingSize: form.embeddingSize,
                envContent
            };

            // Save to localStorage for persistence
            localStorage.setItem('inquiro-config', JSON.stringify(config));

            // Show the .env content to user
            const blob = new Blob([envContent], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '.env';
            a.click();
            URL.revokeObjectURL(url);

            // Trigger app state update
            window.dispatchEvent(new CustomEvent('config-saved', { detail: config }));

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Configuration failed');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="container">
            <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
                    Welcome to Inquiro
                </h1>
                <p style={{ textAlign: 'center', marginBottom: '30px', color: '#666' }}>
                    Configure your AI models and API settings to get started
                </p>

                {error && <div className="error">{error}</div>}

                <form onSubmit={handleSubmit}>
                    {/* Provider Selection */}
                    <div className="form-group">
                        <label className="form-label">AI Provider</label>
                        <select
                            className="form-control"
                            value={form.provider}
                            onChange={(e) => handleProviderChange(e.target.value)}
                            required
                        >
                            {providerOptions.map(option => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                        <small style={{ color: '#666', fontSize: '12px' }}>
                            Currently only Google Gemini is supported
                        </small>
                    </div>

                    {/* Show Gemini-specific fields only when Gemini is selected */}
                    {form.provider === 'gemini' && (
                        <>
                            <div className="form-group">
                                <label className="form-label">Gemini API Key</label>
                                <input
                                    type="password"
                                    className="form-control"
                                    value={form.geminiApiKey}
                                    onChange={(e) => handleInputChange('geminiApiKey', e.target.value)}
                                    placeholder="Enter your Gemini API key"
                                    required
                                />
                                <small style={{ color: '#666', fontSize: '12px' }}>
                                    Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
                                </small>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Generation Model</label>
                                <select
                                    className="form-control"
                                    value={form.generationModelId}
                                    onChange={(e) => handleInputChange('generationModelId', e.target.value)}
                                    required
                                >
                                    {geminiGenerationModels.map(option => (
                                        <option key={option.value} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                                <small style={{ color: '#666', fontSize: '12px' }}>
                                    Model used for text generation and chat responses
                                </small>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Embedding Model</label>
                                <select
                                    className="form-control"
                                    value={form.embeddingModelId}
                                    onChange={(e) => handleInputChange('embeddingModelId', e.target.value)}
                                    required
                                >
                                    {geminiEmbeddingModels.map(option => (
                                        <option key={option.value} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                                <small style={{ color: '#666', fontSize: '12px' }}>
                                    Model used for document embeddings and semantic search
                                </small>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Summary Model</label>
                                <select
                                    className="form-control"
                                    value={form.summaryModelId}
                                    onChange={(e) => handleInputChange('summaryModelId', e.target.value)}
                                    required
                                >
                                    {geminiSummaryModels.map(option => (
                                        <option key={option.value} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                                <small style={{ color: '#666', fontSize: '12px' }}>
                                    Model used for document summarization
                                </small>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Embedding Size</label>
                                <select
                                    className="form-control"
                                    value={form.embeddingSize}
                                    onChange={(e) => handleInputChange('embeddingSize', parseInt(e.target.value))}
                                >
                                    <option value={768}>768 dimensions</option>
                                    <option value={1024}>1024 dimensions</option>
                                </select>
                                <small style={{ color: '#666', fontSize: '12px' }}>
                                    Vector dimension size for embeddings
                                </small>
                            </div>
                        </>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={isSubmitting || !form.provider}
                        style={{ width: '100%', marginTop: '20px' }}
                    >
                        {isSubmitting ? 'Saving...' : 'Save Configuration & Continue'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ConfigurationPage;