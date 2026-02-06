// Image Visualization Module
// Handles AI-powered diagram and image generation

const imageVisualizationModule = {
    init: function() {
        console.log('Image visualization module initialized');
        this.attachEventListeners();
        this.loadRecentImages();
    },
    
    attachEventListeners: function() {
        const form = document.getElementById('imageForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        const downloadImageBtn = document.getElementById('downloadImageBtn');
        if (downloadImageBtn) {
            downloadImageBtn.addEventListener('click', () => this.downloadImages());
        }
    },
    
    handleFormSubmit: async function(e) {
        e.preventDefault();
        
        const concept = document.getElementById('imageConcept').value;
        const diagramType = document.getElementById('diagramType').value;
        const backend = document.getElementById('backendSelect').value;
        const multiple = document.getElementById('multipleImages').checked;
        
        if (!concept.trim()) {
            alert('Please enter a concept');
            return;
        }
        
        if (multiple) {
            await this.generateMultipleImages(concept, diagramType, backend);
        } else {
            await this.generateImage(concept, diagramType, backend);
        }
    },
    
    generateImage: async function(concept, diagramType, backend) {
        const generateBtn = document.querySelector('#imageForm button');
        const outputSection = document.getElementById('imageOutputSection');
        const loadingIndicator = document.getElementById('imageLoadingIndicator');
        const gallery = document.getElementById('imageGallery');
        
        generateBtn.disabled = true;
        outputSection.style.display = 'block';
        loadingIndicator.style.display = 'block';
        gallery.innerHTML = '';
        
        try {
            const response = await fetch('/api/generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    concept: concept,
                    diagram_type: diagramType,
                    backend: backend
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                loadingIndicator.style.display = 'none';
                this.displayImage(data.image_url, diagramType, gallery);
                this.generatedImages = [data];
            } else {
                throw new Error(data.error || 'Failed to generate image');
            }
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            gallery.innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
        } finally {
            generateBtn.disabled = false;
        }
    },
    
    generateMultipleImages: async function(concept, diagramType, backend) {
        const generateBtn = document.querySelector('#imageForm button');
        const outputSection = document.getElementById('imageOutputSection');
        const loadingIndicator = document.getElementById('imageLoadingIndicator');
        const gallery = document.getElementById('imageGallery');
        
        generateBtn.disabled = true;
        outputSection.style.display = 'block';
        loadingIndicator.style.display = 'block';
        gallery.innerHTML = '';
        
        try {
            const response = await fetch('/api/generate-images-multiple', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    concept: concept,
                    count: 3
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                loadingIndicator.style.display = 'none';
                this.generatedImages = data.images;
                
                data.images.forEach((img, index) => {
                    this.displayImage(img.image_url, img.diagram_type, gallery);
                });
            } else {
                throw new Error(data.error || 'Failed to generate images');
            }
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            gallery.innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
        } finally {
            generateBtn.disabled = false;
        }
    },
    
    displayImage: function(imageUrl, diagramType, gallery) {
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.innerHTML = `
            <img src="${imageUrl}" alt="${diagramType}">
            <div class="gallery-item-info">
                <h4>${diagramType} Diagram</h4>
                <p>Click to download</p>
            </div>
        `;
        
        item.addEventListener('click', () => {
            const a = document.createElement('a');
            a.href = imageUrl;
            a.download = `diagram_${Date.now()}.png`;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
        
        gallery.appendChild(item);
    },
    
    downloadImages: function() {
        if (!this.generatedImages || this.generatedImages.length === 0) {
            alert('No images to download');
            return;
        }
        
        this.generatedImages.forEach((img, index) => {
            const a = document.createElement('a');
            a.href = img.image_url;
            a.download = `diagram_${index + 1}.png`;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            // Stagger downloads slightly
            if (index < this.generatedImages.length - 1) {
                setTimeout(() => {}, 500);
            }
        });
    },
    
    loadRecentImages: async function() {
        try {
            const response = await fetch('/api/list-images');
            const data = await response.json();
            
            if (data.success && data.images && data.images.length > 0) {
                const imageList = document.getElementById('imageListContainer');
                imageList.innerHTML = '';
                
                data.images.slice(0, 6).forEach(img => {
                    const item = document.createElement('div');
                    item.className = 'image-item';
                    item.innerHTML = `
                        <img src="${img.path}" alt="${img.filename}">
                    `;
                    
                    item.addEventListener('click', () => {
                        const modal = document.createElement('div');
                        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000;';
                        modal.innerHTML = `
                            <div style="background: white; padding: 2rem; border-radius: 10px; max-width: 90%; max-height: 90%;">
                                <img src="${img.path}" style="max-width: 100%; max-height: 80vh;">
                                <p style="margin-top: 1rem; text-align: center;">${img.filename}</p>
                            </div>
                        `;
                        modal.addEventListener('click', () => modal.remove());
                        document.body.appendChild(modal);
                    });
                    
                    imageList.appendChild(item);
                });
            }
        } catch (error) {
            console.error('Error loading recent images:', error);
        }
    },
    
    generatedImages: []
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    imageVisualizationModule.init();
});
