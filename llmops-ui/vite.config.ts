import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import viteCompression from 'vite-plugin-compression'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig({
  build: {
    target: 'esnext', // 减少转换耗时
    minify: 'esbuild', // 确保使用 esbuild 进行混淆压缩（它是最快的）
    chunkSizeWarningLimit: 1500, // 将警告限制提高到 1000kB
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // 1. 将所有高频基础库(Vue系列)打包在一起，避免循环引用
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vue-framework'
            }

            // // 2. 将 dagre 和 lodash 合并，因为它们互相引用
            // if (id.includes('dagre') || id.includes('lodash')) {
            //   return 'graph-vendor'
            // }

            // 3. 将 Markdown 相关的生态合并（包括 highlight.js 和 katex）
            if (
              id.includes('markdown-it') ||
              id.includes('highlight.js') ||
              id.includes('katex') ||
              id.includes('github-markdown-css')
            ) {
              return 'markdown-vendor'
            }

            // 4. 超大型独立库继续保留独立
            if (id.includes('echarts')) {
              return 'echarts-vendor'
            }

            // 5. 其余不常用的第三方库统一放 vendor
            return 'vendor'
          }
        },
      },
    },
  },
  optimizeDeps: {
    include: ['vue-virtual-scroller'],
  },
  plugins: [
    vue(),
    vueDevTools(),
    viteCompression(),
    visualizer({
      open: false, // 注意：在服务器上构建要设为 false，否则会尝试打开浏览器导致报错
      filename: 'stats.html', // 生成的分析文件名
      gzipSize: true, // 显示 gzip 压缩后的大小
      brotliSize: true, // 显示 brotli 压缩后的大小
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => {
          return path.replace(/^\/api/, '')
        },
      },
    },
  },
})
