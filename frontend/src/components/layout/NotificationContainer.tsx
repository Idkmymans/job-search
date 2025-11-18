import React from 'react';
import { Toast } from '../ui/Toast';
import { useNotification } from '../../context/NotificationContext';

export const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotification();

  return (
    <div
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-3 max-w-sm pointer-events-none"
      role="region"
      aria-live="polite"
      aria-label="Notifications"
    >
      {notifications.map((notification) => (
        <div key={notification.id} className="pointer-events-auto">
          <Toast
            {...notification}
            onClose={() => removeNotification(notification.id)}
          />
        </div>
      ))}
    </div>
  );
};
