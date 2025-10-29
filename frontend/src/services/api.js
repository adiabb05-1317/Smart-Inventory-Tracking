import axios from 'axios';


const BACKEND_URL = process.env.BACKEND_URL;

export const api = {
  // Products
  getProducts: (params) => axios.get(`${BACKEND_URL}/products`, { params }),
  createProduct: (data) => axios.post(`${BACKEND_URL}/products`, data),
  updateProduct: (id, data) => axios.put(`${BACKEND_URL}/products/${id}`, data),
  deleteProduct: (id) => axios.delete(`${BACKEND_URL}/products/${id}`),
  getLowStock: () => axios.get(`${BACKEND_URL}/products/low-stock`),

  // Analytics
  getSalesTrends: (period) => axios.get(`${BACKEND_URL}/analytics/sales-trends?period=${period}`),
  getTopPerformers: (limit) => axios.get(`${BACKEND_URL}/analytics/top-performers?limit=${limit}`),
  getRestockUrgency: () => axios.get(`${BACKEND_URL}/analytics/restock-urgency`),
  getInventoryTurnover: (category) => axios.get(`${BACKEND_URL}/analytics/inventory-turnover`, { params: { category } }),

  // AI Chat
  sendChatMessage: (message) => axios.post(`${BACKEND_URL}/ai/chat`, { message })
};
