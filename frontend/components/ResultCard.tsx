"use client";

import { CtaItem, ChatData } from "@/services/api";

interface Props {
  data: ChatData;
  cta: CtaItem[];
  sessionId: string;
  onCtaClick?: (label: string) => void;
}

export default function ResultCard({ data, cta, onCtaClick }: Props) {
  if (!data.level && data.campuses.length === 0) return null;

  return (
    <div className="mx-4 mb-3 bg-blue-50 border border-blue-200 rounded-xl p-4">
      {/* Cấp học */}
      {data.level && (
        <div className="mb-3">
          <span className="text-xs text-gray-500 uppercase tracking-wide">Cấp học phù hợp</span>
          <div className="mt-1">
            <span className="inline-block bg-[#003087] text-white text-sm font-semibold px-3 py-1 rounded-full">
              {data.level}
            </span>
          </div>
        </div>
      )}

      {/* Cơ sở */}
      {data.campuses.length > 0 && (
        <div className="mb-3">
          <span className="text-xs text-gray-500 uppercase tracking-wide">Cơ sở gợi ý</span>
          <div className="mt-1 space-y-1">
            {data.campuses.map((campus) => (
              <a
                key={campus.name}
                href={campus.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-1.5 text-sm text-[#0057B8] hover:underline"
              >
                <span className="mt-0.5">📍</span>
                <span>
                  <strong>{campus.name}</strong>
                  <span className="text-gray-500 font-normal"> — {campus.address}</span>
                </span>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* CTA Buttons */}
      {cta.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-blue-200">
          {cta.map((item) => (
            <a
              key={item.label}
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => onCtaClick?.(item.label)}
              className="text-xs bg-white border border-[#003087] text-[#003087] px-3 py-1.5 rounded-lg hover:bg-[#003087] hover:text-white transition-colors font-medium"
            >
              {item.label}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
