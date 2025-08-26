
// Enhanced Gallery sorting and display script for all wedding templates
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced Gallery script loaded');
    
    // Find gallery sections - support multiple template structures
    const gallerySection = document.querySelector('.gallery-section');
    const existingGalleryGrid = document.querySelector('.gallery-grid');
    
    // Check for gallery items in different possible containers
    const allGalleryItems = document.querySelectorAll('.gallery-item, .gallery-grid .gallery-item, .prewedding-item');
    
    console.log('Found gallery section:', !!gallerySection);
    console.log('Found existing gallery grid:', !!existingGalleryGrid);
    console.log('Found gallery items:', allGalleryItems.length);
    
    // If no gallery items found, exit
    if (allGalleryItems.length === 0) {
        console.log('No gallery items found, exiting');
        return;
    }
    
    // Create enhanced gallery structure
    if (gallerySection) {
        createEnhancedGalleryStructure();
    }
    
    function createEnhancedGalleryStructure() {
        // Create new gallery container with animations
        const enhancedGalleryHTML = `
            <div class="enhanced-gallery-container">
                <div class="gallery-header">
                    <h3 class="gallery-title">Galeri Foto</h3>
                    <p class="gallery-subtitle">Momen indah menuju hari bahagia</p>
                    <div class="gallery-filters">
                        <button class="filter-btn active" data-filter="all">Semua</button>
                        <button class="filter-btn" data-filter="portrait">Portrait</button>
                        <button class="filter-btn" data-filter="landscape">Landscape</button>
                    </div>
                </div>
                
                <div class="masonry-gallery" id="masonryGallery">
                    <!-- Photos will be added here dynamically -->
                </div>
                
                <div class="gallery-navigation">
                    <button class="nav-btn prev-btn" id="prevBtn">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <div class="gallery-dots" id="galleryDots"></div>
                    <button class="nav-btn next-btn" id="nextBtn">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            </div>
            
            <!-- Enhanced Photo Modal -->
            <div class="enhanced-photo-modal" id="enhancedPhotoModal">
                <div class="modal-overlay" id="modalOverlay"></div>
                <div class="modal-container">
                    <button class="modal-close" id="modalClose">
                        <i class="fas fa-times"></i>
                    </button>
                    <button class="modal-nav modal-prev" id="modalPrev">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <button class="modal-nav modal-next" id="modalNext">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                    <div class="modal-content">
                        <img id="modalImage" src="" alt="Gallery Photo">
                        <div class="modal-info">
                            <h4 id="modalTitle">Foto Galeri</h4>
                            <p id="modalCounter">1 / 1</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add enhanced gallery CSS
        addEnhancedGalleryStyles();
        
        // Replace existing gallery or add to section
        if (existingGalleryGrid) {
            existingGalleryGrid.style.display = 'none';
        }
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = enhancedGalleryHTML;
        gallerySection.appendChild(tempDiv.firstElementChild);
        
        // Process and add photos
        processAndAddPhotos();
        
        // Initialize gallery functionality
        initializeGalleryFeatures();
    }
    
    function addEnhancedGalleryStyles() {
        const styles = `
            <style>
            .enhanced-gallery-container {
                padding: 2rem 0;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            }
            
            .gallery-header {
                text-align: center;
                margin-bottom: 2rem;
                animation: fadeInUp 0.8s ease-out;
            }
            
            .gallery-title {
                font-size: 2.5rem;
                color: #333;
                margin-bottom: 0.5rem;
                font-weight: 300;
                letter-spacing: 2px;
            }
            
            .gallery-subtitle {
                color: #666;
                font-size: 1.1rem;
                margin-bottom: 1.5rem;
                font-style: italic;
            }
            
            .gallery-filters {
                display: flex;
                justify-content: center;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .filter-btn {
                padding: 0.5rem 1.5rem;
                border: 2px solid #d4af37;
                background: transparent;
                color: #d4af37;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .filter-btn.active,
            .filter-btn:hover {
                background: #d4af37;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
            }
            
            .masonry-gallery {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                padding: 0 1rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .gallery-photo-item {
                position: relative;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                opacity: 0;
                transform: translateY(30px) scale(0.8);
                animation: photoFadeIn 0.6s ease-out forwards;
            }
            
            .gallery-photo-item:nth-child(odd) {
                animation-delay: 0.1s;
            }
            
            .gallery-photo-item:nth-child(even) {
                animation-delay: 0.2s;
            }
            
            .gallery-photo-item:hover {
                transform: translateY(-10px) scale(1.02);
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            }
            
            .gallery-photo-item.portrait {
                grid-row: span 2;
            }
            
            .gallery-photo-item img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.4s ease;
            }
            
            .gallery-photo-item:hover img {
                transform: scale(1.1);
            }
            
            .gallery-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(212, 175, 55, 0.8), rgba(139, 69, 19, 0.8));
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .gallery-photo-item:hover .gallery-overlay {
                opacity: 1;
            }
            
            .gallery-overlay i {
                color: white;
                font-size: 2rem;
                transform: scale(0.5);
                transition: transform 0.3s ease;
            }
            
            .gallery-photo-item:hover .gallery-overlay i {
                transform: scale(1);
            }
            
            .gallery-navigation {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                margin-top: 2rem;
            }
            
            .nav-btn {
                width: 50px;
                height: 50px;
                border: none;
                background: #d4af37;
                color: white;
                border-radius: 50%;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .nav-btn:hover {
                background: #b8941f;
                transform: scale(1.1);
            }
            
            .gallery-dots {
                display: flex;
                gap: 0.5rem;
            }
            
            .dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #ccc;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .dot.active {
                background: #d4af37;
                transform: scale(1.2);
            }
            
            .enhanced-photo-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 9999;
                display: none;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .enhanced-photo-modal.active {
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 1;
            }
            
            .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.9);
                backdrop-filter: blur(10px);
            }
            
            .modal-container {
                position: relative;
                max-width: 90vw;
                max-height: 90vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .modal-content img {
                max-width: 100%;
                max-height: 80vh;
                object-fit: contain;
                border-radius: 10px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.5);
                animation: modalImageZoom 0.3s ease-out;
            }
            
            .modal-close {
                position: absolute;
                top: -50px;
                right: -50px;
                width: 40px;
                height: 40px;
                border: none;
                background: rgba(255,255,255,0.2);
                color: white;
                border-radius: 50%;
                cursor: pointer;
                font-size: 1.2rem;
                transition: all 0.3s ease;
            }
            
            .modal-close:hover {
                background: rgba(255,255,255,0.3);
                transform: scale(1.1);
            }
            
            .modal-nav {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 50px;
                height: 50px;
                border: none;
                background: rgba(212, 175, 55, 0.8);
                color: white;
                border-radius: 50%;
                cursor: pointer;
                font-size: 1.2rem;
                transition: all 0.3s ease;
            }
            
            .modal-prev {
                left: -80px;
            }
            
            .modal-next {
                right: -80px;
            }
            
            .modal-nav:hover {
                background: rgba(212, 175, 55, 1);
                transform: translateY(-50%) scale(1.1);
            }
            
            .modal-info {
                position: absolute;
                bottom: -60px;
                left: 50%;
                transform: translateX(-50%);
                text-align: center;
                color: white;
            }
            
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
            
            @keyframes photoFadeIn {
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            @keyframes modalImageZoom {
                from {
                    transform: scale(0.8);
                    opacity: 0;
                }
                to {
                    transform: scale(1);
                    opacity: 1;
                }
            }
            
            @media (max-width: 768px) {
                .masonry-gallery {
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                
                .gallery-filters {
                    flex-wrap: wrap;
                    gap: 0.5rem;
                }
                
                .filter-btn {
                    padding: 0.4rem 1rem;
                    font-size: 0.9rem;
                }
                
                .modal-nav {
                    display: none;
                }
                
                .modal-close {
                    top: 20px;
                    right: 20px;
                }
            }
            
            .hidden {
                display: none !important;
            }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    let galleryPhotos = [];
    let currentFilter = 'all';
    let currentModalIndex = 0;
    
    function processAndAddPhotos() {
        // Enhanced photo processing with automatic orientation detection
        const portraitGrid = document.querySelector('.gallery-portrait-grid');
        const landscapeGrid = document.querySelector('.gallery-landscape-grid');
        
        if (!portraitGrid || !landscapeGrid) {
            console.log('Portrait or landscape grid not found, using fallback method');
            return;
        }
        
        // Clear existing photos
        portraitGrid.innerHTML = '';
        landscapeGrid.innerHTML = '';
        
        const allImages = document.querySelectorAll('.gallery-portrait-item img, .gallery-landscape-item img');
        
        allImages.forEach((img, index) => {
            if (!img.src) return;
            
            // Create temporary image to get dimensions
            const tempImg = new Image();
            tempImg.onload = function() {
                const aspectRatio = this.naturalWidth / this.naturalHeight;
                const isPortrait = aspectRatio < 0.85; // More precise threshold
                
                // Create gallery item
                const galleryItem = document.createElement('div');
                galleryItem.className = isPortrait ? 'gallery-portrait-item' : 'gallery-landscape-item';
                
                const imgElement = document.createElement('img');
                imgElement.src = img.src;
                imgElement.alt = img.alt || 'Wedding Gallery';
                imgElement.loading = 'lazy';
                
                galleryItem.appendChild(imgElement);
                
                // Add to appropriate grid
                if (isPortrait) {
                    portraitGrid.appendChild(galleryItem);
                } else {
                    landscapeGrid.appendChild(galleryItem);
                }
                
                // Add fade-in animation
                setTimeout(() => {
                    galleryItem.classList.add('gallery-fade-in', 'visible');
                }, index * 100);
            };
            tempImg.src = img.src;
        });
        
        // Hide original photos to prevent duplicates
        allImages.forEach(img => {
            const parentItem = img.closest('.gallery-portrait-item, .gallery-landscape-item');
            if (parentItem) {
                parentItem.style.display = 'none';
            }
        });
    }
    
    function createPhotoElement(photoData, index) {
        const photoElement = document.createElement('div');
        photoElement.className = 'gallery-photo-item';
        photoElement.style.animationDelay = `${index * 0.1}s`;
        photoElement.innerHTML = `
            <img src="${photoData.src}" alt="${photoData.alt}" loading="lazy">
            <div class="gallery-overlay">
                <i class="fas fa-search-plus"></i>
            </div>
        `;
        
        photoElement.addEventListener('click', () => openModal(index));
        return photoElement;
    }
    
    function createNavigationDots() {
        const dotsContainer = document.getElementById('galleryDots');
        dotsContainer.innerHTML = '';
        
        galleryPhotos.forEach((_, index) => {
            const dot = document.createElement('div');
            dot.className = `dot ${index === 0 ? 'active' : ''}`;
            dot.addEventListener('click', () => scrollToPhoto(index));
            dotsContainer.appendChild(dot);
        });
    }
    
    function initializeGalleryFeatures() {
        // Filter functionality
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                filterPhotos();
            });
        });
        
        // Navigation
        document.getElementById('prevBtn').addEventListener('click', () => scrollToPhoto(currentModalIndex - 1));
        document.getElementById('nextBtn').addEventListener('click', () => scrollToPhoto(currentModalIndex + 1));
        
        // Modal functionality
        const modal = document.getElementById('enhancedPhotoModal');
        const modalImage = document.getElementById('modalImage');
        const modalCounter = document.getElementById('modalCounter');
        const modalClose = document.getElementById('modalClose');
        const modalOverlay = document.getElementById('modalOverlay');
        const modalPrev = document.getElementById('modalPrev');
        const modalNext = document.getElementById('modalNext');
        
        modalClose.addEventListener('click', closeModal);
        modalOverlay.addEventListener('click', closeModal);
        modalPrev.addEventListener('click', () => navigateModal(-1));
        modalNext.addEventListener('click', () => navigateModal(1));
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (modal.classList.contains('active')) {
                switch(e.key) {
                    case 'Escape':
                        closeModal();
                        break;
                    case 'ArrowLeft':
                        navigateModal(-1);
                        break;
                    case 'ArrowRight':
                        navigateModal(1);
                        break;
                }
            }
        });
    }
    
    function filterPhotos() {
        const photoItems = document.querySelectorAll('.gallery-photo-item');
        
        photoItems.forEach((item, index) => {
            const photo = galleryPhotos[index];
            const shouldShow = currentFilter === 'all' || photo.orientation === currentFilter;
            
            if (shouldShow) {
                item.classList.remove('hidden');
                item.style.animation = 'photoFadeIn 0.6s ease-out forwards';
            } else {
                item.classList.add('hidden');
            }
        });
    }
    
    function openModal(index) {
        currentModalIndex = index;
        const modal = document.getElementById('enhancedPhotoModal');
        const modalImage = document.getElementById('modalImage');
        const modalCounter = document.getElementById('modalCounter');
        const modalTitle = document.getElementById('modalTitle');
        
        modalImage.src = galleryPhotos[index].src;
        modalImage.alt = galleryPhotos[index].alt;
        modalCounter.textContent = `${index + 1} / ${galleryPhotos.length}`;
        modalTitle.textContent = galleryPhotos[index].alt;
        
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeModal() {
        const modal = document.getElementById('enhancedPhotoModal');
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    function navigateModal(direction) {
        const newIndex = currentModalIndex + direction;
        if (newIndex >= 0 && newIndex < galleryPhotos.length) {
            openModal(newIndex);
        }
    }
    
    function scrollToPhoto(index) {
        if (index >= 0 && index < galleryPhotos.length) {
            currentModalIndex = index;
            updateNavigationDots();
        }
    }
    
    function updateNavigationDots() {
        const dots = document.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentModalIndex);
        });
    }
    
    // Auto-play slideshow (optional)
    let autoPlayInterval;
    
    function startAutoPlay() {
        autoPlayInterval = setInterval(() => {
            const nextIndex = (currentModalIndex + 1) % galleryPhotos.length;
            scrollToPhoto(nextIndex);
        }, 5000);
    }
    
    function stopAutoPlay() {
        clearInterval(autoPlayInterval);
    }
    
    // Initialize gallery processing automatically
    function initializeGalleryAutomatically() {
        // Wait for images to load
        setTimeout(() => {
            processAndAddPhotos();
            
            // Add intersection observer for fade-in animations
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.1 });
            
            // Observe all gallery items
            document.querySelectorAll('.gallery-portrait-item, .gallery-landscape-item').forEach(item => {
                observer.observe(item);
            });
        }, 500);
    }
    
    // Run initialization when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeGalleryAutomatically);
    } else {
        initializeGalleryAutomatically();
    }
    
    // Touch/swipe support for mobile
    let startX = 0;
    let startY = 0;
    
    document.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', (e) => {
        if (!startX || !startY) return;
        
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        
        const diffX = startX - endX;
        const diffY = startY - endY;
        
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX > 0) {
                navigateModal(1); // Swipe left - next
            } else {
                navigateModal(-1); // Swipe right - prev
            }
        }
        
        startX = 0;
        startY = 0;
    });
});
