import { render, screen } from '@testing-library/react'
import { Footer } from '@/components/Footer'

describe('Footer Component', () => {
  describe('Rendering', () => {
    it('renders footer with company information', () => {
      render(<Footer />)

      // Check company name
      expect(screen.getByText('Math Service')).toBeInTheDocument()

      // Check description
      expect(screen.getByText(/Giải pháp toán học trực tuyến/i)).toBeInTheDocument()
    })

    it('renders navigation links', () => {
      render(<Footer />)

      // Quick Links section
      expect(screen.getByText('Liên kết nhanh')).toBeInTheDocument()
      expect(screen.getByText('Trang chủ')).toBeInTheDocument()
      expect(screen.getByText('Giải toán')).toBeInTheDocument()
      expect(screen.getByText('Bài viết')).toBeInTheDocument()
      expect(screen.getByText('Về chúng tôi')).toBeInTheDocument()
    })

    it('renders services section', () => {
      render(<Footer />)

      expect(screen.getByText('Dịch vụ')).toBeInTheDocument()
      expect(screen.getByText('Giải phương trình')).toBeInTheDocument()
      expect(screen.getByText('Tính đạo hàm')).toBeInTheDocument()
      expect(screen.getByText('Tính tích phân')).toBeInTheDocument()
      expect(screen.getByText('Thống kê')).toBeInTheDocument()
    })

    it('renders contact information', () => {
      render(<Footer />)

      expect(screen.getByText('Liên hệ')).toBeInTheDocument()
      expect(screen.getByText('support@mathservice.com')).toBeInTheDocument()
      expect(screen.getByText('+84 123 456 789')).toBeInTheDocument()
      expect(screen.getByText(/Hà Nội, Việt Nam/i)).toBeInTheDocument()
    })

    it('renders social media links', () => {
      render(<Footer />)

      expect(screen.getByText('Theo dõi chúng tôi')).toBeInTheDocument()
      expect(screen.getByLabelText('Facebook')).toBeInTheDocument()
      expect(screen.getByLabelText('Twitter')).toBeInTheDocument()
      expect(screen.getByLabelText('LinkedIn')).toBeInTheDocument()
      expect(screen.getByLabelText('YouTube')).toBeInTheDocument()
    })

    it('renders copyright information', () => {
      render(<Footer />)

      const currentYear = new Date().getFullYear()
      expect(screen.getByText(`© ${currentYear} Math Service. Tất cả quyền được bảo lưu.`)).toBeInTheDocument()
    })
  })

  describe('Links and Navigation', () => {
    it('has correct href attributes for navigation links', () => {
      render(<Footer />)

      expect(screen.getByRole('link', { name: 'Trang chủ' })).toHaveAttribute('href', '/')
      expect(screen.getByRole('link', { name: 'Giải toán' })).toHaveAttribute('href', '/solver')
      expect(screen.getByRole('link', { name: 'Bài viết' })).toHaveAttribute('href', '/articles')
      expect(screen.getByRole('link', { name: 'Về chúng tôi' })).toHaveAttribute('href', '/about')
    })

    it('has correct href attributes for service links', () => {
      render(<Footer />)

      expect(screen.getByRole('link', { name: 'Giải phương trình' })).toHaveAttribute('href', '/solver/equation')
      expect(screen.getByRole('link', { name: 'Tính đạo hàm' })).toHaveAttribute('href', '/solver/derivative')
      expect(screen.getByRole('link', { name: 'Tính tích phân' })).toHaveAttribute('href', '/solver/integral')
      expect(screen.getByRole('link', { name: 'Thống kê' })).toHaveAttribute('href', '/solver/statistics')
    })

    it('has correct href attributes for social media links', () => {
      render(<Footer />)

      expect(screen.getByLabelText('Facebook')).toHaveAttribute('href', 'https://facebook.com/mathservice')
      expect(screen.getByLabelText('Twitter')).toHaveAttribute('href', 'https://twitter.com/mathservice')
      expect(screen.getByLabelText('LinkedIn')).toHaveAttribute('href', 'https://linkedin.com/company/mathservice')
      expect(screen.getByLabelText('YouTube')).toHaveAttribute('href', 'https://youtube.com/mathservice')
    })

    it('opens social media links in new tab', () => {
      render(<Footer />)

      expect(screen.getByLabelText('Facebook')).toHaveAttribute('target', '_blank')
      expect(screen.getByLabelText('Twitter')).toHaveAttribute('target', '_blank')
      expect(screen.getByLabelText('LinkedIn')).toHaveAttribute('target', '_blank')
      expect(screen.getByLabelText('YouTube')).toHaveAttribute('target', '_blank')
    })
  })

  describe('Accessibility', () => {
    it('has proper semantic structure', () => {
      render(<Footer />)

      const footer = screen.getByRole('contentinfo')
      expect(footer).toBeInTheDocument()
    })

    it('has proper heading hierarchy', () => {
      render(<Footer />)

      const headings = screen.getAllByRole('heading', { level: 3 })
      expect(headings).toHaveLength(4) // Quick Links, Services, Contact, Follow Us
    })

    it('has proper ARIA labels for social media links', () => {
      render(<Footer />)

      expect(screen.getByLabelText('Facebook')).toBeInTheDocument()
      expect(screen.getByLabelText('Twitter')).toBeInTheDocument()
      expect(screen.getByLabelText('LinkedIn')).toBeInTheDocument()
      expect(screen.getByLabelText('YouTube')).toBeInTheDocument()
    })
  })

  describe('Responsive Design', () => {
    it('has responsive grid classes', () => {
      render(<Footer />)

      const footerContent = screen.getByTestId('footer-content')
      expect(footerContent).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4')
    })

    it('has responsive spacing classes', () => {
      render(<Footer />)

      const footer = screen.getByRole('contentinfo')
      expect(footer).toHaveClass('py-8', 'md:py-12')
    })
  })

  describe('Newsletter Subscription', () => {
    it('renders newsletter subscription form', () => {
      render(<Footer />)

      expect(screen.getByText('Đăng ký nhận tin')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Nhập email của bạn')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Đăng ký' })).toBeInTheDocument()
    })

    it('has proper form validation', () => {
      render(<Footer />)

      const emailInput = screen.getByPlaceholderText('Nhập email của bạn')
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(emailInput).toHaveAttribute('required')
    })
  })

  describe('Legal Links', () => {
    it('renders legal links', () => {
      render(<Footer />)

      expect(screen.getByText('Chính sách bảo mật')).toBeInTheDocument()
      expect(screen.getByText('Điều khoản sử dụng')).toBeInTheDocument()
      expect(screen.getByText('Cookie Policy')).toBeInTheDocument()
    })

    it('has correct href attributes for legal links', () => {
      render(<Footer />)

      expect(screen.getByRole('link', { name: 'Chính sách bảo mật' })).toHaveAttribute('href', '/privacy')
      expect(screen.getByRole('link', { name: 'Điều khoản sử dụng' })).toHaveAttribute('href', '/terms')
      expect(screen.getByRole('link', { name: 'Cookie Policy' })).toHaveAttribute('href', '/cookies')
    })
  })

  describe('Theme Support', () => {
    it('supports dark mode classes', () => {
      render(<Footer />)

      const footer = screen.getByRole('contentinfo')
      expect(footer).toHaveClass('bg-gray-900', 'text-white')
    })
  })

  describe('Performance', () => {
    it('renders without performance issues', () => {
      const startTime = performance.now()
      render(<Footer />)
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100) // Should render in less than 100ms
    })
  })
})
