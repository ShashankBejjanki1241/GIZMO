/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8002/api/:path*',
      },
      {
        source: '/orchestrator/:path*',
        destination: 'http://localhost:8003/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
