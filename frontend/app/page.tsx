import ChatWidget from "@/components/ChatWidget";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Hero */}
      <div className="max-w-4xl mx-auto px-6 py-16 text-center">
        <div className="flex justify-center mb-6">
          <div className="bg-[#003087] text-white px-4 py-2 rounded-lg font-bold text-xl tracking-wide">
            VINSCHOOL
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          Tư vấn tuyển sinh thông minh
        </h1>
        <p className="text-lg text-gray-600 mb-2">
          Tìm chương trình và cơ sở Vinschool phù hợp nhất với con bạn chỉ trong vài giây.
        </p>
        <p className="text-sm text-gray-400">
          Nhấn vào nút chat góc dưới bên phải để bắt đầu
        </p>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          {[
            { icon: "🎓", title: "Gợi ý chương trình", desc: "Dựa trên độ tuổi của học sinh" },
            { icon: "📍", title: "Tìm cơ sở gần", desc: "Theo khu vực bạn quan tâm" },
            { icon: "⚡", title: "Hành động ngay", desc: "Xem học phí hoặc đăng ký tuyển sinh" },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
              <p className="text-sm text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <ChatWidget />
    </main>
  );
}
