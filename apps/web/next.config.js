/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Proxy /api/* to the FastAPI backend during local dev so we can call
  // fetch('/api/...') without worrying about CORS in the browser.
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
