// Audio Learning Module
// Handles text-to-speech and audio lesson generation

const audioLearningModule = {
    init: function() {
        console.log('Audio learning module initialized');
        this.attachEventListeners();
        this.loadRecentAudios();
    },
    
    attachEventListeners: function() {
        const form = document.getElementById('audioForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        const downloadAudioBtn = document.getElementById('downloadAudioBtn');
        if (downloadAudioBtn) {
            downloadAudioBtn.addEventListener('click', () => this.downloadAudio());
        }
        
        const copyTranscriptBtn = document.getElementById('copyTranscriptBtn');
        if (copyTranscriptBtn) {
            copyTranscriptBtn.addEventListener('click', () => this.copyTranscript());
        }
    },
    
    handleFormSubmit: async function(e) {
        e.preventDefault();
        
        const topic = document.getElementById('audioTopic').value;
        const length = document.getElementById('audioLength').value;
        
        if (!topic.trim()) {
            alert('Please enter a topic');
            return;
        }
        
        await this.generateAudio(topic, length);
    },
    
    generateAudio: async function(topic, length) {
        const generateBtn = document.querySelector('#audioForm button');
        const outputSection = document.getElementById('audioOutputSection');
        const loadingIndicator = document.getElementById('audioLoadingIndicator');
        const audioSource = document.getElementById('audioSource');
        const transcriptContent = document.getElementById('transcriptContent');
        
        generateBtn.disabled = true;
        outputSection.style.display = 'block';
        loadingIndicator.style.display = 'block';
        
        try {
            const response = await fetch('/api/generate-audio-script', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic: topic,
                    length: length
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                loadingIndicator.style.display = 'none';
                
                this.currentScript = data.script;
                transcriptContent.textContent = data.script;
                
                if (data.audio_url) {
                    audioSource.src = data.audio_url;
                    const audioPlayer = document.getElementById('audioPlayer');
                    audioPlayer.load();
                }
                
                this.loadRecentAudios();
            } else {
                throw new Error(data.error || 'Failed to generate audio');
            }
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            transcriptContent.textContent = 'Error: ' + error.message;
        } finally {
            generateBtn.disabled = false;
        }
    },
    
    downloadAudio: function() {
        const audioPlayer = document.getElementById('audioPlayer');
        const audioSource = audioPlayer.querySelector('source');
        
        if (!audioSource.src) {
            alert('No audio to download');
            return;
        }
        
        const a = document.createElement('a');
        a.href = audioSource.src;
        a.download = 'lesson.mp3';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    },
    
    copyTranscript: function() {
        if (!this.currentScript) {
            alert('No transcript to copy');
            return;
        }
        
        navigator.clipboard.writeText(this.currentScript).then(() => {
            alert('Transcript copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    },
    
    loadRecentAudios: async function() {
        try {
            const response = await fetch('/api/list-audio-files');
            const data = await response.json();
            
            if (data.success && data.files && data.files.length > 0) {
                const audioList = document.getElementById('audioList');
                audioList.innerHTML = '';
                
                data.files.slice(0, 5).forEach(file => {
                    const item = document.createElement('div');
                    item.className = 'audio-item';
                    item.innerHTML = `
                        <h4>${file.filename}</h4>
                        <p>Size: ${file.size}</p>
                        <p>Created: ${file.created}</p>
                        <audio controls style="width: 100%; margin-top: 0.5rem;">
                            <source src="${file.path}" type="audio/mpeg">
                        </audio>
                    `;
                    audioList.appendChild(item);
                });
            }
        } catch (error) {
            console.error('Error loading recent audios:', error);
        }
    },
    
    currentScript: null
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    audioLearningModule.init();
});
