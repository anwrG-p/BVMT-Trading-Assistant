import React, { useState, useRef, useEffect, ChangeEvent, FormEvent } from 'react';
import { X, Send, Bot, User, Paperclip, File as FileIcon } from 'lucide-react';

interface Message {
  id: number;
  type: 'bot' | 'user';
  text: string;
  timestamp: string;
}

interface ChatbotPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatbotPanel: React.FC<ChatbotPanelProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'bot',
      text: "Bonjour! Je suis votre assistant de trading IA BVMT. Comment puis-je vous aider aujourd'hui?",
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSendMessage = (e: FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: 'user',
      text: inputValue,
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setSelectedFiles([]);

    setTimeout(() => {
      const botResponses = [
        "Basé sur l'analyse technique, BIAT montre une tendance haussière avec un RSI de 65.",
        "Le volume de SAH a augmenté de 45% aujourd'hui, ce qui pourrait indiquer un mouvement important à venir.",
        "Les indicateurs suggèrent une consolidation pour SFBT autour du niveau de 11.90 TND.",
        "L'indice TUNINDEX se maintient solidement soutenu par les grandes capitalisations bancaires.",
        "Je recommande de surveiller les niveaux de support à 50.50 TND pour ATTIJARI BANK."
      ];

      const botMessage: Message = {
        id: messages.length + 2,
        type: 'bot',
        text: botResponses[Math.floor(Math.random() * botResponses.length)],
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMessage]);
    }, 600);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="chatbot-overlay" onClick={onClose} />
      <div className={`chatbot-panel ${isOpen ? 'open' : ''}`}>
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
                Assistant IA BVMT
              </h3>
              <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                En ligne
              </p>
            </div>
          </div>
          <button className="chatbot-close-btn" onClick={onClose} title="Fermer">
            <X size={20} />
          </button>
        </div>

        <div className="chatbot-messages">
          {messages.map((message) => (
            <div key={message.id} className={`chat-message ${message.type}`}>
              <div className="message-avatar">
                {message.type === 'bot' ? <Bot size={16} /> : <User size={16} />}
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

        <div>
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
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept=".pdf,.doc,.docx,.txt,.csv,.xlsx,.xls,.json"
            />

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
              placeholder="Posez votre question sur une valeur BVMT..."
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
