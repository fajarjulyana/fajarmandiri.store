
// Fullscreen Mobile Optimization for Wedding Invitations
document.addEventListener('DOMContentLoaded', function() {
    // Force fullscreen mode
    function enableFullscreen() {
        // Mobile viewport settings
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover');
        } else {
            const meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';
            document.head.appendChild(meta);
        }

        // Add fullscreen CSS
        const style = document.createElement('style');
        style.textContent = `
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                width: 100vw !important;
                min-height: 100vh !important;
                overflow-x: hidden !important;
                -webkit-overflow-scrolling: touch;
                -webkit-text-size-adjust: 100%;
                -ms-text-size-adjust: 100%;
            }

            .container, .invitation-container, .wedding-container {
                max-width: 100% !important;
                width: 100vw !important;
                margin: 0 !important;
                padding: 0 !important;
                box-shadow: none !important;
            }

            /* Hide browser UI on mobile */
            @media screen and (max-width: 768px) {
                body {
                    position: fixed;
                    width: 100%;
                    height: 100%;
                    overflow-y: auto;
                    -webkit-overflow-scrolling: touch;
                }

                .main-content, .wedding-content {
                    height: 100vh;
                    overflow-y: auto;
                }
            }

            /* Desktop fullscreen */
            @media screen and (min-width: 769px) {
                body {
                    width: 100vw;
                    height: 100vh;
                    overflow-x: hidden;
                }
            }

            /* Fix for iOS Safari */
            body {
                -webkit-appearance: none;
                -webkit-tap-highlight-color: transparent;
            }

            /* PWA fullscreen */
            @media all and (display-mode: fullscreen) {
                body {
                    padding-top: env(safe-area-inset-top);
                    padding-bottom: env(safe-area-inset-bottom);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Auto fullscreen for mobile browsers
    function requestFullscreen() {
        const elem = document.documentElement;
        
        // Try different fullscreen APIs
        if (elem.requestFullscreen) {
            elem.requestFullscreen().catch(() => {});
        } else if (elem.webkitRequestFullscreen) {
            elem.webkitRequestFullscreen().catch(() => {});
        } else if (elem.mozRequestFullScreen) {
            elem.mozRequestFullScreen().catch(() => {});
        } else if (elem.msRequestFullscreen) {
            elem.msRequestFullscreen().catch(() => {});
        }
    }

    // Mobile specific optimizations
    function mobileOptimizations() {
        // Hide address bar on mobile
        setTimeout(() => {
            window.scrollTo(0, 1);
        }, 100);

        // Prevent zoom on form inputs
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (!input.style.fontSize || parseFloat(input.style.fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });

        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                window.scrollTo(0, 0);
                document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
            }, 500);
        });

        // Set viewport height custom property
        document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
    }

    // Initialize optimizations
    enableFullscreen();
    mobileOptimizations();

    // Auto request fullscreen on first user interaction
    let fullscreenRequested = false;
    const requestFullscreenOnce = () => {
        if (!fullscreenRequested && document.fullscreenElement === null) {
            requestFullscreen();
            fullscreenRequested = true;
        }
    };

    // Add event listeners for user interaction
    document.addEventListener('click', requestFullscreenOnce, { once: true });
    document.addEventListener('touchstart', requestFullscreenOnce, { once: true });

    // PWA install prompt handling
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
    });

    // Add to homescreen button (optional)
    const addHomeScreenBtn = document.createElement('button');
    addHomeScreenBtn.textContent = 'Tambah ke Home Screen';
    addHomeScreenBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.8);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 14px;
        z-index: 9999;
        display: none;
    `;
    
    if (deferredPrompt) {
        document.body.appendChild(addHomeScreenBtn);
        addHomeScreenBtn.style.display = 'block';
        
        addHomeScreenBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const choiceResult = await deferredPrompt.userChoice;
                deferredPrompt = null;
                addHomeScreenBtn.style.display = 'none';
            }
        });
    }

    // Hide after 5 seconds
    setTimeout(() => {
        addHomeScreenBtn.style.display = 'none';
    }, 5000);
});

// iOS Safari specific fixes
if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
    document.addEventListener('DOMContentLoaded', () => {
        // Prevent bounce scrolling
        document.addEventListener('touchmove', (e) => {
            if (e.target.closest('textarea, input, select')) return;
            e.preventDefault();
        }, { passive: false });

        // Hide Safari bars
        const meta = document.createElement('meta');
        meta.name = 'apple-mobile-web-app-capable';
        meta.content = 'yes';
        document.head.appendChild(meta);

        const meta2 = document.createElement('meta');
        meta2.name = 'apple-mobile-web-app-status-bar-style';
        meta2.content = 'black-translucent';
        document.head.appendChild(meta2);
    });
}
