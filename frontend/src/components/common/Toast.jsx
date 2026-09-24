import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Pin, Database, Info, X } from 'lucide-react';

function SingleToast({ toast, onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, toast.duration || 3500);
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle2 size={18} className="text-emerald-500" />;
      case 'pin':
        return <Pin size={18} className="text-blue-500" />;
      case 'upload':
        return <Database size={18} className="text-purple-500" />;
      case 'error':
        return <AlertCircle size={18} className="text-red-500" />;
      default:
        return <Info size={18} className="text-blue-500" />;
    }
  };

  return (
    <div className={`floating-toast-container toast-${toast.type || 'info'}`}>
      <div className="toast-icon-box">{getIcon()}</div>
      <div className="toast-body">
        <div className="toast-title">{toast.title || 'แจ้งเตือนระบบ'}</div>
        <div className="toast-message">{toast.message}</div>
      </div>
      <button onClick={onClose} className="toast-close-btn" aria-label="ปิดการแจ้งเตือน">
        <X size={14} />
      </button>
    </div>
  );
}

export default function Toast({ toast, toasts, onClose, onRemove }) {
  const items = toasts || (toast ? [toast] : []);

  if (items.length === 0) return null;

  return (
    <div className="floating-toasts-wrapper">
      {items.map((item, idx) => (
        <SingleToast
          key={item.id || idx}
          toast={item}
          onClose={() => {
            if (onRemove && item.id) onRemove(item.id);
            else if (onClose) onClose();
          }}
        />
      ))}
    </div>
  );
}
