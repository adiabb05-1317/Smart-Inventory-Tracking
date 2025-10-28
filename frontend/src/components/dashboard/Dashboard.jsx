import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../services/api';
import { KPICard } from './KPICard';
import { Package, TrendingUp, AlertTriangle, DollarSign } from 'lucide-react';

export const Dashboard = () => {
  const [stats, setStats] = useState({
    totalProducts: 0,
    lowStockCount: 0,
    totalValue: 0,
    topPerformer: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [products, lowStock, topPerformers] = await Promise.all([
        api.getProducts({}),
        api.getLowStock(),
        api.getTopPerformers(1)
      ]);

      const totalValue = products.data.reduce((sum, p) => sum + (p.price * p.stock_quantity), 0);

      setStats({
        totalProducts: products.data.length,
        lowStockCount: lowStock.data.length,
        totalValue,
        topPerformer: topPerformers.data[0]
      });
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of your inventory</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Products"
          value={stats.totalProducts}
          icon={Package}
          color="blue"
        />
        <KPICard
          title="Low Stock Items"
          value={stats.lowStockCount}
          icon={AlertTriangle}
          color="red"
        />
        <KPICard
          title="Inventory Value"
          value={`$${stats.totalValue.toLocaleString()}`}
          icon={DollarSign}
          color="green"
        />
        <KPICard
          title="Top Performer"
          value={stats.topPerformer?.name || 'N/A'}
          icon={TrendingUp}
          color="purple"
          subtitle={stats.topPerformer ? `${stats.topPerformer.total_sales} sales` : ''}
        />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/products"
            className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition-colors text-left block"
          >
            <Package className="text-blue-600 mb-2" size={24} />
            <h3 className="font-semibold text-gray-800">Manage Products</h3>
            <p className="text-sm text-gray-500">Add, edit, or delete products</p>
          </Link>
          <Link
            to="/analytics"
            className="p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition-colors text-left block"
          >
            <TrendingUp className="text-green-600 mb-2" size={24} />
            <h3 className="font-semibold text-gray-800">View Analytics</h3>
            <p className="text-sm text-gray-500">Check sales performance</p>
          </Link>
          <Link
            to="/alerts"
            className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 transition-colors text-left block"
          >
            <AlertTriangle className="text-purple-600 mb-2" size={24} />
            <h3 className="font-semibold text-gray-800">Restock Alerts</h3>
            <p className="text-sm text-gray-500">View items needing restock</p>
          </Link>
        </div>
      </div>
    </div>
  );
};
