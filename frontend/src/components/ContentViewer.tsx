import React from 'react';
import { paperService, summaryService } from '../services';

interface Paper {
    _id: string;
    paper_name: string;
    paper_type: string;
    paper_size: number;
}

interface Summary {
    _id: string;
    summary_name: string;
    summary_paper_id: string;
    summary_type: string;
}

interface ContentViewerProps {
    viewType: 'paper' | 'summary' | null;
    content: Paper | Summary | null;
    projectId: string;
}

const ContentViewer: React.FC<ContentViewerProps> = ({ viewType, content, projectId }) => {
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [pdfUrl, setPdfUrl] = React.useState<string | null>(null);
    const [summaryContent, setSummaryContent] = React.useState<string>('');
    const [isEditing, setIsEditing] = React.useState(false);
    const [editContent, setEditContent] = React.useState<string>('');

    React.useEffect(() => {
        if (content && viewType) {
            loadContent();
        } else {
            setPdfUrl(null);
            setSummaryContent('');
        }
    }, [content, viewType, projectId]); // Removed loadContent dependency to avoid infinite loops

    const loadContent = async () => {
        if (!content || !viewType) return;

        setIsLoading(true);
        setError(null);

        try {
            if (viewType === 'paper') {
                // Load PDF
                const blob = await paperService.view(projectId, content._id);
                const url = URL.createObjectURL(blob);
                setPdfUrl(url);
            } else if (viewType === 'summary') {
                // Load summary content
                const summary = content as Summary;
                const text = await summaryService.view(projectId, summary.summary_paper_id, content._id);
                setSummaryContent(text);
                setEditContent(text);
            }
        } catch (err: any) {
            setError(err.message || 'Failed to load content');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveSummary = async () => {
        if (!content || viewType !== 'summary') return;

        setIsLoading(true);
        setError(null);

        try {
            const summary = content as Summary;
            await summaryService.update(projectId, summary.summary_paper_id, content._id, editContent);
            setSummaryContent(editContent);
            setIsEditing(false);
        } catch (err: any) {
            setError(err.message || 'Failed to save summary');
        } finally {
            setIsLoading(false);
        }
    };

    const renderMarkdown = (text: string) => {
        // Simple markdown rendering - in a real app, use a proper markdown library
        return text
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            .replace(/\n/gim, '<br>');
    };

    // Cleanup PDF URL when component unmounts
    React.useEffect(() => {
        return () => {
            if (pdfUrl) {
                URL.revokeObjectURL(pdfUrl);
            }
        };
    }, [pdfUrl]);

    if (!content || !viewType) {
        return (
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: '#666',
                fontSize: '18px'
            }}>
                Select a file to view its content
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="loading" style={{ height: '100%' }}>
                Loading content...
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '20px' }}>
                <div className="error">{error}</div>
                <button
                    className="btn btn-primary"
                    onClick={loadContent}
                    style={{ marginTop: '10px' }}
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <div style={{
                padding: '15px 20px',
                borderBottom: '1px solid #ddd',
                backgroundColor: '#f8f9fa',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div>
                    <h3 style={{ margin: 0, color: '#333' }}>
                        {viewType === 'paper' ? '📄' : '📋'} {(content as any).paper_name || (content as any).summary_name}
                    </h3>
                    <p style={{ margin: '5px 0 0 0', color: '#666', fontSize: '14px' }}>
                        {viewType === 'paper' ? 'PDF Document' : 'Summary Document'}
                    </p>
                </div>

                {viewType === 'summary' && (
                    <div style={{ display: 'flex', gap: '10px' }}>
                        {isEditing ? (
                            <>
                                <button
                                    className="btn btn-primary"
                                    onClick={handleSaveSummary}
                                    disabled={isLoading}
                                >
                                    Save
                                </button>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => {
                                        setIsEditing(false);
                                        setEditContent(summaryContent);
                                    }}
                                    disabled={isLoading}
                                >
                                    Cancel
                                </button>
                            </>
                        ) : (
                            <button
                                className="btn btn-secondary"
                                onClick={() => setIsEditing(true)}
                            >
                                Edit
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflow: 'auto' }}>
                {viewType === 'paper' && pdfUrl ? (
                    <iframe
                        src={pdfUrl}
                        style={{
                            width: '100%',
                            height: '100%',
                            border: 'none'
                        }}
                        title="PDF Viewer"
                    />
                ) : viewType === 'summary' ? (
                    <div style={{ padding: '20px' }}>
                        {isEditing ? (
                            <textarea
                                value={editContent}
                                onChange={(e) => setEditContent(e.target.value)}
                                style={{
                                    width: '100%',
                                    height: 'calc(100vh - 200px)',
                                    border: '1px solid #ddd',
                                    borderRadius: '4px',
                                    padding: '15px',
                                    fontSize: '14px',
                                    fontFamily: 'monospace',
                                    resize: 'none',
                                    outline: 'none'
                                }}
                                placeholder="Write your summary in Markdown format..."
                            />
                        ) : (
                            <div
                                style={{
                                    lineHeight: '1.6',
                                    color: '#333',
                                    maxWidth: 'none'
                                }}
                                dangerouslySetInnerHTML={{
                                    __html: renderMarkdown(summaryContent)
                                }}
                            />
                        )}
                    </div>
                ) : (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '100%',
                        color: '#666'
                    }}>
                        Content not available
                    </div>
                )}
            </div>
        </div>
    );
};

export default ContentViewer;