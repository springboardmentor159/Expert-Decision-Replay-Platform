import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback((type, message, duration = 4000) => {
    const id = Date.now().toString() + Math.random().toString(36).substring(2, 5);
    setToasts((prev) => [...prev, { id, type, message }]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
    return id;
  }, [removeToast]);

  const toast = useMemo(() => ({
    success: (msg, dur) => addToast('success', msg, dur),
    error: (msg, dur) => addToast('error', msg, dur),
    warning: (msg, dur) => addToast('warning', msg, dur),
    info: (msg, dur) => addToast('info', msg, dur),
  }), [addToast]);

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {/* Toast Container */}
      <div
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          maxWidth: '420px',
          pointerEvents: 'none',
        }}
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            style={{
              pointerEvents: 'auto',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              padding: '14px 18px',
              borderRadius: 'var(--radius-md)',
              backgroundColor:
                t.type === 'error'
                  ? 'var(--status-rejected-bg)'
                  : t.type === 'success'
                  ? 'var(--status-approved-bg)'
                  : t.type === 'warning'
                  ? 'var(--status-review-bg)'
                  : 'var(--color-canvas)',
              color:
                t.type === 'error'
                  ? 'var(--status-rejected-text)'
                  : t.type === 'success'
                  ? 'var(--status-approved-text)'
                  : t.type === 'warning'
                  ? 'var(--status-review-text)'
                  : 'var(--color-ink)',
              border: `1px solid ${
                t.type === 'error'
                  ? 'rgba(220, 38, 38, 0.2)'
                  : t.type === 'success'
                  ? 'rgba(5, 150, 105, 0.2)'
                  : t.type === 'warning'
                  ? 'rgba(217, 119, 6, 0.2)'
                  : 'var(--color-hairline)'
              }`,
              boxShadow: 'var(--shadow-modal)',
              fontSize: '14px',
              fontWeight: 500,
              animation: 'slideIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {t.type === 'success' && <CheckCircle2 size={18} />}
              {t.type === 'error' && <AlertCircle size={18} />}
              {t.type === 'warning' && <AlertTriangle size={18} />}
              {t.type === 'info' && <Info size={18} />}
              <span>{t.message}</span>
            </div>
            <button
              onClick={() => removeToast(t.id)}
              style={{
                color: 'inherit',
                opacity: 0.6,
                padding: '2px',
                display: 'flex',
                alignItems: 'center',
              }}
              aria-label="Close notification"
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
