import { create } from 'zustand';
import { api } from '../services/api';

export const useProductStore = create((set) => ({
  products: [],
  loading: false,
  error: null,

  fetchProducts: async (filters = {}) => {
    set({ loading: true });
    try {
      const response = await api.getProducts(filters);
      set({ products: response.data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  addProduct: async (product) => {
    const response = await api.createProduct(product);
    set(state => ({ products: [...state.products, response.data] }));
  },

  updateProduct: async (id, product) => {
    const response = await api.updateProduct(id, product);
    set(state => ({
      products: state.products.map(p => p.id === id ? response.data : p)
    }));
  },

  deleteProduct: async (id) => {
    await api.deleteProduct(id);
    set(state => ({ products: state.products.filter(p => p.id !== id) }));
  }
}));
