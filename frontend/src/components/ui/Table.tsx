import React from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
  width?: string;
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  onSort?: (key: keyof T) => void;
  sortBy?: keyof T;
  sortOrder?: 'asc' | 'desc';
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  rowClassName?: (row: T) => string;
}

export const Table = React.forwardRef<HTMLDivElement, TableProps<any>>(
  (
    {
      data,
      columns,
      onSort,
      sortBy,
      sortOrder = 'asc',
      loading = false,
      emptyMessage = 'No data available',
      onRowClick,
      rowClassName,
    },
    ref
  ) => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="text-slate-500">Loading...</div>
        </div>
      );
    }

    if (data.length === 0) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="text-slate-500">{emptyMessage}</div>
        </div>
      );
    }

    return (
      <div ref={ref} className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className={`px-6 py-3 text-left text-sm font-semibold text-slate-900 ${
                    column.width ? `w-[${column.width}]` : ''
                  }`}
                >
                  {column.sortable ? (
                    <button
                      onClick={() => onSort?.(column.key)}
                      className="flex items-center gap-2 hover:text-slate-700 transition-colors"
                    >
                      {column.label}
                      {sortBy === column.key && (
                        <>
                          {sortOrder === 'asc' ? (
                            <ChevronUp size={16} />
                          ) : (
                            <ChevronDown size={16} />
                          )}
                        </>
                      )}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`
                  border-b border-slate-100 transition-colors duration-200
                  ${onRowClick ? 'hover:bg-slate-50 cursor-pointer' : ''}
                  ${rowClassName?.(row) || ''}
                `}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => (
                  <td key={String(column.key)} className="px-6 py-4 text-sm text-slate-700">
                    {column.render
                      ? column.render(row[column.key], row)
                      : String(row[column.key] || '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
);

Table.displayName = 'Table';
