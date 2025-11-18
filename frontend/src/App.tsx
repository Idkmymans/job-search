import React, { useState, useEffect } from 'react';
import { NotificationProvider } from './context/NotificationContext';
import { useTenders } from './hooks/useTenders';
import { useNotification } from './context/NotificationContext';
import { ScrapingStatus } from './types';

import { Header } from './components/layout/Header';
import { Sidebar, getNavIcon } from './components/layout/Sidebar';
import { NotificationContainer } from './components/layout/NotificationContainer';

import { RelevantTendersPage } from './components/pages/RelevantTendersPage';
import { AllTendersPage } from './components/pages/AllTendersPage';
import { StatisticsPage } from './components/pages/StatisticsPage';

import { AddTenderModal } from './components/pages/modals/AddTenderModal';
import { ConfirmDialog } from './components/pages/modals/ConfirmDialog';
import { ScrapingStatusModal } from './components/pages/modals/ScrapingStatusModal';
import { Modal } from './components/ui/Modal';
import { Button } from './components/ui/Button';
import { Card, CardBody } from './components/ui/Card';
import { Input } from './components/ui/Input';
import { Checkbox } from './components/ui/Checkbox';

import { formatDateTime, generateCSVContent, downloadFile, generateTimestamp } from './lib/utils';
import { Download, Save } from 'lucide-react';

const AppContent: React.FC = () => {
  const { tenders, addTender, clearAllTenders, fetchTenders } = useTenders();
  const { addNotification } = useNotification();

  const [currentPage, setCurrentPage] = useState('relevant');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  // Modals
  const [showAddTender, setShowAddTender] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [showScrapingStatus, setShowScrapingStatus] = useState(false);
  const [showExportOptions, setShowExportOptions] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false);
  const [showSaveDataConfirm, setShowSaveDataConfirm] = useState(false);

  // Scraping status
  const [scrapingStatus, setScrapingStatus] = useState<ScrapingStatus>({
    status: 'idle',
  });

  // Export options
  const [exportOptions, setExportOptions] = useState({
    export_type: 'relevant' as 'relevant' | 'all' | 'filtered',
    include_summary: false,
    columns: {
      ifb_no: true,
      title: true,
      organization: true,
      deadline: true,
      days_left: true,
      procurement_type: true,
      notice_date: true,
      province: true,
      source: true,
    },
  });

  useEffect(() => {
    fetchTenders();
    setLastUpdated(formatDateTime(new Date().toISOString()));
    const interval = setInterval(() => {
      setLastUpdated(formatDateTime(new Date().toISOString()));
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  // Simulate scraping polling
  useEffect(() => {
    if (scrapingStatus.status === 'scraping') {
      const timer = setTimeout(() => {
        // Simulate scraping progress
        if (scrapingStatus.current_page === undefined) {
          setScrapingStatus({
            status: 'scraping',
            current_page: 1,
            total_pages: 5,
            tenders_found: 0,
            duplicates_skipped: 0,
          });
        } else if ((scrapingStatus.current_page || 0) < (scrapingStatus.total_pages || 1)) {
          setScrapingStatus((prev) => ({
            ...prev,
            current_page: (prev.current_page || 0) + 1,
            tenders_found: (prev.tenders_found || 0) + Math.floor(Math.random() * 10) + 5,
            duplicates_skipped: (prev.duplicates_skipped || 0) + Math.floor(Math.random() * 3),
          }));
        } else {
          setScrapingStatus({
            status: 'completed',
            tenders_found: 45,
            duplicates_skipped: 8,
            last_scraped: formatDateTime(new Date().toISOString()),
          });
          addNotification('success', 'Scraping completed: 45 tenders found, 8 duplicates skipped');
          setTimeout(() => {
            setScrapingStatus({ status: 'idle' });
            fetchTenders();
          }, 3000);
        }
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [scrapingStatus]);

  const handleAddTender = async (tender: any) => {
    await addTender(tender);
    setShowAddTender(false);
    await fetchTenders();
  };

  const handleClearAll = async () => {
    try {
      await clearAllTenders();
      setShowClearConfirm(false);
      addNotification('success', 'All tenders cleared successfully');
    } catch (err) {
      addNotification('error', 'Failed to clear tenders');
    }
  };

  const handleExport = () => {
    const selectedColumns = Object.keys(exportOptions.columns).filter(
      (col) => exportOptions.columns[col as keyof typeof exportOptions.columns]
    ) as (keyof typeof exportOptions.columns)[];

    if (selectedColumns.length === 0) {
      addNotification('error', 'Please select at least one column');
      return;
    }

    let dataToExport = tenders;
    if (exportOptions.export_type === 'relevant') {
      dataToExport = tenders.filter((t) => t.marked_relevant);
    }

    if (dataToExport.length === 0) {
      addNotification('error', 'No tenders to export');
      return;
    }

    const exportData = dataToExport.map((tender) => {
      const row: Record<string, any> = {};
      selectedColumns.forEach((col) => {
        row[col] = tender[col];
      });
      return row;
    });

    const headers = selectedColumns.join(',');
    const rows = exportData.map((row) =>
      selectedColumns
        .map((col) => {
          const value = row[col];
          if (typeof value === 'string' && value.includes(',')) {
            return `"${value}"`;
          }
          return value || '';
        })
        .join(',')
    );

    const content = [headers, ...rows].join('\n');
    const filename = `tenders_export_${generateTimestamp()}.csv`;
    downloadFile(content, filename, 'text/csv');

    addNotification(
      'success',
      `Exported ${dataToExport.length} tender(s) to CSV`
    );
    setShowExportOptions(false);
  };

  const handleSaveData = () => {
    const data = {
      timestamp: new Date().toISOString(),
      total_tenders: tenders.length,
      relevant_tenders: tenders.filter((t) => t.marked_relevant).length,
      tenders: tenders,
    };

    const content = JSON.stringify(data, null, 2);
    const filename = `tender_backup_${generateTimestamp()}.json`;
    downloadFile(content, filename, 'application/json');

    addNotification('success', 'Data backup saved successfully');
    setShowSaveDataConfirm(false);
  };

  const handleStartScraping = () => {
    setScrapingStatus({
      status: 'scraping',
      current_page: 0,
      total_pages: 5,
      tenders_found: 0,
      duplicates_skipped: 0,
    });
  };

  const navItems = [
    {
      id: 'relevant',
      label: 'Relevant Tenders',
      icon: getNavIcon('relevant'),
      action: () => {
        setCurrentPage('relevant');
        setSidebarOpen(false);
      },
    },
    {
      id: 'all',
      label: 'All Tenders',
      icon: getNavIcon('all'),
      action: () => {
        setCurrentPage('all');
        setSidebarOpen(false);
      },
    },
    {
      id: 'add',
      label: 'Add Tender',
      icon: getNavIcon('add'),
      action: () => setShowAddTender(true),
    },
    {
      id: 'export',
      label: 'Export to CSV',
      icon: getNavIcon('export'),
      action: () => setShowExportOptions(true),
    },
    {
      id: 'clear',
      label: 'Clear Tenders',
      icon: getNavIcon('clear'),
      action: () => setShowClearConfirm(true),
    },
    {
      id: 'save',
      label: 'Save Data',
      icon: getNavIcon('save'),
      action: () => setShowSaveDataConfirm(true),
    },
    {
      id: 'scrape',
      label: 'Auto-Scrape',
      icon: getNavIcon('scrape'),
      action: () => setShowScrapingStatus(true),
      badge: scrapingStatus.status === 'scraping',
    },
    {
      id: 'analytics',
      label: 'Statistics',
      icon: getNavIcon('analytics'),
      action: () => {
        setCurrentPage('analytics');
        setSidebarOpen(false);
      },
    },
  ];

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <Sidebar
        navItems={navItems}
        currentPage={currentPage}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <Header
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
          lastUpdated={lastUpdated}
          onScrapingStatus={() => setShowScrapingStatus(true)}
          isScrapingActive={scrapingStatus.status === 'scraping'}
          onExit={() => setShowExitConfirm(true)}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {currentPage === 'relevant' && <RelevantTendersPage />}
            {currentPage === 'all' && <AllTendersPage />}
            {currentPage === 'analytics' && <StatisticsPage />}
          </div>
        </main>
      </div>

      {/* Modals */}
      <AddTenderModal
        isOpen={showAddTender}
        onClose={() => setShowAddTender(false)}
        onSubmit={handleAddTender}
        existingIfbNumbers={tenders.map((t) => t.ifb_no)}
      />

      <ConfirmDialog
        isOpen={showClearConfirm}
        onClose={() => setShowClearConfirm(false)}
        onConfirm={handleClearAll}
        title="Clear All Tenders"
        message="Are you sure you want to delete all tenders?"
        description="This action is permanent and cannot be undone."
        confirmText="Clear All"
        cancelText="Cancel"
        danger={true}
        requiresCheckbox={true}
        checkboxLabel="I understand this will delete all tenders permanently"
        itemCount={tenders.length}
      />

      <ScrapingStatusModal
        isOpen={showScrapingStatus}
        onClose={() => {
          setShowScrapingStatus(false);
          if (scrapingStatus.status === 'idle') {
            setScrapingStatus({ status: 'idle' });
          }
        }}
        status={scrapingStatus}
        onStartScraping={handleStartScraping}
        lastScrapedAt="2025-11-14 10:30 AM"
      />

      {/* Export Options Modal */}
      <Modal
        isOpen={showExportOptions}
        onClose={() => setShowExportOptions(false)}
        title="Export Tenders to CSV"
        size="md"
      >
        <div className="space-y-4">
          {/* Export Type */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Export Type
            </label>
            <div className="space-y-2">
              {[
                { value: 'relevant', label: 'Relevant Tenders Only' },
                { value: 'all', label: 'All Tenders' },
              ].map((option) => (
                <label key={option.value} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="export_type"
                    value={option.value}
                    checked={exportOptions.export_type === option.value}
                    onChange={(e) =>
                      setExportOptions({
                        ...exportOptions,
                        export_type: e.target.value as any,
                      })
                    }
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-slate-700">{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Columns Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Select Columns
            </label>
            <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-lg">
              {Object.keys(exportOptions.columns).map((col) => (
                <Checkbox
                  key={col}
                  label={col}
                  checked={exportOptions.columns[col as keyof typeof exportOptions.columns]}
                  onChange={(e) =>
                    setExportOptions({
                      ...exportOptions,
                      columns: {
                        ...exportOptions.columns,
                        [col]: e.target.checked,
                      },
                    })
                  }
                />
              ))}
            </div>
          </div>

          {/* Include Summary */}
          <Checkbox
            label="Include Summary Statistics"
            checked={exportOptions.include_summary}
            onChange={(e) =>
              setExportOptions({
                ...exportOptions,
                include_summary: e.target.checked,
              })
            }
          />

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-slate-200">
            <Button variant="secondary" onClick={() => setShowExportOptions(false)} className="flex-1">
              Cancel
            </Button>
            <Button variant="primary" onClick={handleExport} icon={<Download size={18} />} className="flex-1">
              Export
            </Button>
          </div>
        </div>
      </Modal>

      {/* Save Data Confirm */}
      <ConfirmDialog
        isOpen={showSaveDataConfirm}
        onClose={() => setShowSaveDataConfirm(false)}
        onConfirm={handleSaveData}
        title="Save Current Data"
        message="Export current database as backup?"
        description="This will download a JSON file with all tender data."
        confirmText="Save Backup"
        cancelText="Cancel"
      />

      {/* Exit Confirm */}
      <ConfirmDialog
        isOpen={showExitConfirm}
        onClose={() => setShowExitConfirm(false)}
        onConfirm={() => {
          addNotification('info', 'All data is safely stored in Supabase');
          setTimeout(() => window.close(), 1000);
        }}
        title="Exit Application"
        message="Are you sure you want to exit?"
        description="Your data is automatically saved in the database and will be available next time you open the application."
        confirmText="Exit"
        cancelText="Continue"
      />

      {/* Notifications */}
      <NotificationContainer />
    </div>
  );
};

function App() {
  return (
    <NotificationProvider>
      <AppContent />
    </NotificationProvider>
  );
}

export default App;
