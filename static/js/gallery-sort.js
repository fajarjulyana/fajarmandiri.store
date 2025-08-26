
// Enhanced Gallery sorting and display script for all wedding templates
document.addEventListener('DOMContentLoaded', function() {
    console.log('Gallery script loaded');
    
    // Find gallery sections - check both new and old systems
    const gallerySection = document.querySelector('.gallery-section');
    const portraitGrid = document.querySelector('.gallery-portrait-grid');
    const landscapeGrid = document.querySelector('.gallery-landscape-grid');
    
    // Check for original gallery items - support both systems
    const originalGalleryItems = document.querySelectorAll('.gallery-item, .original-gallery-items .gallery-item');
    const oldGalleryGrid = document.querySelector('.gallery-grid');
    
    console.log('Found gallery section:', !!gallerySection);
    console.log('Found portrait grid:', !!portraitGrid);
    console.log('Found landscape grid:', !!landscapeGrid);
    console.log('Found gallery items:', originalGalleryItems.length);
    console.log('Found old gallery grid:', !!oldGalleryGrid);
    
    // If no gallery items found, exit
    if (originalGalleryItems.length === 0) {
        console.log('No gallery items found, exiting');
        return;
    }
    
    // Ensure grids exist, create if needed
    if (gallerySection && (!portraitGrid || !landscapeGrid)) {
        console.log('Creating missing grid containers');
        
        if (!portraitGrid) {
            const portraitSection = document.createElement('div');
            portraitSection.className = 'gallery-portrait-section';
            portraitSection.innerHTML = `
                <h3 class="gallery-portrait-title">Foto Portrait</h3>
                <div class="gallery-portrait-grid"></div>
            `;
            gallerySection.appendChild(portraitSection);
        }
        
        if (!landscapeGrid) {
            const landscapeSection = document.createElement('div');
            landscapeSection.className = 'gallery-landscape-section';
            landscapeSection.innerHTML = `
                <h3 class="gallery-landscape-title">Foto Landscape</h3>
                <div class="gallery-landscape-grid"></div>
            `;
            gallerySection.appendChild(landscapeSection);
        }
    }
    
    // Get updated grid references
    const finalPortraitGrid = document.querySelector('.gallery-portrait-grid');
    const finalLandscapeGrid = document.querySelector('.gallery-landscape-grid');
    
    console.log('Final portrait grid:', !!finalPortraitGrid);
    console.log('Final landscape grid:', !!finalLandscapeGrid);
    
    // Sort photos by aspect ratio
    let processedCount = 0;
    const totalItems = originalGalleryItems.length;
    
    originalGalleryItems.forEach((item, index) => {
        const img = item.querySelector('img');
        if (!img || !img.src) {
            console.log('No image found in item', index);
            return;
        }
        
        console.log('Processing image:', img.src);
        
        // Create new image to check dimensions
        const tempImg = new Image();
        tempImg.onload = function() {
            const aspectRatio = this.naturalWidth / this.naturalHeight;
            const newItem = item.cloneNode(true);
            
            console.log('Image loaded:', img.src, 'Aspect ratio:', aspectRatio);
            
            if (aspectRatio < 1) {
                // Portrait image
                newItem.className = 'gallery-portrait-item gallery-fade-in';
                if (finalPortraitGrid) {
                    finalPortraitGrid.appendChild(newItem);
                    console.log('Added to portrait grid');
                }
            } else {
                // Landscape image
                newItem.className = 'gallery-landscape-item gallery-fade-in';
                if (finalLandscapeGrid) {
                    finalLandscapeGrid.appendChild(newItem);
                    console.log('Added to landscape grid');
                }
            }
            
            // Add fade-in animation
            setTimeout(() => {
                newItem.classList.add('visible');
            }, index * 100);
            
            processedCount++;
            
            // Hide original items after all processed
            if (processedCount === totalItems) {
                console.log('All images processed, hiding originals');
                originalGalleryItems.forEach(originalItem => {
                    originalItem.style.display = 'none';
                });
                
                // Hide old gallery grid if exists
                if (oldGalleryGrid) {
                    oldGalleryGrid.style.display = 'none';
                }
            }
        };
        
        tempImg.onerror = function() {
            console.error('Failed to load image:', img.src);
            processedCount++;
        };
        
        tempImg.src = img.src;
        
        // If image is already loaded (cached)
        if (tempImg.complete) {
            tempImg.onload();
        }
    });
    
    // Fallback: if no sorting happens, ensure photos are visible
    setTimeout(() => {
        if (processedCount === 0 && originalGalleryItems.length > 0) {
            console.log('Fallback: showing original gallery items');
            originalGalleryItems.forEach(item => {
                item.style.display = 'block';
                item.classList.add('gallery-fade-in', 'visible');
            });
        }
    }, 2000);
});
