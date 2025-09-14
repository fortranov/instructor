import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Настройка проксирования
  async rewrites() {
    // В продакшене используем переменную окружения для backend URL
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
