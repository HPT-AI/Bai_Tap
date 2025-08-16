import React, { useState } from 'react';
import Link from 'next/link';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="text-2xl">🧮</div>
            <span className="text-xl font-bold text-gray-800">Math Service</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            <Link href="/" className="text-gray-600 hover:text-blue-600 transition-colors">
              Trang chủ
            </Link>
            <Link href="/solve" className="text-gray-600 hover:text-blue-600 transition-colors">
              Giải toán
            </Link>
            <Link href="/pricing" className="text-gray-600 hover:text-blue-600 transition-colors">
              Bảng giá
            </Link>
            <Link href="/help" className="text-gray-600 hover:text-blue-600 transition-colors">
              Trợ giúp
            </Link>
          </nav>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex space-x-4">
            <Link href="/login" className="btn-secondary">
              Đăng nhập
            </Link>
            <Link href="/register" className="btn-primary">
              Đăng ký
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            <div className="w-6 h-6 flex flex-col justify-center space-y-1">
              <div className={`h-0.5 bg-gray-600 transition-all ${isMenuOpen ? 'rotate-45 translate-y-1' : ''}`}></div>
              <div className={`h-0.5 bg-gray-600 transition-all ${isMenuOpen ? 'opacity-0' : ''}`}></div>
              <div className={`h-0.5 bg-gray-600 transition-all ${isMenuOpen ? '-rotate-45 -translate-y-1' : ''}`}></div>
            </div>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            <nav className="flex flex-col space-y-4">
              <Link href="/" className="text-gray-600 hover:text-blue-600 transition-colors">
                Trang chủ
              </Link>
              <Link href="/solve" className="text-gray-600 hover:text-blue-600 transition-colors">
                Giải toán
              </Link>
              <Link href="/pricing" className="text-gray-600 hover:text-blue-600 transition-colors">
                Bảng giá
              </Link>
              <Link href="/help" className="text-gray-600 hover:text-blue-600 transition-colors">
                Trợ giúp
              </Link>
              <div className="flex flex-col space-y-2 pt-4 border-t border-gray-200">
                <Link href="/login" className="btn-secondary text-center">
                  Đăng nhập
                </Link>
                <Link href="/register" className="btn-primary text-center">
                  Đăng ký
                </Link>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
