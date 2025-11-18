import React, { useEffect } from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';
import { Notification } from '../../context/NotificationContext';

interface ToastProps extends Notification {
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ id, type, message, duration = 5000, onClose }) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const styles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const icons = {
    success: <CheckCircle2 size={20} className="text-green-600 flex-shrink-0" />,
    error: <AlertCircle size={20} className="text-red-600 flex-shrink-0" />,
    info: <Info size={20} className="text-blue-600 flex-shrink-0" />,
  };

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${styles[type]} animate-slide-in`}
      role="alert"
      aria-live="polite"
    >
      {icons[type]}
      <p className="flex-1 text-sm font-medium">{message}</p>
      <button
        onClick={onClose}
        className="text-slate-500 hover:text-slate-700 transition-colors"
        aria-label="Close notification"
      >
        <X size={18} />
      </button>
    </div>
  );
};
