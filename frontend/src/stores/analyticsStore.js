import { create } from 'zustand';
import { api } from '../services/api';

export const useAnalyticsStore = create((set) => ({
  salesTrends: [],
  topPerformers: [],
  restockUrgency: [],
  loading: false,

  fetchSalesTrends: async (period = '30d') => {
    set({ loading: true });
    try {
      const response = await api.getSalesTrends(period);
      set({ salesTrends: response.data, loading: false });
    } catch (error) {
      set({ loading: false });
    }
  },

  fetchTopPerformers: async (limit = 5) => {
    set({ loading: true });
    try {
      const response = await api.getTopPerformers(limit);
      set({ topPerformers: response.data, loading: false });
    } catch (error) {
      set({ loading: false });
    }
  },

  fetchRestockUrgency: async () => {
    set({ loading: true });
    try {
      const response = await api.getRestockUrgency();
      set({ restockUrgency: response.data, loading: false });
    } catch (error) {
      set({ loading: false });
    }
  }
}));
