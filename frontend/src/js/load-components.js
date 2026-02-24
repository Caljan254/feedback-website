// Dynamically load header and footer
async function loadComponent(elementId, filePath) {
    try {
        // Get the base path - handle both home and department pages
        const currentPath = window.location.pathname;
        let basePath = '';
        
        if (currentPath.includes('/public/departments/')) {
            // If we're in a department page (public/departments/), go up 2 levels to root (public/departments -> public -> root)
            // Wait, public/departments/admin-feedback.html. To get to root: ../../ (up to public, then up to root)
            basePath = '../../';
        } else if (currentPath.includes('/src/components/pages/')) {
            // If we're in src/components/pages/, go up 3 levels to root (pages -> components -> src -> root)
            basePath = '../../../';
        } else {
            basePath = './';
        }
        
        // Construct full path
        let fullPath = filePath;
        if (!filePath.startsWith('/') && !filePath.startsWith('http')) {
            fullPath = basePath + filePath;
        }
        
        const response = await fetch(fullPath);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const html = await response.text();
        
        // Fix relative links in the injected HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        const links = tempDiv.querySelectorAll('a');
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('http') && !href.startsWith('#') && !href.startsWith('/')) {
                // Prepend basePath to relative links
                link.setAttribute('href', basePath + href);
            }
        });
        
        // Fix image sources too
        const images = tempDiv.querySelectorAll('img');
        images.forEach(img => {
            const src = img.getAttribute('src');
            if (src && !src.startsWith('http') && !src.startsWith('/')) {
                img.setAttribute('src', basePath + src);
            }
        });

        document.getElementById(elementId).innerHTML = tempDiv.innerHTML;
        
        // Re-initialize any components that need it
        if (window.feedbackPortal) {
            window.feedbackPortal.reinitializeComponents();
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