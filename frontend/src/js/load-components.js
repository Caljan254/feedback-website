// Dynamically load header and footer for Vite
async function loadComponent(elementId, filePath) {
    try {
        // In Vite, we use root-relative paths starting with /
        const fullPath = filePath.startsWith('/') ? filePath : '/' + filePath;
        
        const response = await fetch(fullPath + '?v=' + new Date().getTime());
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const html = await response.text();
        
        // Use a temporary div to process the HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Ensure all relative links and images in the header/footer use root-relative paths
        const fixPaths = (selector, attr) => {
            tempDiv.querySelectorAll(selector).forEach(el => {
                const val = el.getAttribute(attr);
                if (val && !val.startsWith('http') && !val.startsWith('#') && !val.startsWith('/')) {
                    // Prepend / to make it root-relative
                    el.setAttribute(attr, '/' + val);
                }
            });
        };
        
        fixPaths('a', 'href');
        fixPaths('img', 'src');

        document.getElementById(elementId).innerHTML = tempDiv.innerHTML;
        
        // Re-initialize any components that need it (themes, mobile menu, etc.)
        if (typeof initTheme === 'function') initTheme();
        if (typeof setupMobileMenu === 'function') setupMobileMenu();

        // After header is injected, re-run auth + nav highlighting
        if (elementId === 'header-placeholder') {
            if (window.feedbackPortal) {
                window.feedbackPortal.reinitializeComponents();
            } else {
                // feedbackPortal loads after this script on some pages, so retry
                const retryInterval = setInterval(() => {
                    if (window.feedbackPortal) {
                        window.feedbackPortal.reinitializeComponents();
                        clearInterval(retryInterval);
                    }
                }, 100);
                // Give up after 3 seconds
                setTimeout(() => clearInterval(retryInterval), 3000);
            }
        }
        
    } catch (err) {
        console.error(`Failed to load ${filePath}:`, err);
        document.getElementById(elementId).innerHTML = `<p style="color:red; text-align:center;">Error loading component. Please refresh.</p>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadComponent('header-placeholder', 'src/components/layout/header.html');
    loadComponent('footer-placeholder', 'src/components/layout/footer.html');
});