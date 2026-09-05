import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
export default defineConfig({
  base: '/key3in/', plugins: [react(), VitePWA({
    registerType: 'autoUpdate', includeAssets: ['icons/icon.svg'],
    manifest: { name:'Key3in', short_name:'Key3in', description:'Календарь и ежедневные заметки', start_url:'/key3in/', scope:'/key3in/', display:'standalone', theme_color:'#425f91', background_color:'#f9f9ff', lang:'ru', icons:[{src:'/key3in/icons/icon.svg',sizes:'any',type:'image/svg+xml',purpose:'any maskable'}]},
    workbox:{importScripts:['notification-handler.js'],navigateFallback:'/key3in/index.html', navigateFallbackDenylist:[/^\/key3in\/api\//], runtimeCaching:[{urlPattern:/\/key3in\/api\//,handler:'NetworkOnly'}]}
  })], test:{environment:'jsdom',setupFiles:'./src/test/setup.ts'}
})
