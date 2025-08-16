import { apiClient, authApi, mathApi, contentApi } from '@/src/utils/api'

// Mock fetch
global.fetch = jest.fn()

describe('API Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(fetch as jest.Mock).mockClear()
  })

  describe('apiClient', () => {
    it('makes GET requests correctly', async () => {
      const mockResponse = { data: 'test' }
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await apiClient.get('/test')

      expect(fetch).toHaveBeenCalledWith('/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      expect(result).toEqual(mockResponse)
    })

    it('makes POST requests correctly', async () => {
      const mockResponse = { success: true }
      const postData = { name: 'test' }

      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await apiClient.post('/test', postData)

      expect(fetch).toHaveBeenCalledWith('/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      })
      expect(result).toEqual(mockResponse)
    })

    it('includes authorization header when token is provided', async () => {
      const mockResponse = { data: 'test' }
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      await apiClient.get('/test', { token: 'test-token' })

      expect(fetch).toHaveBeenCalledWith('/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token',
        },
      })
    })

    it('handles HTTP errors correctly', async () => {
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      })

      await expect(apiClient.get('/test')).rejects.toThrow('HTTP error! status: 404')
    })

    it('handles network errors correctly', async () => {
      ;(fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

      await expect(apiClient.get('/test')).rejects.toThrow('Network error')
    })

    it('handles JSON parsing errors', async () => {
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON')
        },
      })

      await expect(apiClient.get('/test')).rejects.toThrow('Invalid JSON')
    })
  })

  describe('authApi', () => {
    describe('login', () => {
      it('sends login request correctly', async () => {
        const mockResponse = { token: 'test-token', user: { id: 1, email: 'test@example.com' } }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const credentials = { email: 'test@example.com', password: 'password123' }
        const result = await authApi.login(credentials)

        expect(fetch).toHaveBeenCalledWith('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(credentials),
        })
        expect(result).toEqual(mockResponse)
      })

      it('handles login errors', async () => {
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 401,
          statusText: 'Unauthorized',
        })

        const credentials = { email: 'test@example.com', password: 'wrong-password' }

        await expect(authApi.login(credentials)).rejects.toThrow('HTTP error! status: 401')
      })
    })

    describe('register', () => {
      it('sends register request correctly', async () => {
        const mockResponse = { message: 'User created successfully' }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const userData = {
          email: 'test@example.com',
          password: 'password123',
          full_name: 'Test User'
        }
        const result = await authApi.register(userData)

        expect(fetch).toHaveBeenCalledWith('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData),
        })
        expect(result).toEqual(mockResponse)
      })
    })

    describe('logout', () => {
      it('sends logout request correctly', async () => {
        const mockResponse = { message: 'Logged out successfully' }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const result = await authApi.logout('test-token')

        expect(fetch).toHaveBeenCalledWith('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
        })
        expect(result).toEqual(mockResponse)
      })
    })

    describe('getProfile', () => {
      it('fetches user profile correctly', async () => {
        const mockResponse = { id: 1, email: 'test@example.com', full_name: 'Test User' }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const result = await authApi.getProfile('test-token')

        expect(fetch).toHaveBeenCalledWith('/api/auth/profile', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
        })
        expect(result).toEqual(mockResponse)
      })
    })
  })

  describe('mathApi', () => {
    describe('solveEquation', () => {
      it('solves equation correctly', async () => {
        const mockResponse = {
          solution: 'x = 3',
          steps: ['2x + 5 = 11', '2x = 6', 'x = 3']
        }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const equation = '2x + 5 = 11'
        const result = await mathApi.solveEquation(equation)

        expect(fetch).toHaveBeenCalledWith('/api/math/solve/equation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ expression: equation }),
        })
        expect(result).toEqual(mockResponse)
      })

      it('handles invalid equations', async () => {
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 400,
          statusText: 'Bad Request',
        })

        await expect(mathApi.solveEquation('invalid')).rejects.toThrow('HTTP error! status: 400')
      })
    })

    describe('calculateDerivative', () => {
      it('calculates derivative correctly', async () => {
        const mockResponse = {
          derivative: '2x',
          steps: ['f(x) = x²', "f'(x) = 2x"]
        }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const expression = 'x^2'
        const result = await mathApi.calculateDerivative(expression)

        expect(fetch).toHaveBeenCalledWith('/api/math/solve/derivative', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ expression, variable: 'x' }),
        })
        expect(result).toEqual(mockResponse)
      })
    })

    describe('calculateIntegral', () => {
      it('calculates integral correctly', async () => {
        const mockResponse = {
          integral: 'x³/3 + C',
          steps: ['∫x² dx', 'x³/3 + C']
        }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const expression = 'x^2'
        const result = await mathApi.calculateIntegral(expression)

        expect(fetch).toHaveBeenCalledWith('/api/math/solve/integral', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ expression, variable: 'x' }),
        })
        expect(result).toEqual(mockResponse)
      })
    })

    describe('getHistory', () => {
      it('fetches solving history correctly', async () => {
        const mockResponse = {
          problems: [
            { id: 1, expression: '2x + 5 = 11', solution: 'x = 3', created_at: '2024-01-01' }
          ],
          total: 1
        }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const result = await mathApi.getHistory('test-token')

        expect(fetch).toHaveBeenCalledWith('/api/math/history?page=1&limit=20', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
        })
        expect(result).toEqual(mockResponse)
      })
    })
  })

  describe('contentApi', () => {
    describe('getArticles', () => {
      it('fetches articles correctly', async () => {
        const mockResponse = {
          articles: [
            { id: 1, title: 'Test Article', content: 'Test content' }
          ],
          total: 1
        }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const result = await contentApi.getArticles()

        expect(fetch).toHaveBeenCalledWith('/api/content/articles?page=1&limit=10', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        expect(result).toEqual(mockResponse)
      })

      it('handles pagination parameters', async () => {
        const mockResponse = { articles: [], total: 0 }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        await contentApi.getArticles({ page: 2, limit: 5 })

        expect(fetch).toHaveBeenCalledWith('/api/content/articles?page=2&limit=5', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
      })
    })

    describe('getArticle', () => {
      it('fetches single article correctly', async () => {
        const mockResponse = { id: 1, title: 'Test Article', content: 'Test content' }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const result = await contentApi.getArticle(1)

        expect(fetch).toHaveBeenCalledWith('/api/content/articles/1', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        expect(result).toEqual(mockResponse)
      })
    })

    describe('searchArticles', () => {
      it('searches articles correctly', async () => {
        const mockResponse = {
          articles: [
            { id: 1, title: 'Math Article', content: 'Math content' }
          ],
          total: 1
        }
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        })

        const result = await contentApi.searchArticles('math')

        expect(fetch).toHaveBeenCalledWith('/api/content/articles/search?q=math&page=1&limit=10', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        expect(result).toEqual(mockResponse)
      })
    })
  })

  describe('Error Handling', () => {
    it('handles timeout errors', async () => {
      jest.useFakeTimers()

      ;(fetch as jest.Mock).mockImplementationOnce(() =>
        new Promise(resolve => setTimeout(resolve, 10000))
      )

      const promise = apiClient.get('/test')

      jest.advanceTimersByTime(5000)

      await expect(promise).rejects.toThrow('Request timeout')

      jest.useRealTimers()
    })

    it('retries failed requests', async () => {
      ;(fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: 'success' }),
        })

      const result = await apiClient.get('/test', { retry: 3 })

      expect(fetch).toHaveBeenCalledTimes(3)
      expect(result).toEqual({ data: 'success' })
    })
  })

  describe('Request Interceptors', () => {
    it('adds request timestamp', async () => {
      const mockResponse = { data: 'test' }
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      await apiClient.get('/test')

      const callArgs = (fetch as jest.Mock).mock.calls[0]
      expect(callArgs[1].headers['X-Request-Time']).toBeDefined()
    })

    it('adds request ID', async () => {
      const mockResponse = { data: 'test' }
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      await apiClient.get('/test')

      const callArgs = (fetch as jest.Mock).mock.calls[0]
      expect(callArgs[1].headers['X-Request-ID']).toBeDefined()
    })
  })
})
