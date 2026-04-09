"use client";

import { useState } from "react";
import ChatWindow from "./ChatWindow";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Chat Panel */}
      {open && (
        <div className="mb-3 w-[calc(100vw-3rem)] sm:w-[380px] h-[500px] sm:h-[560px] bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-gray-100 flex flex-col overflow-hidden animate-in slide-in-from-bottom-2 fade-in duration-200 origin-bottom-right">
          {/* Header */}
          <div className="bg-[#003087] text-white px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center">
                <span className="text-[#003087] font-bold text-sm">V</span>
              </div>
              <div>
                <div className="font-semibold text-sm">Vinschool Tuyển sinh</div>
                <div className="flex items-center gap-1 text-xs text-blue-200">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
                  Trực tuyến
                </div>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="w-7 h-7 rounded-full hover:bg-blue-800 flex items-center justify-center transition-colors text-lg leading-none"
              aria-label="Đóng chat"
            >
              ×
            </button>
          </div>

          {/* Chat Content */}
          <div className="flex-1 overflow-hidden relative">
            <ChatWindow />
          </div>
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="w-14 h-14 bg-[#003087] hover:bg-[#0057B8] text-white rounded-full shadow-[0_4px_14px_0_rgba(0,48,135,0.39)] hover:shadow-[0_6px_20px_rgba(0,48,135,0.23)] flex items-center justify-center transition-all duration-300 hover:scale-105 active:scale-95"
        aria-label="Mở chat tư vấn tuyển sinh"
      >
        {open ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>

      {/* Badge khi chưa mở */}
      {!open && (
        <div className="absolute -top-1 -right-1 w-5 h-5 bg-[#F5A623] rounded-full flex items-center justify-center">
          <span className="text-white text-xs font-bold">1</span>
        </div>
      )}
    </div>
  );
}
