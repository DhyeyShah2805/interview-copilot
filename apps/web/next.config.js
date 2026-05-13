/** @type {import('next').NextConfig} */
const path = require('path');
 
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
 
  // Tell Turbopack this directory is the project root.
  // Required because apps/web sits inside a monorepo alongside apps/api,
  // which confuses Turbopack's automatic root detection.
  turbopack: {
    root: __dirname,
  },
 
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