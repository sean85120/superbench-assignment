import axios from 'axios';
import React, { useEffect, useRef, useState } from 'react';

// Configure axios base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
axios.defaults.baseURL = API_BASE_URL;

function App() {
    const [activeTab, setActiveTab] = useState('chat');
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    
    // Ref for the messages container
    const messagesEndRef = useRef(null);

    // Function to scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Scroll to bottom when messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async() => {
        if (!message.trim()) return;

        const userMessage = {
            id: Date.now(),
            text: message,
            sender: 'user',
            timestamp: new Date().toLocaleTimeString(),
        };

        setMessages(prev => [...prev, userMessage]);
        setMessage('');
        setIsLoading(true);
        setError('');

        try {
            const response = await axios.post('/chat/', {
                message: message,
                agent_id: 1,
            });

            const botMessage = {
                id: Date.now() + 1,
                text: response.data.response,
                sender: 'bot',
                timestamp: new Date().toLocaleTimeString(),
                metadata: response.data.metadata,
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
            console.error('Error sending message:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // Simple function to render text with line breaks
    const renderTextWithLineBreaks = (text) => {
        return text.split('\n').map((line, index) => (
            <React.Fragment key={index}>
                {line}
                {index < text.split('\n').length - 1 && <br />}
            </React.Fragment>
        ));
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <h1 className="text-xl font-semibold text-gray-900">
                            BikeHero AI Agent Interface
                        </h1>
                        <span className="text-sm text-gray-600">
                            Demo Mode - Single User
                        </span>
                    </div>
                </div>
            </header>

            <nav className="bg-white border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex space-x-8">
                        {['chat', 'history'].map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                                    activeTab === tab
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                            >
                                {tab.charAt(0).toUpperCase() + tab.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {activeTab === 'chat' && (
                    <div className="max-w-4xl mx-auto">
                        <div className="bg-white rounded-lg shadow-sm border">
                            <div className="px-6 py-4 border-b bg-gray-50 rounded-t-lg">
                                <h2 className="text-lg font-semibold text-gray-900">
                                    Chat with AI Agent
                                </h2>
                                <p className="text-sm text-gray-500 mt-1">
                                    Ask me about BikeHero's maintenance services and pricing!
                                </p>
                            </div>

                            <div className="h-96 overflow-y-auto p-6 space-y-4">
                                {messages.length === 0 ? (
                                    <div className="text-center text-gray-500 py-8">
                                        <p>Start a conversation with the AI agent</p>
                                        <p className="text-sm mt-2">
                                            Try asking: "What are your maintenance packages?"
                                        </p>
                                    </div>
                                ) : (
                                    messages.map((msg) => (
                                        <div
                                            key={msg.id}
                                            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                        >
                                            <div
                                                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                                    msg.sender === 'user'
                                                        ? 'bg-blue-600 text-white'
                                                        : 'bg-gray-100 text-gray-900'
                                                }`}
                                            >
                                                <div className="text-sm">
                                                    {renderTextWithLineBreaks(msg.text)}
                                                </div>

                                                {msg.metadata && msg.metadata.requires_human && (
                                                    <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs text-yellow-800">
                                                        ⚠️Transfer to human agent required
                                                    </div>
                                                )}

                                                <p
                                                    className={`text-xs mt-1 ${
                                                        msg.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                                                    }`}
                                                >
                                                    {msg.timestamp}
                                                </p>
                                            </div>
                                        </div>
                                    ))
                                )}

                                {isLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                                            <div className="flex space-x-1">
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                                <div 
                                                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                                    style={{ animationDelay: '0.1s' }}
                                                ></div>
                                                <div 
                                                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                                    style={{ animationDelay: '0.2s' }}
                                                ></div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                
                                {/* Invisible div to scroll to */}
                                <div ref={messagesEndRef} />
                            </div>

                            {error && (
                                <div className="px-6 py-3 bg-red-50 border-t border-red-200">
                                    <span className="text-sm text-red-600">{error}</span>
                                </div>
                            )}

                            <div className="px-6 py-4 border-t bg-gray-50 rounded-b-lg">
                                <div className="flex space-x-3">
                                    <input
                                        type="text"
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Type your message..."
                                        disabled={isLoading}
                                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                                    />
                                    <button
                                        onClick={sendMessage}
                                        disabled={!message.trim() || isLoading}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                    >
                                        Send
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'history' && (
                    <ChatHistoryTab />
                )}
            </main>
        </div>
    );
}

// Chat History Component
function ChatHistoryTab() {
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const fetchHistory = async() => {
        setIsLoading(true);
        setError('');

        try {
            const response = await axios.get('/chat/history/');
            setHistory(response.data);
        } catch (err) {
            setError('Failed to load chat history. Please try again.');
            console.error('Error fetching chat history:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Load history when component mounts
    React.useEffect(() => {
        fetchHistory();
    }, []);

    // Simple function to render text with line breaks
    const renderTextWithLineBreaks = (text) => {
        return text.split('\n').map((line, index) => (
            <React.Fragment key={index}>
                {line}
                {index < text.split('\n').length - 1 && <br />}
            </React.Fragment>
        ));
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b bg-gray-50 rounded-t-lg">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
                        <button
                            onClick={fetchHistory}
                            disabled={isLoading}
                            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                        >
                            {isLoading ? 'Loading...' : 'Refresh'}
                        </button>
                    </div>
                </div>

                <div className="p-6">
                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                            <span className="text-sm text-red-600">{error}</span>
                        </div>
                    )}

                    {isLoading ? (
                        <div className="text-center py-8">
                            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <p className="mt-2 text-gray-500">Loading chat history...</p>
                        </div>
                    ) : history.length === 0 ? (
                        <div className="text-center py-8">
                            <p className="text-gray-500">No chat history found</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {history.map((chat) => (
                                <div key={chat.id} className="border rounded-lg p-4">
                                    <div className="flex items-start space-x-3">
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-gray-900">User Message</p>
                                            <p className="text-sm text-gray-700 mt-1">{chat.message}</p>
                                            <p className="text-xs text-gray-500 mt-1">
                                                {new Date(chat.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-start space-x-3 mt-3 pt-3 border-t">
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-gray-900">AI Response</p>
                                            <div className="text-sm text-gray-700 mt-1">
                                                {renderTextWithLineBreaks(chat.response)}
                                            </div>
                                            {chat.metadata_info && chat.metadata_info.requires_human && (
                                                <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs text-yellow-800">
                                                    ⚠️Transfer to human agent required
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;