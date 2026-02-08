import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Bot, User, Paperclip, File as FileIcon } from 'lucide-react';

const ChatbotPanel = ({ isOpen, onClose }) => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'bot',
            text: 'Bonjour! Je suis votre assistant de trading IA. Comment puis-je vous aider aujourd\'hui?',
            timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [selectedFiles, setSelectedFiles] = useState([]);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files);
        setSelectedFiles(prev => [...prev, ...files]);
    };

    const handleRemoveFile = (index) => {
        setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!inputValue.trim()) return;

        // Add user message
        const userMessage = {
            id: messages.length + 1,
            type: 'user',
            text: inputValue,
            timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setSelectedFiles([]);

        // Simulate bot response after a delay
        setTimeout(() => {
            const botResponses = [
                'Basé sur l\'analyse technique, BIAT montre une tendance haussière avec un RSI de 65.',
                'Le volume de SAH a augmenté de 45% aujourd\'hui, ce qui pourrait indiquer un mouvement important à venir.',
                'Les indicateurs suggèrent une consolidation pour SFBT autour du niveau de 12.50 TND.',
                'L\'indice TUNINDEX est en hausse de 0.8% aujourd\'hui, principalement tiré par le secteur bancaire.',
                'Je recommande de surveiller les niveaux de support à 11.20 TND pour cette action.',
            ];

            const botMessage = {
                id: messages.length + 2,
                type: 'bot',
                text: botResponses[Math.floor(Math.random() * botResponses.length)],
                timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
            };

            setMessages(prev => [...prev, botMessage]);
        }, 1000);
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Overlay */}
            <div
                className="chatbot-overlay"
                onClick={onClose}
            />

            {/* Side Panel */}
            <div className={`chatbot-panel ${isOpen ? 'open' : ''}`}>
                {/* Header */}
                <div className="chatbot-header">
                    <div className="flex items-center gap-3">
                        <div style={{
                            width: '36px',
                            height: '36px',
                            background: 'linear-gradient(135deg, var(--accent) 0%, #0099cc 100%)',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            <Bot size={20} color="white" />
                        </div>
                        <div>
                            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                                Assistant IA
                            </h3>
                            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                En ligne
                            </p>
                        </div>
                    </div>
                    <button
                        className="chatbot-close-btn"
                        onClick={onClose}
                        title="Fermer"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Messages */}
                <div className="chatbot-messages">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`chat-message ${message.type}`}
                        >
                            <div className="message-avatar">
                                {message.type === 'bot' ? (
                                    <Bot size={16} />
                                ) : (
                                    <User size={16} />
                                )}
                            </div>
                            <div className="message-content">
                                <div className="message-bubble">
                                    {message.text}
                                </div>
                                <span className="message-time">{message.timestamp}</span>
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div>
                    {/* Selected Files */}
                    {selectedFiles.length > 0 && (
                        <div className="chatbot-files-preview">
                            {selectedFiles.map((file, index) => (
                                <div key={index} className="file-chip">
                                    <FileIcon size={14} />
                                    <span className="file-name">{file.name}</span>
                                    <button
                                        type="button"
                                        className="file-remove"
                                        onClick={() => handleRemoveFile(index)}
                                        title="Supprimer"
                                    >
                                        <X size={12} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <form className="chatbot-input-container" onSubmit={handleSendMessage}>
                        {/* Hidden File Input */}
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            onChange={handleFileSelect}
                            style={{ display: 'none' }}
                            accept=".pdf,.doc,.docx,.txt,.csv,.xlsx,.xls,.json"
                        />

                        {/* File Upload Button */}
                        <button
                            type="button"
                            className="chatbot-file-btn"
                            onClick={() => fileInputRef.current?.click()}
                            title="Joindre un fichier"
                        >
                            <Paperclip size={18} />
                        </button>

                        <input
                            type="text"
                            className="chatbot-input"
                            placeholder="Posez votre question..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                        />
                        <button
                            type="submit"
                            className="chatbot-send-btn"
                            disabled={!inputValue.trim()}
                        >
                            <Send size={18} />
                        </button>
                    </form>
                </div>
            </div>
        </>
    );
};

export default ChatbotPanel;
