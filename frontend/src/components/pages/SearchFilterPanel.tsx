import React, { useState } from 'react';
import { X } from 'lucide-react';
import { TenderFilter } from '../../types';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Card, CardBody } from '../ui/Card';

const PROCUREMENT_TYPES = ['works ncb', 'goods ncb', 'services ncb', 'works', 'goods', 'services'];
const PROVINCES = ['Not specified', 'Bagmati', 'Gandaki', 'Lumbini', 'Province 1', 'Province 2'];
const SOURCES = ['Bolpatra', 'Manual'];

interface SearchFilterPanelProps {
  onFilterChange: (filter: TenderFilter) => void;
  onClose: () => void;
}

export const SearchFilterPanel: React.FC<SearchFilterPanelProps> = ({
  onFilterChange,
  onClose,
}) => {
  const [keyword, setKeyword] = useState('');
  const [daysLeftMin, setDaysLeftMin] = useState(0);
  const [daysLeftMax, setDaysLeftMax] = useState(365);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedProvinces, setSelectedProvinces] = useState<string[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const handleApplyFilters = () => {
    const filter: TenderFilter = {
      keyword: keyword || undefined,
      days_left_min: daysLeftMin,
      days_left_max: daysLeftMax,
      procurement_type: selectedTypes.length > 0 ? selectedTypes : undefined,
      province: selectedProvinces.length > 0 ? selectedProvinces : undefined,
      source: selectedSources.length > 0 ? selectedSources : undefined,
    };
    onFilterChange(filter);
  };

  const handleClearFilters = () => {
    setKeyword('');
    setDaysLeftMin(0);
    setDaysLeftMax(365);
    setSelectedTypes([]);
    setSelectedProvinces([]);
    setSelectedSources([]);
    onFilterChange({});
  };

  const toggleSelection = (item: string, list: string[], setList: (list: string[]) => void) => {
    if (list.includes(item)) {
      setList(list.filter((i) => i !== item));
    } else {
      setList([...list, item]);
    }
  };

  return (
    <Card>
      <CardBody>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-900">Advanced Filters</h3>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700"
            aria-label="Close filters"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          {/* Keyword Search */}
          <div>
            <Input
              label="Keyword Search"
              placeholder="Search by title, IFB No, or organization"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
          </div>

          {/* Days Left Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Days Left (Min)</label>
              <input
                type="number"
                min="0"
                max="365"
                value={daysLeftMin}
                onChange={(e) => setDaysLeftMin(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Days Left (Max)</label>
              <input
                type="number"
                min="0"
                max="365"
                value={daysLeftMax}
                onChange={(e) => setDaysLeftMax(parseInt(e.target.value) || 365)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Procurement Type */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Procurement Type</label>
            <div className="grid grid-cols-2 gap-2">
              {PROCUREMENT_TYPES.map((type) => (
                <label key={type} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedTypes.includes(type)}
                    onChange={() => toggleSelection(type, selectedTypes, setSelectedTypes)}
                    className="w-4 h-4 rounded border-slate-300"
                  />
                  <span className="text-sm text-slate-700">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Province */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Province</label>
            <div className="grid grid-cols-2 gap-2">
              {PROVINCES.map((province) => (
                <label key={province} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedProvinces.includes(province)}
                    onChange={() => toggleSelection(province, selectedProvinces, setSelectedProvinces)}
                    className="w-4 h-4 rounded border-slate-300"
                  />
                  <span className="text-sm text-slate-700">{province}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Source */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Source</label>
            <div className="space-y-2">
              {SOURCES.map((source) => (
                <label key={source} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source)}
                    onChange={() => toggleSelection(source, selectedSources, setSelectedSources)}
                    className="w-4 h-4 rounded border-slate-300"
                  />
                  <span className="text-sm text-slate-700">{source}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-slate-200">
            <Button variant="primary" onClick={handleApplyFilters} className="flex-1">
              Apply Filters
            </Button>
            <Button variant="secondary" onClick={handleClearFilters} className="flex-1">
              Clear All
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
