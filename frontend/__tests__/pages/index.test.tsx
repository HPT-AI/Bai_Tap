import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Home from '@/pages/index'

// Mock next/router
const mockPush = jest.fn()
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: mockPush,
    pathname: '/',
    query: {},
    asPath: '/',
  }),
}))

// Mock components
jest.mock('@/components/Layout', () => ({
  Layout: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>
}))

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders hero section', () => {
      render(<Home />)

      expect(screen.getByText('Giải Toán Trực Tuyến')).toBeInTheDocument()
      expect(screen.getByText(/Giải pháp toán học thông minh/i)).toBeInTheDocument()
    })

    it('renders main CTA buttons', () => {
      render(<Home />)

      expect(screen.getByText('Bắt đầu giải toán')).toBeInTheDocument()
      expect(screen.getByText('Xem demo')).toBeInTheDocument()
    })

    it('renders features section', () => {
      render(<Home />)

      expect(screen.getByText('Tính năng nổi bật')).toBeInTheDocument()
      expect(screen.getByText('Giải phương trình')).toBeInTheDocument()
      expect(screen.getByText('Tính đạo hàm')).toBeInTheDocument()
      expect(screen.getByText('Tính tích phân')).toBeInTheDocument()
      expect(screen.getByText('Thống kê')).toBeInTheDocument()
    })

    it('renders statistics section', () => {
      render(<Home />)

      expect(screen.getByText('Thống kê sử dụng')).toBeInTheDocument()
      expect(screen.getByText('10,000+')).toBeInTheDocument()
      expect(screen.getByText('Bài toán đã giải')).toBeInTheDocument()
      expect(screen.getByText('5,000+')).toBeInTheDocument()
      expect(screen.getByText('Người dùng')).toBeInTheDocument()
    })

    it('renders testimonials section', () => {
      render(<Home />)

      expect(screen.getByText('Người dùng nói gì')).toBeInTheDocument()
      expect(screen.getByText(/Rất hữu ích cho việc học tập/i)).toBeInTheDocument()
    })
  })

  describe('Navigation', () => {
    it('navigates to solver when "Bắt đầu giải toán" is clicked', () => {
      render(<Home />)

      const startButton = screen.getByText('Bắt đầu giải toán')
      fireEvent.click(startButton)

      expect(mockPush).toHaveBeenCalledWith('/solver')
    })

    it('shows demo modal when "Xem demo" is clicked', async () => {
      render(<Home />)

      const demoButton = screen.getByText('Xem demo')
      fireEvent.click(demoButton)

      await waitFor(() => {
        expect(screen.getByTestId('demo-modal')).toBeInTheDocument()
      })
    })

    it('navigates to specific solver when feature card is clicked', () => {
      render(<Home />)

      const equationCard = screen.getByTestId('feature-equation')
      fireEvent.click(equationCard)

      expect(mockPush).toHaveBeenCalledWith('/solver/equation')
    })
  })

  describe('Interactive Elements', () => {
    it('handles math input demo', async () => {
      render(<Home />)

      const mathInput = screen.getByPlaceholderText('Nhập phương trình của bạn...')
      fireEvent.change(mathInput, { target: { value: '2x + 5 = 11' } })

      const solveButton = screen.getByText('Giải ngay')
      fireEvent.click(solveButton)

      await waitFor(() => {
        expect(screen.getByText('x = 3')).toBeInTheDocument()
      })
    })

    it('validates math input', () => {
      render(<Home />)

      const mathInput = screen.getByPlaceholderText('Nhập phương trình của bạn...')
      fireEvent.change(mathInput, { target: { value: 'invalid equation' } })

      const solveButton = screen.getByText('Giải ngay')
      fireEvent.click(solveButton)

      expect(screen.getByText('Phương trình không hợp lệ')).toBeInTheDocument()
    })

    it('shows loading state during solving', async () => {
      render(<Home />)

      const mathInput = screen.getByPlaceholderText('Nhập phương trình của bạn...')
      fireEvent.change(mathInput, { target: { value: '2x + 5 = 11' } })

      const solveButton = screen.getByText('Giải ngay')
      fireEvent.click(solveButton)

      expect(screen.getByTestId('solving-spinner')).toBeInTheDocument()
    })
  })

  describe('Responsive Design', () => {
    it('adapts to mobile viewport', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })

      render(<Home />)

      const heroSection = screen.getByTestId('hero-section')
      expect(heroSection).toHaveClass('px-4', 'sm:px-6')
    })

    it('shows mobile navigation menu', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 640,
      })

      render(<Home />)

      const mobileMenu = screen.getByTestId('mobile-features')
      expect(mobileMenu).toHaveClass('grid-cols-1', 'sm:grid-cols-2')
    })
  })

  describe('Accessibility', () => {
    it('has proper heading hierarchy', () => {
      render(<Home />)

      const h1 = screen.getByRole('heading', { level: 1 })
      expect(h1).toHaveTextContent('Giải Toán Trực Tuyến')

      const h2Elements = screen.getAllByRole('heading', { level: 2 })
      expect(h2Elements.length).toBeGreaterThan(0)
    })

    it('has proper ARIA labels', () => {
      render(<Home />)

      const mainSection = screen.getByRole('main')
      expect(mainSection).toHaveAttribute('aria-label', 'Trang chủ')

      const ctaButton = screen.getByText('Bắt đầu giải toán')
      expect(ctaButton).toHaveAttribute('aria-label', 'Bắt đầu sử dụng công cụ giải toán')
    })

    it('supports keyboard navigation', () => {
      render(<Home />)

      const startButton = screen.getByText('Bắt đầu giải toán')
      startButton.focus()
      expect(startButton).toHaveFocus()

      fireEvent.keyDown(startButton, { key: 'Enter' })
      expect(mockPush).toHaveBeenCalledWith('/solver')
    })

    it('has proper alt text for images', () => {
      render(<Home />)

      const heroImage = screen.getByAltText('Minh họa giải toán trực tuyến')
      expect(heroImage).toBeInTheDocument()

      const featureImages = screen.getAllByRole('img')
      featureImages.forEach(img => {
        expect(img).toHaveAttribute('alt')
        expect(img.getAttribute('alt')).not.toBe('')
      })
    })
  })

  describe('SEO', () => {
    it('sets proper page title', () => {
      render(<Home />)

      expect(document.title).toBe('Trang chủ | Math Service')
    })

    it('sets meta description', () => {
      render(<Home />)

      const metaDescription = document.querySelector('meta[name="description"]')
      expect(metaDescription).toHaveAttribute('content', expect.stringContaining('Giải toán trực tuyến'))
    })

    it('sets Open Graph tags', () => {
      render(<Home />)

      const ogTitle = document.querySelector('meta[property="og:title"]')
      expect(ogTitle).toHaveAttribute('content', 'Math Service - Giải toán trực tuyến')

      const ogDescription = document.querySelector('meta[property="og:description"]')
      expect(ogDescription).toBeInTheDocument()
    })
  })

  describe('Performance', () => {
    it('renders within performance threshold', () => {
      const startTime = performance.now()
      render(<Home />)
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(100)
    })

    it('lazy loads non-critical sections', async () => {
      render(<Home />)

      // Testimonials should be lazy loaded
      const testimonials = screen.queryByTestId('testimonials-section')
      expect(testimonials).not.toBeInTheDocument()

      // Scroll to trigger lazy loading
      fireEvent.scroll(window, { target: { scrollY: 1000 } })

      await waitFor(() => {
        expect(screen.getByTestId('testimonials-section')).toBeInTheDocument()
      })
    })
  })

  describe('Analytics', () => {
    it('tracks CTA button clicks', () => {
      const mockAnalytics = jest.fn()
      window.gtag = mockAnalytics

      render(<Home />)

      const startButton = screen.getByText('Bắt đầu giải toán')
      fireEvent.click(startButton)

      expect(mockAnalytics).toHaveBeenCalledWith('event', 'cta_click', {
        button_text: 'Bắt đầu giải toán',
        page: 'home'
      })
    })

    it('tracks feature card interactions', () => {
      const mockAnalytics = jest.fn()
      window.gtag = mockAnalytics

      render(<Home />)

      const equationCard = screen.getByTestId('feature-equation')
      fireEvent.click(equationCard)

      expect(mockAnalytics).toHaveBeenCalledWith('event', 'feature_click', {
        feature: 'equation',
        page: 'home'
      })
    })
  })

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      // Mock API failure
      global.fetch = jest.fn().mockRejectedValueOnce(new Error('API Error'))

      render(<Home />)

      const mathInput = screen.getByPlaceholderText('Nhập phương trình của bạn...')
      fireEvent.change(mathInput, { target: { value: '2x + 5 = 11' } })

      const solveButton = screen.getByText('Giải ngay')
      fireEvent.click(solveButton)

      await waitFor(() => {
        expect(screen.getByText('Có lỗi xảy ra, vui lòng thử lại')).toBeInTheDocument()
      })
    })
  })
})
