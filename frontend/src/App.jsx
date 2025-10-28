import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './components/dashboard/Dashboard';
import { ProductList } from './components/products/ProductList';
import { Analytics } from './components/analytics/Analytics';
import { ChatInterface } from './components/ai/ChatInterface';
import { LowStockAlerts } from './components/alerts/LowStockAlerts';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<ProductList />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/ai-chat" element={<ChatInterface />} />
          <Route path="/alerts" element={<LowStockAlerts />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
