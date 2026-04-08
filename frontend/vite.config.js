import { defineConfig } from 'vite';
import { resolve } from 'path';
import fs from 'fs';

// Helper to get all HTML files in a directory
function getHtmlFiles(dir, files_ = []) {
  // Check if directory exists
  if (!fs.existsSync(dir)) return files_;
  
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
      input: input,
      output: {
        // Ensure assets are properly named
        assetFileNames: 'assets/[name].[hash][extname]',
        chunkFileNames: 'assets/[name].[hash].js',
        entryFileNames: 'assets/[name].[hash].js'
      }
    },
    // Ensure build doesn't fail on warnings
    reportCompressedSize: false,
    chunkSizeWarningLimit: 1000
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  plugins: [
    {
      name: 'copy-missing-assets',
      closeBundle() {
        const copyDir = (src, dest) => {
          if (!fs.existsSync(src)) return;
          if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
          const entries = fs.readdirSync(src, { withFileTypes: true });
          for (let entry of entries) {
            const srcPath = resolve(src, entry.name);
            const destPath = resolve(dest, entry.name);
            if (entry.isDirectory()) {
              copyDir(srcPath, destPath);
            } else {
              try {
                fs.copyFileSync(srcPath, destPath);
              } catch (err) {
                console.log(`Warning: Could not copy ${srcPath} - ${err.message}`);
              }
            }
          }
        };
        
        // Copy layout folder
        const layoutSrc = resolve(__dirname, 'src/components/layout');
        const layoutDest = resolve(__dirname, 'dist/src/components/layout');
        if (fs.existsSync(layoutSrc)) {
          copyDir(layoutSrc, layoutDest);
        }
        
        // Copy js folder
        const jsSrc = resolve(__dirname, 'src/js');
        const jsDest = resolve(__dirname, 'dist/src/js');
        if (fs.existsSync(jsSrc)) {
          copyDir(jsSrc, jsDest);
        }
        
        // Copy CSS folder if it exists
        const cssSrc = resolve(__dirname, 'src/css');
        const cssDest = resolve(__dirname, 'dist/src/css');
        if (fs.existsSync(cssSrc)) {
          copyDir(cssSrc, cssDest);
        }
        
        console.log('✅ Asset copying completed!');
      }
    }
  ],
  // Define environment variables for production
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production'),
    'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '/api')
  }
});