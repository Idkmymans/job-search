import React from 'react';
import { Menu, LogOut, Globe } from 'lucide-react';
import { Button } from '../ui/Button';

interface HeaderProps {
  onMenuToggle: () => void;
  lastUpdated?: string;
  onScrapingStatus?: () => void;
  isScrapingActive?: boolean;
  onExit: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onMenuToggle,
  lastUpdated,
  onScrapingStatus,
  isScrapingActive,
  onExit,
}) => {
  return (
    <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
      <div className="flex items-center justify-between px-4 py-3 sm:px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuToggle}
            className="text-slate-600 hover:text-slate-900 lg:hidden transition-colors"
            aria-label="Toggle menu"
          >
            <Menu size={24} />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">TM</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Tender Manager</h1>
              <p className="text-xs text-slate-500">Pranaya's side project</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {lastUpdated && (
            <div className="hidden sm:flex flex-col items-end text-xs text-slate-500">
              <p>Last Updated</p>
              <p className="font-medium text-slate-700">{lastUpdated}</p>
            </div>
          )}

          <button
            onClick={onScrapingStatus}
            className={`p-2 rounded-lg transition-colors ${
              isScrapingActive
                ? 'bg-orange-100 text-orange-600 hover:bg-orange-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
            title="Scraping status"
            aria-label="Scraping status"
          >
            <Globe size={20} />
            {isScrapingActive && (
              <span className="absolute top-2 right-2 w-2 h-2 bg-orange-600 rounded-full animate-pulse" />
            )}
          </button>

          <Button
            variant="subtle"
            size="sm"
            onClick={onExit}
            icon={<LogOut size={18} />}
            title="Exit application"
          >
            <span className="hidden sm:inline">Exit</span>
          </Button>
        </div>
      </div>
    </header>
  );
};
