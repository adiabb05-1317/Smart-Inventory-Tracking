import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Package, TrendingUp, MessageSquare, AlertTriangle } from 'lucide-react';

export const Sidebar = () => {
  const location = useLocation();

  const links = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/products', icon: Package, label: 'Products' },
    { path: '/analytics', icon: TrendingUp, label: 'Analytics' },
    { path: '/ai-chat', icon: MessageSquare, label: 'AI Assistant' },
    { path: '/alerts', icon: AlertTriangle, label: 'Low Stock' }
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-800">
          Smart Inventory
        </h1>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {links.map(({ path, icon: Icon, label }) => (
          <Link
            key={path}
            to={path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              location.pathname === path
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Icon size={20} />
            <span className="font-medium">{label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
};
