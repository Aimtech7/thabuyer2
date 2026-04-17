import { useEffect } from 'react';
import { useStore } from '@/store/useStore';
import { wsClient } from '@/services/django/websocket';

export const useNotifications = () => {
  const { isAuthenticated, notifications, clearNotifications } = useStore();

  useEffect(() => {
    if (isAuthenticated) {
      wsClient.connect();
    } else {
      wsClient.disconnect();
    }

    return () => {
      // We don't necessarily want to disconnect on every unmount if the app is still active
      // but for standard hook usage, cleanup is good.
    };
  }, [isAuthenticated]);

  return {
    notifications,
    clearNotifications,
  };
};
