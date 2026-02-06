// Text Explanation Module
// Handles text generation for ML topics

const textExplanationModule = {
    init: function() {
        console.log('Text explanation module initialized');
        this.attachEventListeners();
    },
    
    attachEventListeners: function() {
        const form = document.getElementById('textExplanationForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        const copyBtn = document.getElementById('copyBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyToClipboard());
        }
        
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadAsText());
        }
        
        const generateAudioBtn = document.getElementById('generateAudioBtn');
        if (generateAudioBtn) {
            generateAudioBtn.addEventListener('click', () => this.generateAudio());
        }
    },
    
    handleFormSubmit: async function(e) {
        e.preventDefault();
        
        const topic = document.getElementById('topic').value;
        const complexity = document.getElementById('complexity').value;
        
        if (!topic.trim()) {
            alert('Please enter a topic');
            return;
        }
        
        await this.generateExplanation(topic, complexity);
    },
    
    generateExplanation: async function(topic, complexity) {
        const generateBtn = document.querySelector('#textExplanationForm button');
        const outputSection = document.getElementById('outputSection');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const explanationContent = document.getElementById('explanationContent');
        
        generateBtn.disabled = true;
        outputSection.style.display = 'block';
        loadingIndicator.style.display = 'block';
        explanationContent.style.display = 'none';
        
        try {
            const response = await fetch('/api/generate-explanation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic: topic,
                    complexity: complexity
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                loadingIndicator.style.display = 'none';
                explanationContent.style.display = 'block';
                explanationContent.textContent = data.explanation;
                this.currentExplanation = data.explanation;
            } else {
                throw new Error(data.error || 'Failed to generate explanation');
            }
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            explanationContent.style.display = 'block';
            explanationContent.textContent = 'Error: ' + error.message;
        } finally {
            generateBtn.disabled = false;
        }
    },
    
    copyToClipboard: function() {
        if (!this.currentExplanation) {
            alert('No explanation to copy');
            return;
        }
        
        navigator.clipboard.writeText(this.currentExplanation).then(() => {
            alert('Explanation copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard');
        });
    },
    
    downloadAsText: function() {
        if (!this.currentExplanation) {
            alert('No explanation to download');
            return;
        }
        
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(this.currentExplanation));
        element.setAttribute('download', 'ml_explanation.txt');
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    },
    
    generateAudio: async function() {
        if (!this.currentExplanation) {
            alert('No explanation to convert to audio');
            return;
        }
        
        const topic = document.getElementById('topic').value;
        
        try {
            const response = await fetch('/api/generate-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: this.currentExplanation,
                    topic: topic,
                    type: 'tts'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Audio generated successfully! Opening audio learning page...');
                // Could redirect or open audio player
                window.location.href = '/audio-learning';
            } else {
                alert('Error: ' + (data.error || 'Failed to generate audio'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error generating audio: ' + error.message);
        }
    },
    
    currentExplanation: null
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    textExplanationModule.init();
});
