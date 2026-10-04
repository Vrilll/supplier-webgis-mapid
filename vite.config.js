import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  // Relative base: the build works at a subdomain root or inside a subfolder.
  base: './',
  plugins: [svelte()]
});
