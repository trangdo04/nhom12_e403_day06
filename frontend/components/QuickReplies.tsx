"use client";

interface Props {
  onSelect: (text: string) => void;
}

const QUICK_REPLIES = [
  "Con tôi 5 tuổi, ở Ocean Park",
  "Con tôi 8 tuổi, khu vực Hà Nội",
  "Con tôi 12 tuổi, ở TP.HCM",
  "Xem học phí các cấp",
  "Cách đăng ký tuyển sinh",
];

export default function QuickReplies({ onSelect }: Props) {
  return (
    <div className="px-4 pb-2">
      <p className="text-xs text-gray-400 mb-2">Gợi ý nhanh:</p>
      <div className="flex flex-wrap gap-2">
        {QUICK_REPLIES.map((reply) => (
          <button
            key={reply}
            onClick={() => onSelect(reply)}
            className="text-xs bg-blue-50 text-[#003087] border border-blue-200 rounded-full px-3 py-1.5 hover:bg-blue-100 transition-colors"
          >
            {reply}
          </button>
        ))}
      </div>
    </div>
  );
}
