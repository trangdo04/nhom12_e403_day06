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
  showAvatar?: boolean;
}

export default function MessageBubble({ message, showAvatar = true }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3 px-4`}>
      {!isUser && (
        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0 mt-1 ${showAvatar ? "bg-[#003087] text-white" : "bg-transparent opacity-0"}`}>
          {showAvatar ? "V" : ""}
        </div>
      )}
      <div
        className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
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
                p: ({ children }) => <p className="mb-1.5 last:mb-0">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold text-[#003087]">{children}</strong>,
                ul: ({ children }) => <ul className="list-none space-y-1 my-1.5 pl-0">{children}</ul>,
                li: ({ children }) => (
                  <li className="flex items-start gap-1.5">
                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#003087] flex-shrink-0" />
                    <span>{children}</span>
                  </li>
                ),
                ol: ({ children }) => <ol className="list-decimal pl-5 space-y-1 my-1.5">{children}</ol>,
                a: ({ href, children }) => (
                  <a href={href} target="_blank" rel="noopener noreferrer" className="text-[#0057B8] underline">{children}</a>
                ),
                code: ({ children }) => <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-700">{children}</code>,
              }}
            >
              {message.content}
            </ReactMarkdown>
            {message.streaming && (
              <span className="inline-block w-1.5 h-4 bg-[#003087] ml-1 animate-pulse align-middle rounded-sm" />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
