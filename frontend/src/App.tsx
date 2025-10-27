import React from 'react';
import WorkspacePage from './pages/WorkspacePage';
import FileExplorer from './components/FileExplorer';
import ContentViewer from './components/ContentViewer';
import ChatInterface from './components/ChatInterface';
import { ragService, translatorService, explainerService } from './services';

interface Project {
    _id: string;
    project_title: string;
    created_at?: string;
    updated_at?: string;
}

type AppState = 'workspace' | 'dashboard';

const App: React.FC = () => {
    const [currentState, setCurrentState] = React.useState<AppState>('workspace');
    const [currentProject, setCurrentProject] = React.useState<Project | null>(null);

    const handleProjectSelect = (project: Project) => {
        setCurrentProject(project);
        setCurrentState('dashboard');
    };

    const handleBackToWorkspace = () => {
        setCurrentProject(null);
        setCurrentState('workspace');
    };

    // Enhanced Dashboard with proper component integration
    const EnhancedDashboard: React.FC<{ project: Project; onBackToWorkspace: () => void }> = ({
        project,
        onBackToWorkspace
    }) => {
        const [isIndexed, setIsIndexed] = React.useState(false);
        const [indexInfo, setIndexInfo] = React.useState<any>(null);
        const [currentView, setCurrentView] = React.useState<'paper' | 'summary' | null>(null);
        const [currentContent, setCurrentContent] = React.useState<any>(null);
        const [selectedText, setSelectedText] = React.useState<string>('');
        const [showTranslateModal, setShowTranslateModal] = React.useState(false);
        const [showExplainModal, setShowExplainModal] = React.useState(false);

        // Check if project is indexed on mount
        React.useEffect(() => {
            checkIndexStatus();
        }, [project._id]);

        const checkIndexStatus = async () => {
            try {
                const response = await ragService.getIndexInfo(project._id);
                setIndexInfo(response.collection_info);
                setIsIndexed(true);
            } catch (err) {
                setIsIndexed(false);
            }
        };

        const handleIndexProject = async () => {
            try {
                await ragService.indexProject(project._id, false);
                await checkIndexStatus();
            } catch (err) {
                console.error('Failed to index project:', err);
            }
        };

        const handleTextSelection = () => {
            const selection = window.getSelection();
            if (selection && selection.toString().trim()) {
                setSelectedText(selection.toString().trim());
            }
        };

        return (
            <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
                {/* Header */}
                <div style={{
                    background: 'white',
                    padding: '15px 20px',
                    borderBottom: '1px solid #ddd',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                        <button
                            className="btn btn-secondary"
                            onClick={onBackToWorkspace}
                        >
                            ← Back to Workspaces
                        </button>
                        <h1 style={{ margin: 0, color: '#333' }}>{project.project_title}</h1>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {isIndexed ? (
                            <span style={{ color: '#28a745', fontSize: '14px' }}>
                                ✓ Indexed ({indexInfo?.vectors_count || 0} vectors)
                            </span>
                        ) : (
                            <button
                                className="btn btn-primary"
                                onClick={handleIndexProject}
                            >
                                Index Project for Chat
                            </button>
                        )}

                        {selectedText && (
                            <div style={{ display: 'flex', gap: '5px' }}>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => setShowTranslateModal(true)}
                                    title="Translate selected text"
                                >
                                    Translate
                                </button>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => setShowExplainModal(true)}
                                    title="Explain selected text"
                                >
                                    Explain
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Main Layout */}
                <div className="layout" style={{ height: 'calc(100vh - 80px)' }}>
                    {/* Left Sidebar - File Explorer */}
                    <div className="sidebar">
                        <FileExplorer
                            projectId={project._id}
                            onFileSelect={(type, content) => {
                                setCurrentView(type);
                                setCurrentContent(content);
                            }}
                        />
                    </div>

                    {/* Middle Panel - Content Viewer */}
                    <div className="main-content" onMouseUp={handleTextSelection}>
                        <ContentViewer
                            viewType={currentView}
                            content={currentContent}
                            projectId={project._id}
                        />
                    </div>

                    {/* Right Panel - Chat */}
                    <div className="chat-panel">
                        <ChatInterface
                            projectId={project._id}
                            isIndexed={isIndexed}
                        />
                    </div>
                </div>

                {/* Modals */}
                {showTranslateModal && (
                    <TranslateModal
                        text={selectedText}
                        onClose={() => setShowTranslateModal(false)}
                    />
                )}

                {showExplainModal && (
                    <ExplainModal
                        text={selectedText}
                        context={currentContent?.paper_name || ''}
                        onClose={() => setShowExplainModal(false)}
                    />
                )}
            </div>
        );
    };

    // Translation Modal Component
    const TranslateModal: React.FC<{ text: string; onClose: () => void }> = ({ text, onClose }) => {
        const [targetLanguage, setTargetLanguage] = React.useState('Spanish');
        const [translatedText, setTranslatedText] = React.useState('');
        const [isLoading, setIsLoading] = React.useState(false);
        const [error, setError] = React.useState<string | null>(null);

        const languages = ['Spanish', 'French', 'German', 'Arabic', 'Italian', 'English'];

        const handleTranslate = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await translatorService.translate({
                    text: text,
                    target_language: targetLanguage
                });
                setTranslatedText(response.translated_text);
            } catch (err: any) {
                setError(err.message || 'Translation failed');
            } finally {
                setIsLoading(false);
            }
        };

        return (
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0,0,0,0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
            }}>
                <div className="card" style={{ maxWidth: '600px', width: '90%', maxHeight: '80vh', overflow: 'auto' }}>
                    <h3>Translate Text</h3>

                    <div className="form-group">
                        <label className="form-label">Original Text:</label>
                        <div style={{
                            padding: '10px',
                            border: '1px solid #ddd',
                            borderRadius: '4px',
                            backgroundColor: '#f8f9fa',
                            maxHeight: '100px',
                            overflow: 'auto'
                        }}>
                            {text}
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Target Language:</label>
                        <select
                            className="form-control"
                            value={targetLanguage}
                            onChange={(e) => setTargetLanguage(e.target.value)}
                        >
                            {languages.map(lang => (
                                <option key={lang} value={lang}>{lang}</option>
                            ))}
                        </select>
                    </div>

                    {error && <div className="error">{error}</div>}

                    {translatedText && (
                        <div className="form-group">
                            <label className="form-label">Translation:</label>
                            <div style={{
                                padding: '10px',
                                border: '1px solid #ddd',
                                borderRadius: '4px',
                                backgroundColor: '#f8f9fa',
                                maxHeight: '150px',
                                overflow: 'auto'
                            }}>
                                {translatedText}
                            </div>
                        </div>
                    )}

                    <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                        <button
                            className="btn btn-primary"
                            onClick={handleTranslate}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Translating...' : 'Translate'}
                        </button>
                        <button className="btn btn-secondary" onClick={onClose}>
                            Close
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    // Explanation Modal Component
    const ExplainModal: React.FC<{ text: string; context: string; onClose: () => void }> = ({
        text,
        context,
        onClose
    }) => {
        const [explanation, setExplanation] = React.useState('');
        const [isLoading, setIsLoading] = React.useState(false);
        const [error, setError] = React.useState<string | null>(null);

        React.useEffect(() => {
            handleExplain();
        }, []);

        const handleExplain = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await explainerService.explain({
                    text: text,
                    context: context
                });
                setExplanation(response.explanation);
            } catch (err: any) {
                setError(err.message || 'Explanation failed');
            } finally {
                setIsLoading(false);
            }
        };

        return (
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0,0,0,0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
            }}>
                <div className="card" style={{ maxWidth: '700px', width: '90%', maxHeight: '80vh', overflow: 'auto' }}>
                    <h3>Explain Text</h3>

                    <div className="form-group">
                        <label className="form-label">Selected Text:</label>
                        <div style={{
                            padding: '10px',
                            border: '1px solid #ddd',
                            borderRadius: '4px',
                            backgroundColor: '#f8f9fa',
                            maxHeight: '100px',
                            overflow: 'auto'
                        }}>
                            {text}
                        </div>
                    </div>

                    {context && (
                        <div className="form-group">
                            <label className="form-label">Context:</label>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                                From: {context}
                            </div>
                        </div>
                    )}

                    {error && <div className="error">{error}</div>}

                    {isLoading ? (
                        <div className="loading">Generating explanation...</div>
                    ) : explanation ? (
                        <div className="form-group">
                            <label className="form-label">Explanation:</label>
                            <div style={{
                                padding: '15px',
                                border: '1px solid #ddd',
                                borderRadius: '4px',
                                backgroundColor: '#f8f9fa',
                                maxHeight: '300px',
                                overflow: 'auto',
                                lineHeight: '1.6'
                            }}>
                                {explanation}
                            </div>
                        </div>
                    ) : null}

                    <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                        <button className="btn btn-secondary" onClick={onClose}>
                            Close
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    // Render appropriate component based on current state
    switch (currentState) {
        case 'workspace':
            return <WorkspacePage onProjectSelect={handleProjectSelect} />;

        case 'dashboard':
            return currentProject ? (
                <EnhancedDashboard
                    project={currentProject}
                    onBackToWorkspace={handleBackToWorkspace}
                />
            ) : (
                <WorkspacePage onProjectSelect={handleProjectSelect} />
            );

        default:
            return <WorkspacePage onProjectSelect={handleProjectSelect} />;
    }
};

export default App;