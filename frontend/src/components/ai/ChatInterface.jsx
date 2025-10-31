import { useState, useEffect, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { Send, Trash2, MessageSquare } from 'lucide-react';

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const { messages, isLoading, sendMessage, clearChat } = useChatStore();
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive or loading state changes
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] bg-white rounded-lg shadow">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">AI Assistant</h3>
          <p className="text-sm text-gray-500">Ask about inventory, sales, and analytics</p>
        </div>
        <button
          onClick={clearChat}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Clear chat"
        >
          <Trash2 size={18} className="text-gray-600" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
            <p>Start a conversation with your AI assistant</p>
            <div className="mt-6 space-y-2 text-sm">
              <p className="text-gray-500">Try asking:</p>
              <div className="space-y-1">
                <p className="text-blue-600">"Show me low stock items"</p>
                <p className="text-blue-600">"What are my top performers?"</p>
                <p className="text-blue-600">"Sales trends for last 30 days"</p>
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl px-4 py-3 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : msg.error
                  ? 'bg-red-50 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-lg">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}

        {/* Invisible element to scroll to */}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about inventory..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};

