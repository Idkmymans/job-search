import React from 'react';
import { Eye, EyeOff, Copy, ExternalLink } from 'lucide-react';
import { Modal } from '../../ui/Modal';
import { Button } from '../../ui/Button';
import { Card, CardBody } from '../../ui/Card';
import { Tender } from '../../../types';
import { formatDateTime, getUrgencyBadgeClass } from '../../../lib/utils';
import { useNotification } from '../../../context/NotificationContext';

interface TenderDetailModalProps {
  tender: Tender;
  isOpen: boolean;
  onClose: () => void;
  onUnmarkRelevant?: () => void;
}

export const TenderDetailModal: React.FC<TenderDetailModalProps> = ({
  tender,
  isOpen,
  onClose,
  onUnmarkRelevant,
}) => {
  const { addNotification } = useNotification();

  const handleCopyIfbNo = () => {
    navigator.clipboard.writeText(tender.ifb_no);
    addNotification('success', 'IFB No copied to clipboard');
  };

  const detailItems = [
    { label: 'IFB No', value: tender.ifb_no, copiable: true },
    { label: 'Title', value: tender.title },
    { label: 'Organization', value: tender.organization },
    { label: 'Deadline', value: formatDateTime(tender.deadline) },
    { label: 'Days Left', value: tender.days_left ? `${tender.days_left} days` : 'N/A' },
    { label: 'Procurement Type', value: tender.procurement_type },
    { label: 'Notice Date', value: formatDateTime(tender.notice_date) },
    { label: 'Province', value: tender.province || 'Not specified' },
    { label: 'Source', value: tender.source },
    { label: 'Scraped Date', value: tender.scraped_date },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Tender Details" size="lg">
      <div className="space-y-4">
        {/* Urgency Badge */}
        <div className="flex items-center gap-3">
          <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getUrgencyBadgeClass(tender.days_left)}`}>
            {tender.days_left !== null
              ? tender.days_left <= 5
                ? 'URGENT'
                : tender.days_left <= 15
                ? 'COMING SOON'
                : 'AVAILABLE'
              : 'STATUS UNKNOWN'}
          </span>
          {tender.marked_relevant && (
            <span className="px-3 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium flex items-center gap-1">
              <Eye size={16} />
              Marked Relevant
            </span>
          )}
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {detailItems.map((item, idx) => (
            <div key={idx} className="space-y-1">
              <label className="text-xs font-semibold text-slate-600 uppercase">{item.label}</label>
              <div className="flex items-center gap-2">
                <p className="text-sm text-slate-900 break-words">{item.value}</p>
                {item.copiable && (
                  <button
                    onClick={handleCopyIfbNo}
                    className="text-slate-400 hover:text-slate-600 transition-colors flex-shrink-0"
                    title="Copy to clipboard"
                    aria-label="Copy IFB No"
                  >
                    <Copy size={16} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-slate-200">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Close
          </Button>
          {onUnmarkRelevant && (
            <Button variant="danger" onClick={onUnmarkRelevant} className="flex-1">
              Unmark as Relevant
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};
