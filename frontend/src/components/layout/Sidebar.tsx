import React from 'react';
import {
  BarChart3,
  Database,
  Download,
  Eye,
  FileText,
  Globe,
  Plus,
  Search,
  Trash2,
  Save,
  X,
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  action: () => void;
  badge?: number | boolean;
  isLoading?: boolean;
}

interface SidebarProps {
  navItems: NavItem[];
  currentPage: string;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ navItems, currentPage, isOpen, onClose }) => {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-screen w-64 bg-slate-900 text-white z-40 transition-transform duration-300
          lg:relative lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          flex flex-col
        `}
      >
        {/* Close button for mobile */}
        <div className="lg:hidden flex items-center justify-between px-6 py-4 border-b border-slate-700">
          <span className="font-semibold">Menu</span>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
            aria-label="Close sidebar"
          >
            <X size={24} />
          </button>
        </div>

        {/* Navigation items */}
        <nav className="flex-1 px-4 py-6 overflow-y-auto space-y-2">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                item.action();
                onClose();
              }}
              disabled={item.isLoading}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                ${
                  currentPage === item.id
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }
              `}
              title={item.label}
            >
              <span className="flex-shrink-0">{item.icon}</span>
              <span className="flex-1 text-left text-sm font-medium">{item.label}</span>
              {item.isLoading && (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" opacity="0.25" />
                  <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {item.badge && typeof item.badge === 'number' && (
                <span className="ml-auto inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                  {item.badge}
                </span>
              )}
              {item.badge === true && (
                <span className="ml-auto w-2 h-2 bg-orange-400 rounded-full animate-pulse" />
              )}
            </button>
          ))}
        </nav>

        {/* Footer info */}
        <div className="border-t border-slate-700 px-4 py-4 text-xs text-slate-400">
          <p>Tender Management System</p>
          <p>v1.0.0</p>
        </div>
      </aside>
    </>
  );
};

export const getNavIcon = (itemId: string) => {
  const iconProps = { size: 20 };
  switch (itemId) {
    case 'dashboard':
      return <BarChart3 {...iconProps} />;
    case 'relevant':
      return <Eye {...iconProps} />;
    case 'all':
      return <Database {...iconProps} />;
    case 'search':
      return <Search {...iconProps} />;
    case 'add':
      return <Plus {...iconProps} />;
    case 'export':
      return <Download {...iconProps} />;
    case 'clear':
      return <Trash2 {...iconProps} />;
    case 'save':
      return <Save {...iconProps} />;
    case 'scrape':
      return <Globe {...iconProps} />;
    case 'analytics':
      return <BarChart3 {...iconProps} />;
    default:
      return <FileText {...iconProps} />;
  }
};
