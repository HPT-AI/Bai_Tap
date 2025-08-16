import { render, screen } from '@testing-library/react'
import { Layout } from '@/components/Layout'

// Mock child components
jest.mock('@/components/Header', () => ({
  Header: () => <header data-testid="header">Header</header>
}))

jest.mock('@/components/Footer', () => ({
  Footer: () => <footer data-testid="footer">Footer</footer>
}))

describe('Layout Component', () => {
  const mockChildren = <div data-testid="children">Test Content</div>

  describe('Rendering', () => {
    it('renders header, children, and footer', () => {
      render(<Layout>{mockChildren}</Layout>)

      expect(screen.getByTestId('header')).toBeInTheDocument()
      expect(screen.getByTestId('children')).toBeInTheDocument()
      expect(screen.getByTestId('footer')).toBeInTheDocument()
    })

    it('renders children content correctly', () => {
      const customContent = <div data-testid="custom">Custom Content</div>
      render(<Layout>{customContent}</Layout>)

      expect(screen.getByTestId('custom')).toBeInTheDocument()
      expect(screen.getByText('Custom Content')).toBeInTheDocument()
    })

    it('renders multiple children correctly', () => {
      render(
        <Layout>
          <div data-testid="child1">Child 1</div>
          <div data-testid="child2">Child 2</div>
        </Layout>
      )

      expect(screen.getByTestId('child1')).toBeInTheDocument()
      expect(screen.getByTestId('child2')).toBeInTheDocument()
    })
  })

  describe('Structure', () => {
    it('has proper semantic structure', () => {
      render(<Layout>{mockChildren}</Layout>)

      const main = screen.getByRole('main')
      expect(main).toBeInTheDocument()
      expect(main).toContainElement(screen.getByTestId('children'))
    })

    it('has correct layout structure', () => {
      render(<Layout>{mockChildren}</Layout>)

      const layoutContainer = screen.getByTestId('layout-container')
      expect(layoutContainer).toHaveClass('min-h-screen', 'flex', 'flex-col')
    })

    it('has proper main content area', () => {
      render(<Layout>{mockChildren}</Layout>)

      const main = screen.getByRole('main')
      expect(main).toHaveClass('flex-1')
    })
  })

  describe('Props Handling', () => {
    it('accepts and renders className prop', () => {
      render(<Layout className="custom-class">{mockChildren}</Layout>)

      const layoutContainer = screen.getByTestId('layout-container')
      expect(layoutContainer).toHaveClass('custom-class')
    })

    it('merges custom className with default classes', () => {
      render(<Layout className="custom-class">{mockChildren}</Layout>)

      const layoutContainer = screen.getByTestId('layout-container')
      expect(layoutContainer).toHaveClass('min-h-screen', 'flex', 'flex-col', 'custom-class')
    })

    it('handles no className prop gracefully', () => {
      render(<Layout>{mockChildren}</Layout>)

      const layoutContainer = screen.getByTestId('layout-container')
      expect(layoutContainer).toHaveClass('min-h-screen', 'flex', 'flex-col')
    })
  })

  describe('Responsive Design', () => {
    it('has responsive container classes', () => {
      render(<Layout>{mockChildren}</Layout>)

      const main = screen.getByRole('main')
      expect(main).toHaveClass('container', 'mx-auto', 'px-4', 'sm:px-6', 'lg:px-8')
    })

    it('handles mobile layout correctly', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })

      render(<Layout>{mockChildren}</Layout>)

      const main = screen.getByRole('main')
      expect(main).toHaveClass('px-4')
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA landmarks', () => {
      render(<Layout>{mockChildren}</Layout>)

      expect(screen.getByRole('main')).toBeInTheDocument()
      expect(screen.getByTestId('header')).toBeInTheDocument()
      expect(screen.getByTestId('footer')).toBeInTheDocument()
    })

    it('maintains focus management', () => {
      render(<Layout>{mockChildren}</Layout>)

      const main = screen.getByRole('main')
      expect(main).toHaveAttribute('tabIndex', '-1')
    })

    it('supports skip to content functionality', () => {
      render(<Layout>{mockChildren}</Layout>)

      const main = screen.getByRole('main')
      expect(main).toHaveAttribute('id', 'main-content')
    })
  })

  describe('Loading States', () => {
    it('renders loading state when specified', () => {
      render(<Layout loading>{mockChildren}</Layout>)

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
      expect(screen.queryByTestId('children')).not.toBeInTheDocument()
    })

    it('renders children when not loading', () => {
      render(<Layout loading={false}>{mockChildren}</Layout>)

      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
      expect(screen.getByTestId('children')).toBeInTheDocument()
    })
  })

  describe('Error Boundaries', () => {
    it('handles component errors gracefully', () => {
      const ThrowError = () => {
        throw new Error('Test error')
      }

      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

      render(
        <Layout>
          <ThrowError />
        </Layout>
      )

      // Should render error boundary
      expect(screen.getByTestId('error-boundary')).toBeInTheDocument()

      consoleSpy.mockRestore()
    })
  })

  describe('Meta Tags', () => {
    it('sets proper meta tags when title is provided', () => {
      render(<Layout title="Test Page">{mockChildren}</Layout>)

      expect(document.title).toBe('Test Page | Math Service')
    })

    it('sets default title when no title provided', () => {
      render(<Layout>{mockChildren}</Layout>)

      expect(document.title).toBe('Math Service')
    })

    it('sets meta description when provided', () => {
      render(<Layout description="Test description">{mockChildren}</Layout>)

      const metaDescription = document.querySelector('meta[name="description"]')
      expect(metaDescription).toHaveAttribute('content', 'Test description')
    })
  })

  describe('Theme Support', () => {
    it('applies theme classes correctly', () => {
      render(<Layout theme="dark">{mockChildren}</Layout>)

      const layoutContainer = screen.getByTestId('layout-container')
      expect(layoutContainer).toHaveClass('dark')
    })

    it('defaults to light theme', () => {
      render(<Layout>{mockChildren}</Layout>)

      const layoutContainer = screen.getByTestId('layout-container')
      expect(layoutContainer).not.toHaveClass('dark')
    })
  })

  describe('Performance', () => {
    it('renders efficiently', () => {
      const startTime = performance.now()
      render(<Layout>{mockChildren}</Layout>)
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(50)
    })

    it('handles re-renders efficiently', () => {
      const { rerender } = render(<Layout>{mockChildren}</Layout>)

      const startTime = performance.now()
      rerender(<Layout className="updated">{mockChildren}</Layout>)
      const endTime = performance.now()

      expect(endTime - startTime).toBeLessThan(20)
    })
  })

  describe('Integration', () => {
    it('integrates properly with Header component', () => {
      render(<Layout>{mockChildren}</Layout>)

      const header = screen.getByTestId('header')
      const main = screen.getByRole('main')

      expect(header.nextElementSibling).toBe(main)
    })

    it('integrates properly with Footer component', () => {
      render(<Layout>{mockChildren}</Layout>)

      const main = screen.getByRole('main')
      const footer = screen.getByTestId('footer')

      expect(main.nextElementSibling).toBe(footer)
    })
  })
})
