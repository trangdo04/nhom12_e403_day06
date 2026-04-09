import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vinschool – Tư vấn tuyển sinh",
  description: "AI Admissions Copilot – Tìm chương trình và cơ sở Vinschool phù hợp với con bạn.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
