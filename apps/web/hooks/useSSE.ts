'use client';
import { useEffect, useRef, useState, useCallback } from 'react';

interface SSEOptions {
  onMessage?: (data: unknown) => void;
  onError?: (err: Event) => void;
  enabled?: boolean;
}

export function useSSE(url: string | null, options: SSEOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const esRef = useRef<EventSource | null>(null);
  const { onMessage, onError, enabled = true } = options;

  const connect = useCallback(() => {
    if (!url || !enabled) return;
    
    if (esRef.current) {
      esRef.current.close();
    }
    
    const es = new EventSource(url);
    esRef.current = es;
    
    es.onopen = () => { setIsConnected(true); setError(null); };
    es.onerror = (e) => {
      setIsConnected(false);
      setError('Connection error');
      onError?.(e);
    };
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setLastEvent(data);
        onMessage?.(data);
      } catch {
        setLastEvent(e.data);
        onMessage?.(e.data);
      }
    };
    
    return () => { es.close(); };
  }, [url, enabled, onMessage, onError]);

  useEffect(() => {
    const cleanup = connect();
    return () => {
      cleanup?.();
      esRef.current?.close();
      setIsConnected(false);
    };
  }, [connect]);

  const close = useCallback(() => {
    esRef.current?.close();
    setIsConnected(false);
  }, []);

  return { isConnected, lastEvent, error, close };
}
