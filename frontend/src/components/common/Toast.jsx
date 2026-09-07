import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Pin, Database, Info, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        onClose();
      }, toast.duration || 3200);
      return () => clearTimeout(timer);
    }
  }, [toast, onClose]);

  if (!toast) return null;

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
      <button onClick={onClose} className="toast-close-btn">
        <X size={14} />
      </button>
    </div>
  );
}
