/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'PingFang SC', 'Microsoft YaHei', 'system-ui', 'sans-serif'],
        serif: ['Noto Serif SC', 'Source Han Serif SC', 'Songti SC', 'Georgia', 'serif'],
      },
      colors: {
        warm: {
          50: '#faf8f5',
          100: '#f5f0e8',
          200: '#ebe0cc',
          800: '#3d3226',
          900: '#2c241a',
        },
        accent: '#c75b39',
      },
    },
  },
  plugins: [],
};
