import axios from 'axios';

// Prefer Vite env vars; fallback to empty string for relative /api calls
const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || '';
const VITE_API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api';

function buildUrl(endpoint) {
  const clean = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  if (!VITE_BACKEND_URL) {
    // Production behind Nginx: use relative /api
    return endpoint.startsWith('/') ? endpoint : `${VITE_API_PREFIX}/${clean}`;
  }
  // Dev: explicit backend URL
  return `${VITE_BACKEND_URL}/${clean}`;
}

export const api = {
  // Products
  getProducts: (params) => axios.get(buildUrl('products'), { params }),
  createProduct: (data) => axios.post(buildUrl('products'), data),
  updateProduct: (id, data) => axios.put(buildUrl(`products/${id}`), data),
  deleteProduct: (id) => axios.delete(buildUrl(`products/${id}`)),
  getLowStock: () => axios.get(buildUrl('products/low-stock')),

  // Analytics
  getSalesTrends: (period) => axios.get(buildUrl(`analytics/sales-trends?period=${period}`)),
  getTopPerformers: (limit) => axios.get(buildUrl(`analytics/top-performers?limit=${limit}`)),
  getRestockUrgency: () => axios.get(buildUrl('analytics/restock-urgency')),
  getInventoryTurnover: (category) => axios.get(buildUrl('analytics/inventory-turnover'), { params: { category } }),

  // AI Chat
  sendChatMessage: (message) => axios.post(buildUrl('ai/chat'), { message })
};
