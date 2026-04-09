const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface CampusInfo {
  name: string;
  address: string;
  url: string;
}

export interface ChatData {
  age: number | null;
  area: string | null;
  level: string | null;
  campuses: CampusInfo[];
}

export interface CtaItem {
  label: string;
  url: string;
}

export interface ChatResponse {
  response: string;
  data: ChatData;
  cta: CtaItem[];
}

export async function sendMessage(message: string, sessionId: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export async function logAction(
  sessionId: string,
  action: "accept_cta" | "correct" | "drop_off",
  detail?: string
): Promise<void> {
  await fetch(`${API_URL}/api/log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, action, detail: detail || "" }),
  }).catch(() => {}); // log lỗi không cần xử lý
}
