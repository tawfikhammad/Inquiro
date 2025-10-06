import React from 'react';

// Configuration setup page
interface ConfigurationPageProps { }

interface ConfigForm {
    generationModel: string;
    embeddingModel: string;
    geminiApiKey: string;
    temperature: number;
    maxTokens: number;
}

const ConfigurationPage: React.FC<ConfigurationPageProps> = () => {
    const [form, setForm] = React.useState<ConfigForm>({
        generationModel: 'gemini-pro',
        embeddingModel: 'text-embedding-004',
        geminiApiKey: '',
        temperature: 0.7,
        maxTokens: 2048
    });

    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const modelOptions = [
        { value: 'gemini-pro', label: 'Gemini Pro' },
        { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
        { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash' }
    ];

    const embeddingOptions = [
        { value: 'text-embedding-004', label: 'Text Embedding 004' },
        { value: 'embedding-001', label: 'Embedding 001' }
    ];

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
            if (!form.geminiApiKey.trim()) {
                throw new Error('Gemini API key is required');
            }

            if (form.temperature < 0 || form.temperature > 2) {
                throw new Error('Temperature must be between 0 and 2');
            }

            if (form.maxTokens < 1 || form.maxTokens > 8192) {
                throw new Error('Max tokens must be between 1 and 8192');
            }

            // Store configuration
            const config = {
                generationModel: form.generationModel,
                embeddingModel: form.embeddingModel,
                geminiApiKey: form.geminiApiKey,
                temperature: form.temperature,
                maxTokens: form.maxTokens
            };

            // Save to localStorage for persistence
            localStorage.setItem('inquiro-config', JSON.stringify(config));

            // Trigger app state update - this will be implemented with proper state management
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
                    <div className="form-group">
                        <label className="form-label">Generation Model</label>
                        <select
                            className="form-control"
                            value={form.generationModel}
                            onChange={(e) => handleInputChange('generationModel', e.target.value)}
                        >
                            {modelOptions.map(option => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Embedding Model</label>
                        <select
                            className="form-control"
                            value={form.embeddingModel}
                            onChange={(e) => handleInputChange('embeddingModel', e.target.value)}
                        >
                            {embeddingOptions.map(option => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>

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
                        <label className="form-label">Temperature ({form.temperature})</label>
                        <input
                            type="range"
                            min="0"
                            max="2"
                            step="0.1"
                            className="form-control"
                            value={form.temperature}
                            onChange={(e) => handleInputChange('temperature', parseFloat(e.target.value))}
                        />
                        <small style={{ color: '#666', fontSize: '12px' }}>
                            Controls randomness: 0 = deterministic, 2 = very creative
                        </small>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Max Tokens</label>
                        <input
                            type="number"
                            min="1"
                            max="8192"
                            className="form-control"
                            value={form.maxTokens}
                            onChange={(e) => handleInputChange('maxTokens', parseInt(e.target.value))}
                        />
                        <small style={{ color: '#666', fontSize: '12px' }}>
                            Maximum number of tokens in the response
                        </small>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={isSubmitting}
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