import { useState, useEffect, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { Send, Trash2, MessageSquare, Mic, Square, Loader2 } from 'lucide-react';

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [voiceError, setVoiceError] = useState('');
  const { messages, isLoading, sendMessage, clearChat } = useChatStore();
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioStreamRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Auto-scroll to bottom when new messages arrive or loading state changes
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isTranscribing) {
      sendMessage(input);
      setInput('');
    }
  };

  const stopAudioStream = () => {
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((track) => track.stop());
      audioStreamRef.current = null;
    }
  };

  const transcribeAudio = async (audioBlob) => {
    const apiKey = 'b454b5990f5727ec5951a965a81fd1bad66d7cca';
    if (!apiKey) {
      setVoiceError('Deepgram API key is missing. Add VITE_DEEPGRAM_API_KEY to your env.');
      return;
    }

    try {
      setIsTranscribing(true);
      setVoiceError('');

      const arrayBuffer = await audioBlob.arrayBuffer();
      const response = await fetch('https://api.deepgram.com/v1/listen', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${apiKey}`,
          'Content-Type': audioBlob.type || 'audio/webm'
        },
        body: arrayBuffer
      });

      if (!response.ok) {
        throw new Error('Transcription failed');
      }

      const data = await response.json();
      const transcript = data?.results?.channels?.[0]?.alternatives?.[0]?.transcript?.trim();

      if (transcript) {
        await sendMessage(transcript);
        setInput('');
      } else {
        setVoiceError('Could not detect any speech. Please try again.');
      }
    } catch (error) {
      console.error(error);
      setVoiceError('Could not transcribe audio. Please try again.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleRecordingStop = async () => {
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
    audioChunksRef.current = [];
    stopAudioStream();
    setIsRecording(false);

    if (audioBlob.size > 0) {
      await transcribeAudio(audioBlob);
    } else {
      setVoiceError('No audio captured. Please try again.');
    }
  };

  const startRecording = async () => {
    setVoiceError('');

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setVoiceError('Microphone is not supported in this browser.');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : undefined;
      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.addEventListener('dataavailable', (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      });

      mediaRecorder.addEventListener('stop', handleRecordingStop);

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error(error);
      setVoiceError('Microphone access denied or unavailable.');
      stopAudioStream();
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    } else {
      stopAudioStream();
      setIsRecording(false);
    }
  };

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
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
        <div className="flex gap-2 items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about inventory..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || isTranscribing}
          />
          <button
            type="button"
            onClick={handleMicClick}
            disabled={isLoading || isTranscribing}
            className={`p-3 rounded-lg border transition-colors flex items-center justify-center ${
              isRecording
                ? 'bg-red-100 border-red-200 text-red-600 hover:bg-red-200'
                : 'border-gray-300 text-gray-600 hover:bg-gray-100'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            title={isRecording ? 'Stop recording' : 'Start voice input'}
          >
            {isRecording ? <Square size={18} /> : <Mic size={18} />}
          </button>
          <button
            type="submit"
            disabled={isLoading || isTranscribing || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isTranscribing ? <Loader2 size={18} className="animate-spin" /> : <Send size={20} />}
          </button>
        </div>
        {voiceError && (
          <p className="text-sm text-red-500 mt-2">{voiceError}</p>
        )}
        {isTranscribing && !voiceError && (
          <p className="text-sm text-gray-500 mt-2">Transcribing your message...</p>
        )}
      </form>
    </div>
  );
};

