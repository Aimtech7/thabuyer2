import { useStore } from '@/store/useStore';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

class WebSocketClient {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 3000;
  private isConnected = false;

  connect() {
    if (this.isConnected || this.socket?.readyState === WebSocket.OPEN) return;

    const token = localStorage.getItem('tha_access_token');
    if (!token) {
      console.warn('No access token found for WebSocket connection');
      return;
    }

    // Full URL: ws://localhost:8000/ws/notifications/?token=...
    const url = `${WS_URL}/notifications/?token=${token}`;
    
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log('✅ Connected to real-time notifications');
      this.reconnectAttempts = 0;
      this.isConnected = true;
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { addNotification } = useStore.getState();
        addNotification(data);
      } catch (err) {
        console.error('❌ Failed to parse socket message', err);
      }
    };

    this.socket.onclose = (event) => {
      this.isConnected = false;
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        console.log(`⚠️ Socket closed. Reconnecting attempt ${this.reconnectAttempts + 1}...`);
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, this.reconnectTimeout * Math.pow(2, this.reconnectAttempts));
      } else if (!event.wasClean) {
        console.error('❌ Max reconnection attempts reached');
      }
    };

    this.socket.onerror = (err) => {
      console.error('❌ Socket error:', err);
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }
}

export const wsClient = new WebSocketClient();
