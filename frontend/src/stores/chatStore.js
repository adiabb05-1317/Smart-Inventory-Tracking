import { create } from 'zustand';
import { api } from '../services/api';

export const useChatStore = create((set) => ({
  messages: [],
  isLoading: false,

  sendMessage: async (message) => {
    set(state => ({
      messages: [...state.messages, { role: 'user', content: message }],
      isLoading: true
    }));

    try {
      const response = await api.sendChatMessage(message);
      
      set(state => ({
        messages: [...state.messages, {
          role: 'assistant',
          content: response.data.response,
          tools_used: response.data.tools_used
        }],
        isLoading: false
      }));
    } catch (error) {
      set(state => ({
        messages: [...state.messages, {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          error: true
        }],
        isLoading: false
      }));
    }
  },

  clearChat: () => set({ messages: [] })
}));
