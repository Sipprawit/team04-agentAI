import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check } from 'lucide-react';

export default function MarkdownMessage({ content, allowCopy = true }) {
  const [copied, setCopied] = useState(false);

  if (!content) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  return (
    <div className="markdown-content-wrapper">
      <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ node: _node, ...props }) => (
            <div className="md-table-wrapper">
              <table className="md-table" {...props} />
            </div>
          ),
          th: ({ node: _node, ...props }) => <th className="md-th" {...props} />,
          td: ({ node: _node, ...props }) => <td className="md-td" {...props} />,
          code: ({ node: _node, inline, ...props }) =>
            inline ? (
              <code className="md-inline-code" {...props} />
            ) : (
              <pre className="md-block-code">
                <code {...props} />
              </pre>
            ),
          p: ({ node: _node, ...props }) => <p className="md-p" {...props} />,
          ul: ({ node: _node, ...props }) => <ul className="md-ul" {...props} />,
          li: ({ node: _node, ...props }) => <li className="md-li" {...props} />,
          strong: ({ node: _node, ...props }) => <strong className="md-strong" {...props} />,
          h1: ({ node: _node, ...props }) => <h3 className="md-heading" {...props} />,
          h2: ({ node: _node, ...props }) => <h4 className="md-heading" {...props} />,
          h3: ({ node: _node, ...props }) => <h5 className="md-heading" {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
      </div>
      {allowCopy && (
        <div className="markdown-actions">
          <button
            type="button"
            className={`markdown-copy-btn ${copied ? 'copied' : ''}`}
            onClick={handleCopy}
            title={copied ? 'คัดลอกเรียบร้อยแล้ว' : 'คัดลอกข้อความสรุป'}
          >
            {copied ? <Check size={13} className="text-emerald-500" /> : <Copy size={13} />}
            <span>{copied ? 'คัดลอกแล้ว' : 'คัดลอก'}</span>
          </button>
        </div>
      )}
    </div>
  );
}
