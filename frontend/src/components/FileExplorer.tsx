import React from 'react';
import { paperService, summaryService } from '../services';

interface Paper {
    _id: string;
    paper_name: string;
    paper_type: string;
    paper_size: number;
    created_at?: string;
}

interface Summary {
    _id: string;
    summary_name: string;
    summary_paper_id: string;
    summary_type: string;
    summary_size: number;
    created_at?: string;
}

interface FileExplorerProps {
    projectId: string;
    onFileSelect: (type: 'paper' | 'summary', content: any) => void;
}

const FileExplorer: React.FC<FileExplorerProps> = ({ projectId, onFileSelect }) => {
    const [papers, setPapers] = React.useState<Paper[]>([]);
    const [summaries, setSummaries] = React.useState<Summary[]>([]);
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [uploadStatus, setUploadStatus] = React.useState<{
        isUploading: boolean;
        progress: number;
        filename: string;
    } | null>(null);
    const [selectedPaper, setSelectedPaper] = React.useState<string | null>(null);
    const [expandedSections, setExpandedSections] = React.useState<{ [key: string]: boolean }>({
        papers: true,
        summaries: true
    });

    const fileInputRef = React.useRef<HTMLInputElement>(null);

    React.useEffect(() => {
        loadFiles();
    }, [projectId]); // Removed loadFiles dependency to avoid infinite loops

    const loadFiles = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Load papers
            const papersData = await paperService.getByProject(projectId);
            setPapers(papersData);

            // Load summaries for all papers
            const allSummaries: Summary[] = [];
            for (const paper of papersData) {
                try {
                    const paperSummaries = await summaryService.getByProject(projectId, paper._id);
                    allSummaries.push(...paperSummaries);
                } catch (err) {
                    // It's okay if there are no summaries for a paper
                    console.log(`No summaries found for paper ${paper._id}`);
                }
            }
            setSummaries(allSummaries);
        } catch (err: any) {
            setError(err.message || 'Failed to load files');
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            setError('Only PDF files are supported');
            return;
        }

        // Validate file size (50MB limit)
        if (file.size > 50 * 1024 * 1024) {
            setError('File size must be less than 50MB');
            return;
        }

        setUploadStatus({
            isUploading: true,
            progress: 0,
            filename: file.name
        });
        setError(null);

        try {
            await paperService.upload(projectId, file);
            await loadFiles(); // Reload files
            setUploadStatus(null);
        } catch (err: any) {
            setError(err.message || 'Upload failed');
            setUploadStatus(null);
        }

        // Reset file input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleDeletePaper = async (paperId: string, paperName: string) => {
        if (!window.confirm(`Are you sure you want to delete "${paperName}"?`)) {
            return;
        }

        try {
            await paperService.delete(projectId, paperId);
            await loadFiles();
        } catch (err: any) {
            setError(err.message || 'Failed to delete paper');
        }
    };

    const handleCreateSummary = async (paperId: string) => {
        setIsLoading(true);
        try {
            await summaryService.create(projectId, paperId);
            await loadFiles();
        } catch (err: any) {
            setError(err.message || 'Failed to create summary');
        } finally {
            setIsLoading(false);
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const toggleSection = (section: string) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    return (
        <div style={{ padding: '20px', height: '100%', overflow: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ margin: 0 }}>Library</h3>
                <button
                    className="btn btn-primary"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploadStatus?.isUploading}
                >
                    + Upload PDF
                </button>
            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
            />

            {error && <div className="error" style={{ marginBottom: '15px' }}>{error}</div>}

            {uploadStatus?.isUploading && (
                <div className="card" style={{ marginBottom: '15px', padding: '10px' }}>
                    <div style={{ fontSize: '14px', marginBottom: '5px' }}>
                        Uploading: {uploadStatus.filename}
                    </div>
                    <div style={{
                        width: '100%',
                        height: '8px',
                        backgroundColor: '#e0e0e0',
                        borderRadius: '4px',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            width: '50%', // Placeholder progress
                            height: '100%',
                            backgroundColor: '#007bff',
                            transition: 'width 0.3s ease'
                        }} />
                    </div>
                </div>
            )}

            {/* Papers Section */}
            <div className="card" style={{ marginBottom: '15px' }}>
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        cursor: 'pointer',
                        padding: '10px 0'
                    }}
                    onClick={() => toggleSection('papers')}
                >
                    <h4 style={{ margin: 0 }}>
                        {expandedSections.papers ? '📂' : '📁'} Papers ({papers.length})
                    </h4>
                </div>

                {expandedSections.papers && (
                    <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                        {papers.length === 0 ? (
                            <p style={{ color: '#666', fontStyle: 'italic', margin: '10px 0' }}>
                                No papers uploaded yet
                            </p>
                        ) : (
                            papers.map((paper) => (
                                <div
                                    key={paper._id}
                                    style={{
                                        padding: '10px',
                                        border: '1px solid #e0e0e0',
                                        borderRadius: '4px',
                                        marginBottom: '8px',
                                        cursor: 'pointer',
                                        backgroundColor: selectedPaper === paper._id ? '#f0f7ff' : 'white'
                                    }}
                                    onClick={() => {
                                        setSelectedPaper(paper._id);
                                        onFileSelect('paper', paper);
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ flex: 1, minWidth: 0 }}>
                                            <div style={{
                                                fontWeight: '500',
                                                fontSize: '14px',
                                                wordBreak: 'break-word',
                                                marginBottom: '4px'
                                            }}>
                                                📄 {paper.paper_name}
                                            </div>
                                            <div style={{ fontSize: '12px', color: '#666' }}>
                                                {formatFileSize(paper.paper_size)}
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: '5px', marginLeft: '10px' }}>
                                            <button
                                                className="btn btn-secondary"
                                                style={{ fontSize: '12px', padding: '4px 8px' }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleCreateSummary(paper._id);
                                                }}
                                                disabled={isLoading}
                                            >
                                                📋
                                            </button>
                                            <button
                                                className="btn btn-danger"
                                                style={{ fontSize: '12px', padding: '4px 8px' }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDeletePaper(paper._id, paper.paper_name);
                                                }}
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            {/* Summaries Section */}
            <div className="card">
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        cursor: 'pointer',
                        padding: '10px 0'
                    }}
                    onClick={() => toggleSection('summaries')}
                >
                    <h4 style={{ margin: 0 }}>
                        {expandedSections.summaries ? '📂' : '📁'} Summaries ({summaries.length})
                    </h4>
                </div>

                {expandedSections.summaries && (
                    <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                        {summaries.length === 0 ? (
                            <p style={{ color: '#666', fontStyle: 'italic', margin: '10px 0' }}>
                                No summaries created yet
                            </p>
                        ) : (
                            summaries.map((summary) => (
                                <div
                                    key={summary._id}
                                    style={{
                                        padding: '10px',
                                        border: '1px solid #e0e0e0',
                                        borderRadius: '4px',
                                        marginBottom: '8px',
                                        cursor: 'pointer',
                                        backgroundColor: 'white'
                                    }}
                                    onClick={() => onFileSelect('summary', summary)}
                                >
                                    <div style={{
                                        fontWeight: '500',
                                        fontSize: '14px',
                                        wordBreak: 'break-word',
                                        marginBottom: '4px'
                                    }}>
                                        📋 {summary.summary_name}
                                    </div>
                                    <div style={{ fontSize: '12px', color: '#666' }}>
                                        {formatFileSize(summary.summary_size)}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            {isLoading && (
                <div className="loading" style={{ margin: '20px 0' }}>
                    Loading...
                </div>
            )}
        </div>
    );
};

export default FileExplorer;