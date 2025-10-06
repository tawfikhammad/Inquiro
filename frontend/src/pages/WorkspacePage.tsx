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
                <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
                    Select Workspace
                </h1>

                {error && <div className="error">{error}</div>}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2>Your Projects</h2>
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowCreateForm(true)}
                        disabled={isLoading}
                    >
                        + New Project
                    </button>
                </div>

                {showCreateForm && (
                    <div className="card" style={{ marginBottom: '20px', backgroundColor: '#f8f9fa' }}>
                        <h3>Create New Project</h3>
                        <form onSubmit={handleCreateProject}>
                            <div className="form-group">
                                <label className="form-label">Project Name</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    value={newProjectTitle}
                                    onChange={(e) => setNewProjectTitle(e.target.value)}
                                    placeholder="Enter project name"
                                    required
                                    autoFocus
                                />
                            </div>
                            <div style={{ display: 'flex', gap: '10px' }}>
                                <button type="submit" className="btn btn-primary" disabled={isLoading}>
                                    {isLoading ? 'Creating...' : 'Create Project'}
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => {
                                        setShowCreateForm(false);
                                        setNewProjectTitle('');
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
                    <div className="loading">Loading projects...</div>
                ) : projects.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                        <p>No projects found. Create your first project to get started!</p>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gap: '15px' }}>
                        {projects.map((project) => (
                            <div
                                key={project._id}
                                className="card"
                                style={{
                                    padding: '15px',
                                    border: '1px solid #ddd',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    backgroundColor: '#fff'
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                                    e.currentTarget.style.transform = 'translateY(-2px)';
                                    e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.backgroundColor = '#fff';
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div
                                        style={{ flex: 1 }}
                                        onClick={() => onProjectSelect(project)}
                                    >
                                        <h3 style={{ margin: '0 0 5px 0', color: '#333' }}>
                                            {project.project_title}
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
                                        style={{ marginLeft: '10px' }}
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default WorkspacePage;