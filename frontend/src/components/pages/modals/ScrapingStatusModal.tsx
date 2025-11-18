import React, { useEffect, useState } from 'react';
import { Globe, CheckCircle2, AlertCircle, Loader } from 'lucide-react';
import { Modal } from '../../ui/Modal';
import { Button } from '../../ui/Button';
import { Card, CardBody } from '../../ui/Card';
import { ScrapingStatus } from '../../../types';

interface ScrapingStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  status: ScrapingStatus;
  onStartScraping?: () => void;
  onCancelScraping?: () => void;
  lastScrapedAt?: string;
}

export const ScrapingStatusModal: React.FC<ScrapingStatusModalProps> = ({
  isOpen,
  onClose,
  status,
  onStartScraping,
  onCancelScraping,
  lastScrapedAt,
}) => {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    if (status.status === 'scraping') {
      const newLog = `Scraping page ${status.current_page || 0} of ${status.total_pages || '?'}`;
      if (!logs.includes(newLog)) {
        setLogs((prev) => [newLog, ...prev.slice(0, 4)]);
      }
    } else if (status.status === 'completed') {
      setLogs((prev) => [
        `Completed: Found ${status.tenders_found || 0} tenders, skipped ${status.duplicates_skipped || 0} duplicates`,
        ...prev,
      ]);
    } else if (status.status === 'failed') {
      setLogs((prev) => [`Error: ${status.error_message || 'Unknown error'}`, ...prev]);
    }
  }, [status]);

  const getStatusColor = () => {
    switch (status.status) {
      case 'scraping':
        return 'text-orange-600';
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-slate-600';
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'scraping':
        return <Loader className="animate-spin" size={20} />;
      case 'completed':
        return <CheckCircle2 size={20} />;
      case 'failed':
        return <AlertCircle size={20} />;
      default:
        return <Globe size={20} />;
    }
  };

  const getProgressPercentage = () => {
    if (status.total_pages && status.current_page) {
      return Math.round((status.current_page / status.total_pages) * 100);
    }
    return 0;
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Auto-Scrape Status" size="md">
      <div className="space-y-6">
        {/* Status Display */}
        <div className="flex items-center gap-3">
          <div className={getStatusColor()}>{getStatusIcon()}</div>
          <div>
            <p className="font-semibold text-slate-900 capitalize">{status.status}</p>
            <p className="text-sm text-slate-600">
              {status.status === 'idle' && 'Ready to scrape Bolpatra'}
              {status.status === 'scraping' && 'Scraping Bolpatra pages...'}
              {status.status === 'completed' && 'Scraping completed successfully'}
              {status.status === 'failed' && 'Scraping encountered an error'}
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        {status.status === 'scraping' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-600">Progress</span>
              <span className="font-semibold text-slate-900">{getProgressPercentage()}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-full transition-all duration-300"
                style={{ width: `${getProgressPercentage()}%` }}
              />
            </div>
            {status.current_page && status.total_pages && (
              <p className="text-xs text-slate-600">
                Page {status.current_page} of {status.total_pages}
              </p>
            )}
          </div>
        )}

        {/* Stats */}
        {(status.tenders_found !== undefined || status.duplicates_skipped !== undefined) && (
          <div className="grid grid-cols-2 gap-3">
            {status.tenders_found !== undefined && (
              <Card>
                <CardBody className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{status.tenders_found}</p>
                  <p className="text-xs text-slate-600">Tenders Found</p>
                </CardBody>
              </Card>
            )}
            {status.duplicates_skipped !== undefined && (
              <Card>
                <CardBody className="text-center">
                  <p className="text-2xl font-bold text-orange-600">{status.duplicates_skipped}</p>
                  <p className="text-xs text-slate-600">Duplicates Skipped</p>
                </CardBody>
              </Card>
            )}
          </div>
        )}

        {/* Activity Log */}
        {logs.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-semibold text-slate-700">Activity Log</p>
            <div className="bg-slate-50 rounded-lg p-3 max-h-32 overflow-y-auto space-y-1">
              {logs.map((log, idx) => (
                <p key={idx} className="text-xs text-slate-600 font-mono">
                  {log}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Last Scraped */}
        {lastScrapedAt && status.status === 'idle' && (
          <div className="p-3 bg-slate-50 rounded-lg text-sm text-slate-600">
            <p>
              Last scraped: <span className="font-medium text-slate-900">{lastScrapedAt}</span>
            </p>
          </div>
        )}

        {/* Error Message */}
        {status.status === 'failed' && status.error_message && (
          <Card className="border-red-200 bg-red-50">
            <CardBody className="text-red-700 text-sm">{status.error_message}</CardBody>
          </Card>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-slate-200">
          {status.status === 'idle' ? (
            <>
              <Button variant="secondary" onClick={onClose} className="flex-1">
                Close
              </Button>
              <Button
                variant="primary"
                onClick={onStartScraping}
                icon={<Globe size={18} />}
                className="flex-1"
              >
                Start Scraping
              </Button>
            </>
          ) : status.status === 'scraping' ? (
            <>
              <Button
                variant="danger"
                onClick={onCancelScraping}
                disabled
                className="flex-1"
              >
                Cancel (unavailable)
              </Button>
            </>
          ) : (
            <Button variant="secondary" onClick={onClose} className="w-full">
              Close
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};
