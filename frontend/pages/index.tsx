import React from 'react';
import Head from 'next/head';

const HomePage: React.FC = () => {
  return (
    <>
      <Head>
        <title>Math Service - Website Dịch vụ Toán học</title>
        <meta name="description" content="Website dịch vụ toán học trực tuyến với AI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-16">
          {/* Header */}
          <header className="text-center mb-16">
            <h1 className="text-5xl font-bold text-gray-800 mb-4">
              Math Service
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Website dịch vụ toán học trực tuyến với AI - Giải toán nhanh chóng, chính xác
            </p>
          </header>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <div className="text-4xl mb-4">🧮</div>
              <h3 className="text-xl font-semibold mb-2">Giải Phương Trình</h3>
              <p className="text-gray-600">
                Giải phương trình bậc 2, hệ phương trình, tích phân với các bước chi tiết
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <div className="text-4xl mb-4">💳</div>
              <h3 className="text-xl font-semibold mb-2">Thanh Toán Linh Hoạt</h3>
              <p className="text-gray-600">
                Hỗ trợ VNPay, MoMo, ZaloPay với bảo mật cao và xử lý nhanh chóng
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-2">Quản Lý Thông Minh</h3>
              <p className="text-gray-600">
                Dashboard admin với analytics, monitoring và quản lý người dùng
              </p>
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-md mx-auto">
              <h2 className="text-2xl font-bold mb-4">Bắt đầu ngay</h2>
              <p className="text-gray-600 mb-6">
                Đăng ký tài khoản để trải nghiệm dịch vụ giải toán AI
              </p>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors">
                  Đăng ký miễn phí
                </button>
                <button className="w-full border border-gray-300 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-50 transition-colors">
                  Đăng nhập
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 Math Service. All rights reserved.</p>
          <p className="text-gray-400 mt-2">
            Powered by Next.js, FastAPI & AI Technology
          </p>
        </div>
      </footer>
    </>
  );
};

export default HomePage;

