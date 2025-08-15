/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output để tối ưu cho Docker
  output: 'standalone',

  // Disable telemetry
  telemetry: false,

  // Environment variables
  env: {
    CUSTOM_KEY: 'math-service-website',
  },

  // API routes configuration
  async rewrites() {
    return [
      {
        source: '/api/users/:path*',
        destination: `${process.env.NEXT_PUBLIC_USER_SERVICE_URL}/api/v1/:path*`,
      },
      {
        source: '/api/payments/:path*',
        destination: `${process.env.NEXT_PUBLIC_PAYMENT_SERVICE_URL}/api/v1/:path*`,
      },
      {
        source: '/api/math/:path*',
        destination: `${process.env.NEXT_PUBLIC_MATH_SOLVER_SERVICE_URL}/api/v1/:path*`,
      },
      {
        source: '/api/content/:path*',
        destination: `${process.env.NEXT_PUBLIC_CONTENT_SERVICE_URL}/api/v1/:path*`,
      },
      {
        source: '/api/admin/:path*',
        destination: `${process.env.NEXT_PUBLIC_ADMIN_SERVICE_URL}/api/v1/:path*`,
      },
    ];
  },

  // Headers configuration cho CORS
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization' },
        ],
      },
    ];
  },

  // Experimental features
  experimental: {
    serverComponentsExternalPackages: [],
  },

  // Images configuration
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
};

module.exports = nextConfig;
