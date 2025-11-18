import React, { useState, useEffect } from 'react';
import { Eye, Search, Filter } from 'lucide-react';
import { useTenders } from '../../hooks/useTenders';
import { TenderFilter, Tender } from '../../types';
import { Table } from '../ui/Table';
import { Button } from '../ui/Button';
import { Card, CardHeader, CardBody } from '../ui/Card';
import { useNotification } from '../../context/NotificationContext';
import {
  formatDate,
  getUrgencyBadgeClass,
  calculateDaysLeft,
} from '../../lib/utils';
import { TenderDetailModal } from './modals/TenderDetailModal';
import { SearchFilterPanel } from './SearchFilterPanel';

export const RelevantTendersPage: React.FC = () => {
  const { tenders, loading, error, fetchTenders, markRelevant } = useTenders();
  const { addNotification } = useNotification();
  const [filter, setFilter] = useState<TenderFilter>({});
  const [showFilters, setShowFilters] = useState(false);
  const [selectedTender, setSelectedTender] = useState<Tender | null>(null);
  const [sortBy, setSortBy] = useState<'deadline' | 'days_left'>('days_left');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    fetchTenders(filter, true);
  }, [filter]);

  const handleSort = (key: any) => {
    if (sortBy === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(key);
      setSortOrder('asc');
    }
  };

  const handleMarkNonRelevant = async (tenderId: string) => {
    try {
      await markRelevant(tenderId, false);
      addNotification('success', 'Tender unmarked as relevant');
      await fetchTenders(filter, true);
    } catch (err) {
      addNotification('error', 'Failed to update tender');
    }
  };

  const relevantTenders = tenders.filter((t) => t.marked_relevant);

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
      key: 'deadline' as const,
      label: 'Deadline',
      sortable: true,
      render: (value: string) => formatDate(value),
    },
    {
      key: 'days_left' as const,
      label: 'Days Left',
      sortable: true,
      render: (value: number | null, row: Tender) => (
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getUrgencyBadgeClass(value)}`}>
          {value !== null ? `${value}d` : 'N/A'}
        </span>
      ),
    },
    {
      key: 'procurement_type' as const,
      label: 'Type',
      render: (value: string) => (
        <span className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded">{value}</span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
            <Eye className="text-blue-600" />
            Relevant Tenders
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            {relevantTenders.length} tender{relevantTenders.length !== 1 ? 's' : ''} marked as relevant
          </p>
        </div>
        <Button
          variant="secondary"
          icon={<Filter size={18} />}
          onClick={() => setShowFilters(!showFilters)}
        >
          Filter
        </Button>
      </div>

      {/* Search and Filter Panel */}
      {showFilters && (
        <SearchFilterPanel
          onFilterChange={setFilter}
          onClose={() => setShowFilters(false)}
        />
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardBody className="text-red-700 text-sm">{error}</CardBody>
        </Card>
      )}

      {/* Tenders Table */}
      <Card>
        <CardHeader className="flex items-center justify-between">
          <h2 className="font-semibold text-slate-900">Tender Listings</h2>
          <span className="text-sm text-slate-600">{relevantTenders.length} results</span>
        </CardHeader>
        <CardBody className="p-0">
          <Table
            data={relevantTenders}
            columns={columns}
            loading={loading}
            emptyMessage="No relevant tenders found"
            onRowClick={(tender) => setSelectedTender(tender)}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSort={handleSort}
          />
        </CardBody>
      </Card>

      {/* Tender Detail Modal */}
      {selectedTender && (
        <TenderDetailModal
          tender={selectedTender}
          isOpen={!!selectedTender}
          onClose={() => setSelectedTender(null)}
          onUnmarkRelevant={() => {
            handleMarkNonRelevant(selectedTender.id);
            setSelectedTender(null);
          }}
        />
      )}
    </div>
  );
};
