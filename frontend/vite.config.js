import { defineConfig } from 'vite';
import { resolve } from 'path';
import fs from 'fs';

// Helper to get all HTML files in a directory
function getHtmlFiles(dir, files_ = []) {
  const files = fs.readdirSync(dir);
  for (const i in files) {
    const name = dir + '/' + files[i];
    if (fs.statSync(name).isDirectory()) {
      getHtmlFiles(name, files_);
    } else if (name.endsWith('.html')) {
      files_.push(name);
    }
  }
  return files_;
}

// Get all pages from src/components/pages and public/departments
const pagesDir = resolve(__dirname, 'src/components/pages');
const deptsDir = resolve(__dirname, 'public/departments');

const pageFiles = fs.existsSync(pagesDir) ? getHtmlFiles(pagesDir) : [];
const deptFiles = fs.existsSync(deptsDir) ? getHtmlFiles(deptsDir) : [];

const input = {
  main: resolve(__dirname, 'index.html'),
};

pageFiles.forEach(file => {
  const name = file.replace(pagesDir + '/', '').replace('.html', '').replace(/\//g, '_');
  input[`page_${name}`] = file;
});

deptFiles.forEach(file => {
  const name = file.replace(deptsDir + '/', '').replace('.html', '').replace(/\//g, '_');
  input[`dept_${name}`] = file;
});

export default defineConfig({
  root: './',
  base: './',
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: input
    }
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
