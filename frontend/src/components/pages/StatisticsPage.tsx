import React, { useState, useEffect } from 'react';
import { BarChart3, Download } from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, ComposedChart,
} from 'recharts';
import { useTenders } from '../../hooks/useTenders';
import { Button } from '../ui/Button';
import { Card, CardHeader, CardBody } from '../ui/Card';
import { useNotification } from '../../context/NotificationContext';
import { getTopKeywords, generateTimestamp } from '../../lib/utils';

interface StatsSummary {
  totalTenders: number;
  relevantTenders: number;
  urgentTenders: number;
  avgDaysLeft: number;
  organizationCounts: Record<string, number>;
  typeCounts: Record<string, number>;
  sourceCounts: Record<string, number>;
  provinceCounts: Record<string, number>;
  keywordCounts: Array<{ keyword: string; count: number }>;
  daysLeftDistribution: Array<{ daysLeft: string; count: number; source: string }>;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#eab308'];

export const StatisticsPage: React.FC = () => {
  const { tenders, loading } = useTenders();
  const { addNotification } = useNotification();
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [viewMode, setViewMode] = useState<'all' | 'relevant'>('all');

  useEffect(() => {
    if (tenders.length > 0) {
      const filteredTenders = viewMode === 'relevant' ? tenders.filter((t) => t.marked_relevant) : tenders;

      const relevant = filteredTenders.filter((t) => t.marked_relevant);
      const urgent = filteredTenders.filter((t) => t.days_left !== null && t.days_left <= 5);
      const validDaysLeft = filteredTenders
        .filter((t) => t.days_left !== null)
        .map((t) => t.days_left || 0);
      const avgDays =
        validDaysLeft.length > 0
          ? Math.round(validDaysLeft.reduce((a, b) => a + b, 0) / validDaysLeft.length)
          : 0;

      const orgCounts: Record<string, number> = {};
      const typeCounts: Record<string, number> = {};
      const srcCounts: Record<string, number> = {};
      const provCounts: Record<string, number> = {};

      filteredTenders.forEach((t) => {
        orgCounts[t.organization] = (orgCounts[t.organization] || 0) + 1;
        typeCounts[t.procurement_type] = (typeCounts[t.procurement_type] || 0) + 1;
        srcCounts[t.source] = (srcCounts[t.source] || 0) + 1;
        if (t.province) {
          provCounts[t.province] = (provCounts[t.province] || 0) + 1;
        }
      });

      const keywordTitles = filteredTenders.map((t) => t.title);
      const topKeywords = getTopKeywords(keywordTitles, 10);

      const daysLeftBuckets: Record<string, Record<string, number>> = {};
      filteredTenders.forEach((t) => {
        const bucket =
          t.days_left === null
            ? 'Unknown'
            : t.days_left === 0
              ? '0 days'
              : t.days_left <= 5
                ? '1-5 days'
                : t.days_left <= 15
                  ? '6-15 days'
                  : t.days_left <= 30
                    ? '16-30 days'
                    : '30+ days';

        if (!daysLeftBuckets[bucket]) daysLeftBuckets[bucket] = {};
        daysLeftBuckets[bucket][t.source] = (daysLeftBuckets[bucket][t.source] || 0) + 1;
      });

      const daysLeftDistribution = Object.entries(daysLeftBuckets).flatMap(([bucket, sources]) =>
        Object.entries(sources).map(([source, count]) => ({
          daysLeft: bucket,
          count,
          source,
        }))
      );

      setStats({
        totalTenders: filteredTenders.length,
        relevantTenders: relevant.length,
        urgentTenders: urgent.length,
        avgDaysLeft: avgDays,
        organizationCounts: orgCounts,
        typeCounts: typeCounts,
        sourceCounts: srcCounts,
        provinceCounts: provCounts,
        keywordCounts: topKeywords,
        daysLeftDistribution,
      });
    }
  }, [tenders, viewMode]);

  const handleExportStats = () => {
    if (!stats) return;

    const content = `
TENDER MANAGEMENT STATISTICS
Generated: ${new Date().toLocaleString()}
Mode: ${viewMode === 'relevant' ? 'Relevant Tenders Only' : 'All Tenders'}

SUMMARY
Total Tenders: ${stats.totalTenders}
Relevant Tenders: ${stats.relevantTenders}
Urgent Tenders (≤5 days): ${stats.urgentTenders}
Average Days Left: ${stats.avgDaysLeft}

TOP ORGANIZATIONS
${Object.entries(stats.organizationCounts)
  .sort(([, a], [, b]) => b - a)
  .slice(0, 10)
  .map(([org, count]) => `${org}: ${count}`)
  .join('\n')}

PROCUREMENT TYPES
${Object.entries(stats.typeCounts)
  .map(([type, count]) => `${type}: ${count}`)
  .join('\n')}

SOURCES
${Object.entries(stats.sourceCounts)
  .map(([src, count]) => `${src}: ${count}`)
  .join('\n')}

PROVINCES
${Object.entries(stats.provinceCounts)
  .sort(([, a], [, b]) => b - a)
  .map(([prov, count]) => `${prov}: ${count}`)
  .join('\n')}

TOP KEYWORDS
${stats.keywordCounts
  .map(({ keyword, count }) => `${keyword}: ${count}`)
  .join('\n')}
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tender_statistics_${generateTimestamp()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    addNotification('success', 'Statistics exported successfully');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-slate-500">Loading...</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-slate-500">No data available</div>
      </div>
    );
  }

  const provinceChartData = Object.entries(stats.provinceCounts)
    .sort(([, a], [, b]) => b - a)
    .map(([prov, count]) => ({ name: prov, value: count }));

  const typeChartData = Object.entries(stats.typeCounts).map(([type, count]) => ({
    name: type,
    value: count,
  }));

  const sourceChartData = Object.entries(stats.sourceCounts).map(([source, count]) => ({
    name: source,
    value: count,
  }));

  const daysLeftChartData = [
    { bucket: '0 days', count: 0 },
    { bucket: '1-5 days', count: 0 },
    { bucket: '6-15 days', count: 0 },
    { bucket: '16-30 days', count: 0 },
    { bucket: '30+ days', count: 0 },
  ];

  stats.daysLeftDistribution.forEach(({ daysLeft, count }) => {
    const item = daysLeftChartData.find((d) => d.bucket === daysLeft);
    if (item) item.count += count;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="text-blue-600" />
            Statistics Dashboard
          </h1>
          <p className="text-slate-600 text-sm mt-1">Tender analytics and insights</p>
        </div>
        <Button variant="primary" size="sm" onClick={handleExportStats} icon={<Download size={18} />}>
          Export Stats
        </Button>
      </div>

      {/* View Mode Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setViewMode('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            viewMode === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
          }`}
        >
          All Tenders
        </button>
        <button
          onClick={() => setViewMode('relevant')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            viewMode === 'relevant'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
          }`}
        >
          Relevant Only
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardBody className="text-center">
            <p className="text-3xl font-bold text-blue-600">{stats.totalTenders}</p>
            <p className="text-sm text-slate-600 mt-1">Total Tenders</p>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <p className="text-3xl font-bold text-green-600">{stats.relevantTenders}</p>
            <p className="text-sm text-slate-600 mt-1">Relevant Tenders</p>
            <p className="text-xs text-slate-500 mt-2">
              {stats.totalTenders > 0
                ? Math.round((stats.relevantTenders / stats.totalTenders) * 100)
                : 0}
              % of total
            </p>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <p className="text-3xl font-bold text-red-600">{stats.urgentTenders}</p>
            <p className="text-sm text-slate-600 mt-1">Urgent Tenders</p>
            <p className="text-xs text-slate-500 mt-2">Deadline within 5 days</p>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <p className="text-3xl font-bold text-orange-600">{stats.avgDaysLeft}</p>
            <p className="text-sm text-slate-600 mt-1">Avg Days Left</p>
          </CardBody>
        </Card>
      </div>

      {/* Charts - Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Province Distribution - Pie Chart */}
        {provinceChartData.length > 0 && (
          <Card>
            <CardHeader className="border-b border-slate-200">
              <h3 className="font-semibold text-slate-900">Province Distribution</h3>
            </CardHeader>
            <CardBody className="flex items-center justify-center">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={provinceChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {provinceChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `${value} tender(s)`} />
                </PieChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
        )}

        {/* Procurement Types - Bar Chart */}
        <Card>
          <CardHeader className="border-b border-slate-200">
            <h3 className="font-semibold text-slate-900">Procurement Types</h3>
          </CardHeader>
          <CardBody className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={typeChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} interval={0} />
                <YAxis />
                <Tooltip formatter={(value: number) => `${value} tender(s)`} />
                <Bar dataKey="value" fill="#10b981" name="Count" />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </div>

      {/* Charts - Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Source Distribution - Bar Chart */}
        <Card>
          <CardHeader className="border-b border-slate-200"> 
            <h3 className="font-semibold text-slate-900">Source Distribution</h3>
          </CardHeader>
          <CardBody className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sourceChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip formatter={(value: number) => `${value} tender(s)`} />
                <Bar dataKey="value" fill="#f59e0b" name="Count" />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        {/* Days Left Distribution - Scatter Chart */}
        <Card>
          <CardHeader className="border-b border-slate-200">
            <h3 className="font-semibold text-slate-900">Days Left vs Source Distribution</h3>
          </CardHeader>
          <CardBody className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={daysLeftChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="bucket" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value: number) => `${value} tender(s)`} />
                <Bar dataKey="count" fill="#3b82f6" name="Tender Count" />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </div>

      {/* Keywords - Horizontal Bar Chart */}
      {stats.keywordCounts.length > 0 && (
        <Card>
          <CardHeader className="border-b border-slate-200">
            <h3 className="font-semibold text-slate-900">Top Keywords in Tender Titles</h3>
          </CardHeader>
          <CardBody className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={stats.keywordCounts}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="keyword" type="category" width={190} />
                <Tooltip formatter={(value: number) => `${value} occurrence(s)`} />
                <Bar dataKey="count" fill="#8b5cf6" name="Occurrences" />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      )}

      {/* Detailed Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Organizations */}
        <Card>
          <CardHeader className="border-b border-slate-200">
            <h3 className="font-semibold text-slate-900">Top Organizations</h3>
          </CardHeader>
          <CardBody>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {Object.entries(stats.organizationCounts)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 8)
                .map(([org, count]) => (
                  <div key={org} className="flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{org}</p>
                    </div>
                    <div className="flex-1 bg-slate-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-blue-600 h-full"
                        style={{
                          width: `${(count / Math.max(...Object.values(stats.organizationCounts))) * 100}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-semibold text-slate-900 w-8 text-right">{count}</span>
                  </div>
                ))}
            </div>
          </CardBody>
        </Card>

        {/* Statistics Summary */}
        <Card>
          <CardHeader className="border-b border-slate-200">
            <h3 className="font-semibold text-slate-900">Statistics Summary</h3>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-slate-200">
                <span className="text-sm text-slate-600">Unique Organizations</span>
                <span className="font-semibold text-slate-900">{Object.keys(stats.organizationCounts).length}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-slate-200">
                <span className="text-sm text-slate-600">Procurement Types</span>
                <span className="font-semibold text-slate-900">{Object.keys(stats.typeCounts).length}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-slate-200">
                <span className="text-sm text-slate-600">Sources</span>
                <span className="font-semibold text-slate-900">{Object.keys(stats.sourceCounts).length}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-slate-200">
                <span className="text-sm text-slate-600">Provinces</span>
                <span className="font-semibold text-slate-900">{Object.keys(stats.provinceCounts).length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600">Urgent Percentage</span>
                <span className="font-semibold text-slate-900">
                  {stats.totalTenders > 0
                    ? Math.round((stats.urgentTenders / stats.totalTenders) * 100)
                    : 0}
                  %
                </span>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};
