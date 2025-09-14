import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Настройка проксирования для разработки
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:9000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
