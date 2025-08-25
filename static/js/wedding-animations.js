
/* Universal Wedding Template Animations and Music Handler */

// Animation CSS
const animationCSS = `
/* Animation Keyframes */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes zoomIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes bounce {
    0%, 20%, 53%, 80%, 100% {
        transform: translateY(0);
    }
    40%, 43% {
        transform: translateY(-30px);
    }
    70% {
        transform: translateY(-15px);
    }
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
    100% {
        transform: scale(1);
    }
}

@keyframes rotateIn {
    from {
        opacity: 0;
        transform: rotate(-200deg);
    }
    to {
        opacity: 1;
        transform: rotate(0deg);
    }
}

/* Animation Classes */
.fade-in {
    animation: fadeInUp 1s ease-out;
}

.animate-slideInUp {
    animation: fadeInUp 0.8s ease-out;
}

.animate-slideInLeft {
    animation: slideInLeft 1s ease-out;
}

.animate-slideInRight {
    animation: slideInRight 1s ease-out;
}

.animate-zoomIn {
    animation: zoomIn 0.6s ease-out;
}

.animate-bounce {
    animation: bounce 2s infinite;
}

.animate-pulse {
    animation: pulse 2s infinite;
}

.animate-rotateIn {
    animation: rotateIn 1s ease-out;
}

/* Gallery Overlay Effects */
.gallery-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.gallery-item:hover .gallery-overlay {
    opacity: 1;
}

.gallery-overlay i {
    font-size: 2rem;
}

/* Smooth transitions for all elements */
* {
    transition: all 0.3s ease;
}
`;

// Initialize animations and music
function initWeddingFeatures() {
    // Inject animation CSS
    const style = document.createElement('style');
    style.textContent = animationCSS;
    document.head.appendChild(style);

    // Initialize music autoplay
    initMusicAutoplay();

    // Initialize scroll animations
    initScrollAnimations();

    // Initialize gallery enhancements
    enhanceGallery();
}

function initMusicAutoplay() {
    const music = document.getElementById('backgroundMusic');
    const musicToggle = document.getElementById('musicToggle');
    
    if (!music) return;
    
    let isPlaying = false;

    // Add bounce animation to music toggle
    if (musicToggle) {
        musicToggle.classList.add('animate-bounce');
    }

    // Auto start music when page loads
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            music.play().then(() => {
                if (musicToggle) {
                    musicToggle.innerHTML = '<i class="fas fa-pause"></i>';
                }
                isPlaying = true;
            }).catch(() => {
                console.log('Autoplay blocked, waiting for user interaction');
            });
        }, 1000);
    });

    // Music toggle functionality
    if (musicToggle) {
        musicToggle.addEventListener('click', function() {
            if (isPlaying) {
                music.pause();
                musicToggle.innerHTML = '<i class="fas fa-music"></i>';
                isPlaying = false;
            } else {
                music.play();
                musicToggle.innerHTML = '<i class="fas fa-pause"></i>';
                isPlaying = true;
            }
        });
    }

    // Fallback: Auto play music on first user interaction
    document.addEventListener('click', function() {
        if (!isPlaying) {
            music.play().then(() => {
                if (musicToggle) {
                    musicToggle.innerHTML = '<i class="fas fa-pause"></i>';
                }
                isPlaying = true;
            }).catch(() => {
                console.log('Music play failed');
            });
        }
    }, { once: true });
}

function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                
                // Add staggered animation to children
                const children = entry.target.querySelectorAll('.gallery-item, .countdown-item, .info-card');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.classList.add('animate-zoomIn');
                    }, index * 200);
                });
            }
        });
    }, observerOptions);

    // Observe all sections and content elements
    document.querySelectorAll('section, .content-section, .hero-section').forEach(element => {
        observer.observe(element);
    });
}

function enhanceGallery() {
    // Add overlay to gallery items that don't have it
    document.querySelectorAll('.gallery-item').forEach(item => {
        if (!item.querySelector('.gallery-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'gallery-overlay';
            overlay.innerHTML = '<i class="fas fa-expand"></i>';
            item.appendChild(overlay);
        }
        
        // Add hover effects
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.05)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initWeddingFeatures);

// Lightbox functionality
function openLightbox(imageSrc) {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox-overlay';
    lightbox.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeInUp 0.3s ease-out;
    `;
    
    const img = document.createElement('img');
    img.src = imageSrc;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        border-radius: 10px;
        animation: zoomIn 0.3s ease-out;
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '×';
    closeBtn.style.cssText = `
        position: absolute;
        top: 20px;
        right: 30px;
        background: none;
        border: none;
        color: white;
        font-size: 40px;
        cursor: pointer;
    `;
    
    closeBtn.onclick = function() {
        document.body.removeChild(lightbox);
    };
    
    lightbox.onclick = function(e) {
        if (e.target === lightbox) {
            document.body.removeChild(lightbox);
        }
    };
    
    lightbox.appendChild(img);
    lightbox.appendChild(closeBtn);
    document.body.appendChild(lightbox);
}
