// vue.config.js
const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        ws: true,
        changeOrigin: true,
        target: 'http://127.0.0.1:8000'
      },
      '/uploads': {
        changeOrigin: true,
        target: 'http://127.0.0.1:8000'
      }
      // раздел /sse теперь не нужен, т.к. вы обращаетесь к нему напрямую
    }
  }
});
