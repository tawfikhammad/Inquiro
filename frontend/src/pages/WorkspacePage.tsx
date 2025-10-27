import React from 'react';
import { projectService } from '../services';

interface Project {
    _id: string;
    project_title: string;
    created_at?: string;
    updated_at?: string;
}

interface WorkspacePageProps {
    onProjectSelect: (project: Project) => void;
}

const WorkspacePage: React.FC<WorkspacePageProps> = ({ onProjectSelect }) => {
    const [projects, setProjects] = React.useState<Project[]>([]);
    const [showCreateForm, setShowCreateForm] = React.useState(false);
    const [newProjectTitle, setNewProjectTitle] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    // Load projects on component mount
    React.useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const projectsData = await projectService.getAll();
            setProjects(projectsData);
        } catch (err: any) {
            if (err.message.includes('404')) {
                // No projects exist yet
                setProjects([]);
            } else {
                setError(err.message || 'Failed to load projects');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateProject = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newProjectTitle.trim()) return;

        setIsLoading(true);
        setError(null);
        try {
            const result = await projectService.create({ project_title: newProjectTitle.trim() });
            setProjects(prev => [...prev, result.project]);
            setNewProjectTitle('');
            setShowCreateForm(false);
        } catch (err: any) {
            setError(err.message || 'Failed to create project');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteProject = async (projectId: string) => {
        if (!window.confirm('Are you sure you want to delete this project? This will delete all papers and data associated with it.')) {
            return;
        }

        setIsLoading(true);
        try {
            await projectService.delete(projectId);
            setProjects(prev => prev.filter(p => p._id !== projectId));
        } catch (err: any) {
            setError(err.message || 'Failed to delete project');
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return 'Unknown';
        return new Date(dateString).toLocaleDateString();
    };

    return (
        <div className="container">
            <div className="card">
                <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                    <h1 style={{ margin: '0 0 10px 0', color: '#333' }}>
                        Welcome to Inquiro
                    </h1>
                    <p style={{ color: '#666', fontSize: '16px', margin: 0 }}>
                        Select an existing workspace or create a new one to get started
                    </p>
                </div>

                {error && <div className="error">{error}</div>}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2 style={{ margin: 0 }}>Your Workspaces</h2>
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowCreateForm(true)}
                        disabled={isLoading || showCreateForm}
                    >
                        + Create New Workspace
                    </button>
                </div>

                {showCreateForm && (
                    <div className="card" style={{ marginBottom: '20px', backgroundColor: '#f8f9fa', border: '2px solid #007bff' }}>
                        <h3 style={{ marginTop: 0 }}>Create New Workspace</h3>
                        <form onSubmit={handleCreateProject}>
                            <div className="form-group">
                                <label className="form-label">Workspace Name</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    value={newProjectTitle}
                                    onChange={(e) => setNewProjectTitle(e.target.value)}
                                    placeholder="e.g., Machine Learning Research, PhD Thesis, etc."
                                    required
                                    autoFocus
                                />
                                <small style={{ color: '#666', fontSize: '12px' }}>
                                    Give your workspace a descriptive name to organize your papers and research
                                </small>
                            </div>
                            <div style={{ display: 'flex', gap: '10px' }}>
                                <button type="submit" className="btn btn-primary" disabled={isLoading}>
                                    {isLoading ? 'Creating...' : 'Create Workspace'}
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => {
                                        setShowCreateForm(false);
                                        setNewProjectTitle('');
                                        setError(null);
                                    }}
                                    disabled={isLoading}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {isLoading && projects.length === 0 ? (
                    <div className="loading">Loading workspaces...</div>
                ) : projects.length === 0 && !showCreateForm ? (
                    <div style={{
                        textAlign: 'center',
                        padding: '60px 40px',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '8px',
                        border: '2px dashed #ddd'
                    }}>
                        <h3 style={{ color: '#333', marginBottom: '10px' }}>No Workspaces Yet</h3>
                        <p style={{ color: '#666', marginBottom: '20px' }}>
                            Create your first workspace to start organizing and analyzing research papers
                        </p>
                        <button
                            className="btn btn-primary"
                            onClick={() => setShowCreateForm(true)}
                            style={{ fontSize: '16px', padding: '10px 30px' }}
                        >
                            + Create Your First Workspace
                        </button>
                    </div>
                ) : projects.length > 0 ? (
                    <div style={{ display: 'grid', gap: '15px' }}>
                        {projects.map((project) => (
                            <div
                                key={project._id}
                                className="card"
                                style={{
                                    padding: '20px',
                                    border: '2px solid #ddd',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    backgroundColor: '#fff'
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                                    e.currentTarget.style.transform = 'translateY(-2px)';
                                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                                    e.currentTarget.style.borderColor = '#007bff';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.backgroundColor = '#fff';
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                                    e.currentTarget.style.borderColor = '#ddd';
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div
                                        style={{ flex: 1 }}
                                        onClick={() => onProjectSelect(project)}
                                    >
                                        <h3 style={{ margin: '0 0 8px 0', color: '#333', fontSize: '20px' }}>
                                            📁 {project.project_title}
                                        </h3>
                                        <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                                            Created: {formatDate(project.created_at)}
                                        </p>
                                    </div>
                                    <button
                                        className="btn btn-danger"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDeleteProject(project._id);
                                        }}
                                        disabled={isLoading}
                                        style={{ marginLeft: '15px' }}
                                        title="Delete this workspace"
                                    >
                                        🗑️ Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : null}
            </div>
        </div>
    );
};

export default WorkspacePage;