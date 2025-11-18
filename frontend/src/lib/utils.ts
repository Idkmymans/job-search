export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const calculateDaysLeft = (deadline: string): number => {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const diffTime = deadlineDate.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return Math.max(0, diffDays);
};

export const getUrgencyColor = (daysLeft: number | null): string => {
  if (daysLeft === null) return 'gray';
  if (daysLeft <= 5) return 'red';
  if (daysLeft <= 15) return 'orange';
  return 'green';
};

export const getUrgencyBgClass = (daysLeft: number | null): string => {
  if (daysLeft === null) return 'bg-gray-100';
  if (daysLeft <= 5) return 'bg-red-50';
  if (daysLeft <= 15) return 'bg-orange-50';
  return 'bg-green-50';
};

export const getUrgencyTextClass = (daysLeft: number | null): string => {
  if (daysLeft === null) return 'text-gray-700';
  if (daysLeft <= 5) return 'text-red-700';
  if (daysLeft <= 15) return 'text-orange-700';
  return 'text-green-700';
};

export const getUrgencyBadgeClass = (daysLeft: number | null): string => {
  if (daysLeft === null) return 'bg-gray-200 text-gray-800';
  if (daysLeft <= 5) return 'bg-red-200 text-red-800';
  if (daysLeft <= 15) return 'bg-orange-200 text-orange-800';
  return 'bg-green-200 text-green-800';
};

export const generateCSVContent = (
  tenders: any[],
  columns: string[]
): string => {
  const headers = columns.join(',');
  const rows = tenders.map((tender) =>
    columns
      .map((col) => {
        const value = tender[col];
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value || '';
      })
      .join(',')
  );
  return [headers, ...rows].join('\n');
};

export const downloadFile = (
  content: string,
  filename: string,
  type: string = 'text/csv'
) => {
  const blob = new Blob([content], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const generateTimestamp = (): string => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
};

export const parseDateForDisplay = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return dateString;
    }
    return formatDateTime(dateString);
  } catch {
    return dateString;
  }
};

export const extractKeywords = (text: string, minLength = 4): string[] => {
  if (!text) return [];

  const stopWords = new Set([
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
    'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i',
    'you', 'he', 'she', 'it', 'we', 'they', 'all', 'each', 'every', 'both',
    'such', 'no', 'not', 'only', 'very', 'too', 'than', 'if', 'just', 'about',
  ]);

  const words = text
    .toLowerCase()
    .match(/\b[\w]+\b/g) || [];

  return words
    .filter((word) => word.length >= minLength && !stopWords.has(word))
    .filter((word) => !/^\d+$/.test(word));
};

export const getKeywordFrequency = (texts: string[]): Record<string, number> => {
  const frequency: Record<string, number> = {};

  texts.forEach((text) => {
    const keywords = extractKeywords(text);
    keywords.forEach((keyword) => {
      frequency[keyword] = (frequency[keyword] || 0) + 1;
    });
  });

  return frequency;
};

export const getTopKeywords = (
  texts: string[],
  limit = 10
): Array<{ keyword: string; count: number }> => {
  const frequency = getKeywordFrequency(texts);

  return Object.entries(frequency)
    .map(([keyword, count]) => ({ keyword, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
};
