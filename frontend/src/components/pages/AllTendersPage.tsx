import React, { useState, useEffect } from 'react';
import { Database, Eye, EyeOff, Trash2 } from 'lucide-react';
import { useTenders } from '../../hooks/useTenders';
import { Tender } from '../../types';
import { Table } from '../ui/Table';
import { Button } from '../ui/Button';
import { Card, CardHeader, CardBody } from '../ui/Card';
import { useNotification } from '../../context/NotificationContext';
import { formatDate, getUrgencyBadgeClass } from '../../lib/utils';
import { TenderDetailModal } from './modals/TenderDetailModal';
import { ConfirmDialog } from './modals/ConfirmDialog';

export const AllTendersPage: React.FC = () => {
  const { tenders, loading, error, fetchTenders, markRelevant, deleteTenders } = useTenders();
  const { addNotification } = useNotification();
  const [selectedTender, setSelectedTender] = useState<Tender | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [sortBy, setSortBy] = useState<'deadline' | 'days_left'>('days_left');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    fetchTenders();
  }, []);

  const handleSort = (key: any) => {
    if (sortBy === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(key);
      setSortOrder('asc');
    }
  };

  const handleToggleSelect = (tenderId: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(tenderId)) {
      newSelected.delete(tenderId);
    } else {
      newSelected.add(tenderId);
    }
    setSelectedIds(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedIds.size === tenders.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(tenders.map((t) => t.id)));
    }
  };

  const handleMarkRelevant = async (tenderId: string, marked: boolean) => {
    try {
      await markRelevant(tenderId, marked);
      addNotification('success', `Tender ${marked ? 'marked' : 'unmarked'} as relevant`);
      await fetchTenders();
    } catch (err) {
      addNotification('error', 'Failed to update tender');
    }
  };

  const handleDeleteSelected = async () => {
    try {
      await deleteTenders(Array.from(selectedIds));
      setSelectedIds(new Set());
      setDeleteConfirm(false);
      addNotification('success', 'Tender(s) deleted successfully');
      await fetchTenders();
    } catch (err) {
      addNotification('error', 'Failed to delete tender(s)');
    }
  };

  const columns = [
    {
      key: 'ifb_no' as const,
      label: 'IFB No',
      sortable: true,
      render: (value: string) => <span className="font-medium text-blue-600">{value}</span>,
    },
    {
      key: 'title' as const,
      label: 'Title',
      render: (value: string) => <div className="max-w-xs truncate">{value}</div>,
    },
    {
      key: 'organization' as const,
      label: 'Organization',
    },
    {
      key: 'days_left' as const,
      label: 'Days Left',
      sortable: true,
      render: (value: number | null) => (
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getUrgencyBadgeClass(value)}`}>
          {value !== null ? `${value}d` : 'N/A'}
        </span>
      ),
    },
    {
      key: 'source' as const,
      label: 'Source',
      render: (value: string) => (
        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">{value}</span>
      ),
    },
    {
      key: 'marked_relevant' as const,
      label: 'Status',
      render: (value: boolean) => (
        <span
          className={`px-2 py-1 text-xs rounded font-medium ${
            value ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'
          }`}
        >
          {value ? 'Relevant' : 'Non-Relevant'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
            <Database className="text-blue-600" />
            All Tenders
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            {tenders.length} tender{tenders.length !== 1 ? 's' : ''} in database
          </p>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardBody className="text-red-700 text-sm">{error}</CardBody>
        </Card>
      )}

      {/* Bulk Actions */}
      {selectedIds.size > 0 && (
        <Card className="bg-blue-50 border-blue-200">
          <CardBody className="flex items-center justify-between gap-4 flex-wrap">
            <span className="font-semibold text-slate-900">
              {selectedIds.size} tender{selectedIds.size !== 1 ? 's' : ''} selected
            </span>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setSelectedIds(new Set())}
              >
                Clear Selection
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => setDeleteConfirm(true)}
              >
                Delete Selected
              </Button>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Tenders Table */}
      <Card>
        <CardHeader className="flex items-center justify-between">
          <h2 className="font-semibold text-slate-900">Tender Listings</h2>
          <span className="text-sm text-slate-600">{tenders.length} results</span>
        </CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.size === tenders.length && tenders.length > 0}
                      onChange={handleSelectAll}
                      className="w-4 h-4 rounded"
                    />
                  </th>
                  {columns.map((col) => (
                    <th
                      key={String(col.key)}
                      className="px-6 py-3 text-left text-sm font-semibold text-slate-900"
                    >
                      {col.label}
                    </th>
                  ))}
                  <th className="px-6 py-3 text-center text-sm font-semibold text-slate-900">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {loading ? (
                  <tr>
                    <td colSpan={columns.length + 2} className="px-6 py-12 text-center">
                      <div className="text-slate-500">Loading...</div>
                    </td>
                  </tr>
                ) : tenders.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length + 2} className="px-6 py-12 text-center">
                      <div className="text-slate-500">No tenders available</div>
                    </td>
                  </tr>
                ) : (
                  tenders.map((tender) => (
                    <tr key={tender.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedIds.has(tender.id)}
                          onChange={() => handleToggleSelect(tender.id)}
                          className="w-4 h-4 rounded"
                        />
                      </td>
                      {columns.map((col) => (
                        <td key={String(col.key)} className="px-6 py-4 text-sm text-slate-700">
                          {col.render
                            ? col.render(tender[col.key], tender)
                            : String(tender[col.key] || '-')}
                        </td>
                      ))}
                      <td className="px-6 py-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() =>
                              handleMarkRelevant(tender.id, !tender.marked_relevant)
                            }
                            className="p-2 text-slate-600 hover:bg-slate-100 rounded transition-colors"
                            title={tender.marked_relevant ? 'Unmark as relevant' : 'Mark as relevant'}
                          >
                            {tender.marked_relevant ? (
                              <Eye size={18} className="text-green-600" />
                            ) : (
                              <EyeOff size={18} />
                            )}
                          </button>
                          <button
                            onClick={() => setSelectedTender(tender)}
                            className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                          >
                            View
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* Modals */}
      {selectedTender && (
        <TenderDetailModal
          tender={selectedTender}
          isOpen={!!selectedTender}
          onClose={() => setSelectedTender(null)}
        />
      )}

      <ConfirmDialog
        isOpen={deleteConfirm}
        onClose={() => setDeleteConfirm(false)}
        onConfirm={handleDeleteSelected}
        title="Delete Tender(s)"
        message="Are you sure you want to delete the selected tender(s)?"
        description="This action cannot be undone."
        confirmText="Delete"
        danger={true}
        requiresCheckbox={true}
        checkboxLabel="I understand this action is permanent and cannot be undone"
        itemCount={selectedIds.size}
      />
    </div>
  );
};
