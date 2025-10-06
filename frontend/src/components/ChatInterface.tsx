import React from 'react';
import { ragService } from '../services';

interface ChatMessage {
    id: string;
    type: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface ChatInterfaceProps {
    projectId: string;
    isIndexed: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ projectId, isIndexed }) => {
    const [messages, setMessages] = React.useState<ChatMessage[]>([]);
    const [inputMessage, setInputMessage] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const messagesEndRef = React.useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    React.useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Add welcome message when component mounts
    React.useEffect(() => {
        if (isIndexed && messages.length === 0) {
            const welcomeMessage: ChatMessage = {
                id: 'welcome',
                type: 'assistant',
                content: `Hello! I'm your research assistant. I can help you ask questions about the papers in your "${projectId}" project. What would you like to know?`,
                timestamp: new Date()
            };
            setMessages([welcomeMessage]);
        }
    }, [isIndexed, projectId]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!inputMessage.trim() || isLoading) return;
        if (!isIndexed) {
            setError('Please index the project first before asking questions.');
            return;
        }

        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'user',
            content: inputMessage.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await ragService.answer(projectId, {
                query: userMessage.content,
                limit: 5,
                RAGFusion: false
            });

            const assistantMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                type: 'assistant',
                content: response.answer,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (err: any) {
            setError(err.message || 'Failed to send message');
            // Add error message to chat
            const errorMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                type: 'assistant',
                content: 'Sorry, I encountered an error while processing your question. Please try again.',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleClearChat = () => {
        setMessages([]);
        setError(null);
    };

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

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
                <h3 style={{ margin: 0, color: '#333' }}>💬 Research Chat</h3>
                <button
                    className="btn btn-secondary"
                    onClick={handleClearChat}
                    style={{ fontSize: '12px', padding: '5px 10px' }}
                >
                    Clear
                </button>
            </div>

            {/* Status */}
            <div style={{ padding: '10px 15px', backgroundColor: isIndexed ? '#d4edda' : '#f8d7da', fontSize: '12px' }}>
                {isIndexed ? (
                    <span style={{ color: '#155724' }}>✓ Ready to answer questions about your papers</span>
                ) : (
                    <span style={{ color: '#721c24' }}>⚠ Project needs to be indexed before asking questions</span>
                )}
            </div>

            {/* Messages */}
            <div style={{
                flex: 1,
                overflow: 'auto',
                padding: '15px',
                display: 'flex',
                flexDirection: 'column',
                gap: '15px'
            }}>
                {messages.length === 0 && !isIndexed && (
                    <div style={{
                        textAlign: 'center',
                        color: '#666',
                        fontSize: '14px',
                        padding: '20px'
                    }}>
                        Index your project to start asking questions about your papers.
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: message.type === 'user' ? 'flex-end' : 'flex-start'
                        }}
                    >
                        <div style={{
                            maxWidth: '85%',
                            padding: '10px 15px',
                            borderRadius: '18px',
                            backgroundColor: message.type === 'user' ? '#007bff' : '#f1f3f4',
                            color: message.type === 'user' ? 'white' : '#333',
                            fontSize: '14px',
                            lineHeight: '1.4',
                            wordBreak: 'break-word'
                        }}>
                            {message.content}
                        </div>
                        <div style={{
                            fontSize: '11px',
                            color: '#999',
                            marginTop: '5px',
                            marginLeft: message.type === 'user' ? '0' : '15px',
                            marginRight: message.type === 'user' ? '15px' : '0'
                        }}>
                            {formatTime(message.timestamp)}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                        <div style={{
                            padding: '10px 15px',
                            borderRadius: '18px',
                            backgroundColor: '#f1f3f4',
                            color: '#666',
                            fontSize: '14px'
                        }}>
                            <span>Thinking</span>
                            <span className="loading-dots">...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Error Display */}
            {error && (
                <div style={{ padding: '10px 15px', backgroundColor: '#f8d7da', color: '#721c24', fontSize: '12px' }}>
                    {error}
                </div>
            )}

            {/* Input */}
            <div style={{
                padding: '15px',
                borderTop: '1px solid #ddd',
                backgroundColor: 'white'
            }}>
                <form onSubmit={handleSendMessage}>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder={isIndexed ? "Ask a question about your papers..." : "Index project to enable chat"}
                            style={{
                                flex: 1,
                                padding: '10px 15px',
                                border: '1px solid #ddd',
                                borderRadius: '20px',
                                fontSize: '14px',
                                outline: 'none'
                            }}
                            disabled={!isIndexed || isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!inputMessage.trim() || !isIndexed || isLoading}
                            style={{
                                padding: '10px 20px',
                                border: 'none',
                                borderRadius: '20px',
                                backgroundColor: '#007bff',
                                color: 'white',
                                cursor: 'pointer',
                                fontSize: '14px',
                                opacity: (!inputMessage.trim() || !isIndexed || isLoading) ? 0.5 : 1
                            }}
                        >
                            Send
                        </button>
                    </div>
                </form>

                {/* Quick Actions */}
                {isIndexed && messages.length > 1 && (
                    <div style={{ marginTop: '10px' }}>
                        <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>
                            Quick questions:
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                            {[
                                "Summarize the main findings",
                                "What are the key methodologies?",
                                "List the conclusions"
                            ].map((suggestion, index) => (
                                <button
                                    key={index}
                                    onClick={() => setInputMessage(suggestion)}
                                    style={{
                                        padding: '5px 10px',
                                        border: '1px solid #ddd',
                                        borderRadius: '15px',
                                        backgroundColor: 'white',
                                        color: '#666',
                                        fontSize: '11px',
                                        cursor: 'pointer'
                                    }}
                                    disabled={isLoading}
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatInterface;