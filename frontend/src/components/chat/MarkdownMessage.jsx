import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function MarkdownMessage({ content }) {
  if (!content) return null;

  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ node, ...props }) => (
            <div className="md-table-wrapper">
              <table className="md-table" {...props} />
            </div>
          ),
          th: ({ node, ...props }) => <th className="md-th" {...props} />,
          td: ({ node, ...props }) => <td className="md-td" {...props} />,
          code: ({ node, inline, ...props }) =>
            inline ? (
              <code className="md-inline-code" {...props} />
            ) : (
              <pre className="md-block-code">
                <code {...props} />
              </pre>
            ),
          p: ({ node, ...props }) => <p className="md-p" {...props} />,
          ul: ({ node, ...props }) => <ul className="md-ul" {...props} />,
          li: ({ node, ...props }) => <li className="md-li" {...props} />,
          strong: ({ node, ...props }) => <strong className="md-strong" {...props} />,
          h1: ({ node, ...props }) => <h3 className="md-heading" {...props} />,
          h2: ({ node, ...props }) => <h4 className="md-heading" {...props} />,
          h3: ({ node, ...props }) => <h5 className="md-heading" {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
