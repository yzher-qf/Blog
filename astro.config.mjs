import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [vue(), tailwind()],
  output: 'server',
  server: {
    port: 4321,
    host: true,
  },
  markdown: {
    shikiConfig: {
      theme: 'github-light',
    },
  },
});
