"use client";

import ReactMarkdown from "react-markdown";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  streaming?: boolean;
}

interface Props {
  message: Message;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3 px-4`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-[#003087] flex items-center justify-center text-white text-xs font-bold mr-2 flex-shrink-0 mt-1">
          V
        </div>
      )}
      <div
        className={`max-w-[78%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-[#003087] text-white rounded-tr-sm"
            : "bg-white text-gray-800 rounded-tl-sm shadow-sm border border-gray-100"
        }`}
      >
        {isUser ? (
          <span>{message.content}</span>
        ) : (
          <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0.5 prose-strong:text-[#003087] prose-a:text-[#0057B8] prose-a:no-underline hover:prose-a:underline prose-headings:text-gray-800">
            <ReactMarkdown
              components={{
                // Paragraphs
                p: ({ children }) => <p className="mb-1.5 last:mb-0">{children}</p>,
                // Bold
                strong: ({ children }) => (
                  <strong className="font-semibold text-[#003087]">{children}</strong>
                ),
                // Bullet lists
                ul: ({ children }) => (
                  <ul className="list-none space-y-1 my-1.5 pl-0">{children}</ul>
                ),
                li: ({ children }) => (
                  <li className="flex items-start gap-1.5">
                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#003087] flex-shrink-0" />
                    <span>{children}</span>
                  </li>
                ),
                // Ordered lists
                ol: ({ children }) => (
                  <ol className="list-decimal pl-5 space-y-1 my-1.5">{children}</ol>
                ),
                // Links
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#0057B8] underline"
                  >
                    {children}
                  </a>
                ),
                // Code inline
                code: ({ children }) => (
                  <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-700">
                    {children}
                  </code>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
            {message.streaming && (
              <span className="inline-block w-0.5 h-4 bg-[#003087] ml-0.5 animate-pulse align-middle" />
            )}
          </div>
        )}
      </div>
      {isUser && (
        <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs font-bold ml-2 flex-shrink-0 mt-1">
          B
        </div>
      )}
    </div>
  );
}
