import React, { useState } from 'react';
import { Code, Copy, Check, Sparkles, Info } from 'lucide-react';

export default function SqlSnippetBox({ sql, explanation, confidence }) {
  const [copied, setCopied] = useState(false);

  if (!sql) return null;

  const handleCopy = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    let success = false;
    if (navigator?.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(sql);
        success = true;
      } catch {
        // Fallback below
      }
    }
    if (!success) {
      try {
        const textArea = document.createElement('textarea');
        textArea.value = sql;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        textArea.style.top = '-9999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        success = document.execCommand('copy');
        document.body.removeChild(textArea);
      } catch (err) {
        console.error('Copy fallback failed:', err);
      }
    }
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <details className="sql-snippet-box">
      <summary>
        <div className="sql-snippet-summary-left">
          <Code size={13} />
          <span>คำสั่ง SQL ที่ใช้ประมวลผล</span>
          <span className="sql-dialect-tag">SQLite</span>
          {confidence && (
            <span className={`sql-confidence-tag confidence-${confidence.level}`}>
              <Sparkles size={10} />
              <span>{confidence.label}</span>
            </span>
          )}
        </div>
        <button
          type="button"
          className={`sql-copy-btn ${copied ? 'copied' : ''}`}
          onClick={handleCopy}
          title={copied ? 'คัดลอกเรียบร้อยแล้ว' : 'คัดลอกคำสั่ง SQL'}
        >
          {copied ? <Check size={12} /> : <Copy size={12} />}
          <span>{copied ? 'คัดลอกแล้ว' : 'คัดลอก SQL'}</span>
        </button>
      </summary>
      <div className="sql-code-container">
        {explanation && (
          <div className="sql-explanation-banner">
            <Info size={13} className="text-blue-500 flex-shrink-0" />
            <span>{explanation}</span>
          </div>
        )}
        <pre className="sql-code-display">{sql}</pre>
      </div>
    </details>
  );
}
