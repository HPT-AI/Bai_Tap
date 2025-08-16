import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Header } from '@/components/Header'

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

// Mock authentication context
const mockAuthContext = {
  user: null,
  login: jest.fn(),
  logout: jest.fn(),
  loading: false,
}

jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext,
}))

describe('Header Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders header with logo and navigation', () => {
      render(<Header />)

      // Check logo
      expect(screen.getByText('Math Service')).toBeInTheDocument()

      // Check navigation links
      expect(screen.getByText('Trang chủ')).toBeInTheDocument()
      expect(screen.getByText('Giải toán')).toBeInTheDocument()
      expect(screen.getByText('Bài viết')).toBeInTheDocument()
      expect(screen.getByText('Về chúng tôi')).toBeInTheDocument()
    })

    it('renders login/register buttons when user is not authenticated', () => {
      render(<Header />)

      expect(screen.getByText('Đăng nhập')).toBeInTheDocument()
      expect(screen.getByText('Đăng ký')).toBeInTheDocument()
    })

    it('renders user menu when user is authenticated', () => {
      mockAuthContext.user = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'user',
      }

      render(<Header />)

      expect(screen.getByText('Test User')).toBeInTheDocument()
      expect(screen.queryByText('Đăng nhập')).not.toBeInTheDocument()
    })
  })

  describe('Navigation', () => {
    it('navigates to home page when logo is clicked', () => {
      render(<Header />)

      const logo = screen.getByText('Math Service')
      fireEvent.click(logo)

      expect(mockPush).toHaveBeenCalledWith('/')
    })

    it('navigates to solver page when "Giải toán" is clicked', () => {
      render(<Header />)

      const solverLink = screen.getByText('Giải toán')
      fireEvent.click(solverLink)

      expect(mockPush).toHaveBeenCalledWith('/solver')
    })

    it('navigates to articles page when "Bài viết" is clicked', () => {
      render(<Header />)

      const articlesLink = screen.getByText('Bài viết')
      fireEvent.click(articlesLink)

      expect(mockPush).toHaveBeenCalledWith('/articles')
    })
  })

  describe('Mobile Menu', () => {
    it('toggles mobile menu when hamburger button is clicked', () => {
      render(<Header />)

      // Mobile menu should be hidden initially
      const mobileMenu = screen.getByTestId('mobile-menu')
      expect(mobileMenu).toHaveClass('hidden')

      // Click hamburger button
      const hamburgerButton = screen.getByTestId('mobile-menu-button')
      fireEvent.click(hamburgerButton)

      // Mobile menu should be visible
      expect(mobileMenu).not.toHaveClass('hidden')

      // Click again to hide
      fireEvent.click(hamburgerButton)
      expect(mobileMenu).toHaveClass('hidden')
    })

    it('closes mobile menu when navigation link is clicked', () => {
      render(<Header />)

      // Open mobile menu
      const hamburgerButton = screen.getByTestId('mobile-menu-button')
      fireEvent.click(hamburgerButton)

      const mobileMenu = screen.getByTestId('mobile-menu')
      expect(mobileMenu).not.toHaveClass('hidden')

      // Click navigation link in mobile menu
      const mobileHomeLink = screen.getByTestId('mobile-home-link')
      fireEvent.click(mobileHomeLink)

      // Menu should close
      expect(mobileMenu).toHaveClass('hidden')
    })
  })

  describe('User Authentication', () => {
    it('shows login modal when login button is clicked', async () => {
      render(<Header />)

      const loginButton = screen.getByText('Đăng nhập')
      fireEvent.click(loginButton)

      await waitFor(() => {
        expect(screen.getByTestId('login-modal')).toBeInTheDocument()
      })
    })

    it('shows user dropdown when user avatar is clicked', async () => {
      mockAuthContext.user = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'user',
      }

      render(<Header />)

      const userAvatar = screen.getByTestId('user-avatar')
      fireEvent.click(userAvatar)

      await waitFor(() => {
        expect(screen.getByText('Hồ sơ')).toBeInTheDocument()
        expect(screen.getByText('Lịch sử')).toBeInTheDocument()
        expect(screen.getByText('Đăng xuất')).toBeInTheDocument()
      })
    })

    it('calls logout function when logout is clicked', async () => {
      mockAuthContext.user = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'user',
      }

      render(<Header />)

      // Open user dropdown
      const userAvatar = screen.getByTestId('user-avatar')
      fireEvent.click(userAvatar)

      // Click logout
      await waitFor(() => {
        const logoutButton = screen.getByText('Đăng xuất')
        fireEvent.click(logoutButton)
      })

      expect(mockAuthContext.logout).toHaveBeenCalled()
    })
  })

  describe('Premium Features', () => {
    it('shows premium badge for premium users', () => {
      mockAuthContext.user = {
        id: 1,
        email: 'premium@example.com',
        full_name: 'Premium User',
        role: 'user',
        is_premium: true,
      }

      render(<Header />)

      expect(screen.getByText('Premium')).toBeInTheDocument()
    })

    it('shows upgrade button for non-premium users', () => {
      mockAuthContext.user = {
        id: 1,
        email: 'user@example.com',
        full_name: 'Regular User',
        role: 'user',
        is_premium: false,
      }

      render(<Header />)

      expect(screen.getByText('Nâng cấp')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels for navigation', () => {
      render(<Header />)

      const nav = screen.getByRole('navigation')
      expect(nav).toHaveAttribute('aria-label', 'Main navigation')

      const hamburgerButton = screen.getByTestId('mobile-menu-button')
      expect(hamburgerButton).toHaveAttribute('aria-label', 'Toggle mobile menu')
    })

    it('supports keyboard navigation', () => {
      render(<Header />)

      const homeLink = screen.getByText('Trang chủ')
      homeLink.focus()
      expect(homeLink).toHaveFocus()

      // Tab to next link
      fireEvent.keyDown(homeLink, { key: 'Tab' })
      const solverLink = screen.getByText('Giải toán')
      expect(solverLink).toHaveFocus()
    })
  })

  describe('Responsive Design', () => {
    it('hides desktop menu on mobile screens', () => {
      // Mock window.innerWidth
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 640, // Mobile width
      })

      render(<Header />)

      const desktopMenu = screen.getByTestId('desktop-menu')
      expect(desktopMenu).toHaveClass('hidden', 'md:flex')
    })

    it('shows mobile menu button on mobile screens', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 640, // Mobile width
      })

      render(<Header />)

      const mobileMenuButton = screen.getByTestId('mobile-menu-button')
      expect(mobileMenuButton).toHaveClass('md:hidden')
    })
  })

  describe('Loading States', () => {
    it('shows loading spinner when auth is loading', () => {
      mockAuthContext.loading = true

      render(<Header />)

      expect(screen.getByTestId('auth-loading')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('handles navigation errors gracefully', () => {
      mockPush.mockRejectedValueOnce(new Error('Navigation failed'))

      render(<Header />)

      const homeLink = screen.getByText('Trang chủ')
      fireEvent.click(homeLink)

      // Should not throw error
      expect(mockPush).toHaveBeenCalledWith('/')
    })
  })
})
