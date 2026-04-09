"use client";

import { useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import MessageBubble, { Message } from "./MessageBubble";
import QuickReplies from "./QuickReplies";
import ResultCard from "./ResultCard";
import { sendMessage, logAction, ChatResponse } from "@/services/api";

const SESSION_ID = uuidv4();

const WELCOME_MESSAGE: Message = {
  id: "welcome",
  role: "assistant",
  content: "Xin chào! Tôi là trợ lý tuyển sinh Vinschool. Cho tôi biết tuổi của bé và khu vực bạn quan tâm nhé, tôi sẽ gợi ý chương trình và cơ sở phù hợp ngay!",
  timestamp: new Date(),
};

interface AssistantTurn {
  messageId: string;
  result: ChatResponse;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [results, setResults] = useState<Map<string, ChatResponse>>(new Map());
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(text?: string) {
    const messageText = (text || input).trim();
    if (!messageText || loading) return;

    setInput("");
    setShowQuickReplies(false);

    const userMsg: Message = {
      id: uuidv4(),
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const result = await sendMessage(messageText, SESSION_ID);
      const assistantId = uuidv4();
      const assistantMsg: Message = {
        id: assistantId,
        role: "assistant",
        content: result.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setResults((prev) => new Map(prev).set(assistantId, result));
    } catch {
      const errMsg: Message = {
        id: uuidv4(),
        role: "assistant",
        content: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }

  function handleCtaClick(label: string) {
    logAction(SESSION_ID, "accept_cta", label);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 chat-scrollbar">
        {messages.map((msg) => (
          <div key={msg.id}>
            <MessageBubble message={msg} />
            {msg.role === "assistant" && results.has(msg.id) && (
              <ResultCard
                data={results.get(msg.id)!.data}
                cta={results.get(msg.id)!.cta}
                sessionId={SESSION_ID}
                onCtaClick={handleCtaClick}
              />
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start mb-3 px-4">
            <div className="w-7 h-7 rounded-full bg-[#003087] flex items-center justify-center text-white text-xs font-bold mr-2">
              V
            </div>
            <div className="bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-gray-100">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick Replies */}
      {showQuickReplies && <QuickReplies onSelect={handleSend} />}

      {/* Input */}
      <div className="border-t border-gray-100 px-4 py-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Nhập câu hỏi (vd: Con tôi 7 tuổi ở Gia Lâm...)"
            className="flex-1 text-sm border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-[#003087] focus:ring-1 focus:ring-[#003087] transition-colors"
            disabled={loading}
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="bg-[#003087] text-white px-4 py-2.5 rounded-xl hover:bg-[#0057B8] transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 text-sm font-medium"
          >
            Gửi
          </button>
        </div>
      </div>
    </div>
  );
}
