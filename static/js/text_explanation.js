// Text Explanation Module
// Handles text generation for ML topics

const textExplanationModule = {
    init: function() {
        console.log('Text explanation module initialized');
        this.initTopicFromUrl();
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

        const nextTopicBtn = document.getElementById('nextTopicBtn');
        if (nextTopicBtn) {
            nextTopicBtn.addEventListener('click', () => this.goToNextTopic());
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
        const nextTopicBtn = document.getElementById('nextTopicBtn');
        
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
                explanationContent.innerHTML = this.formatText(data.explanation);
                this.currentExplanation = data.explanation;
                if (nextTopicBtn && this.currentTopicId) nextTopicBtn.style.display = 'inline-block';
                await this.trackProgress('text');
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

    initTopicFromUrl: async function() {
        const params = new URLSearchParams(window.location.search);
        const topicId = params.get('topic');
        this.currentTopicId = topicId;
        this.pageStartTs = Date.now();

        const nextTopicBtn = document.getElementById('nextTopicBtn');
        if (nextTopicBtn) nextTopicBtn.style.display = topicId ? 'inline-block' : 'none';

        if (!topicId) return;

        try {
            const resp = await fetch(`/api/topic/${encodeURIComponent(topicId)}`);
            const data = await resp.json();
            if (data.success && data.topic && data.topic.title) {
                const topicInput = document.getElementById('topic');
                if (topicInput) topicInput.value = data.topic.title;
            }
        } catch (e) {
            // non-fatal
        }
    },

    goToNextTopic: async function() {
        if (!this.currentTopicId) return;

        try {
            const resp = await fetch(`/api/topic-next/${encodeURIComponent(this.currentTopicId)}`);
            const data = await resp.json();

            if (!data.success || !data.has_next || !data.next_topic || !data.next_topic.topic) {
                alert('No next topic available.');
                return;
            }

            const nextTopic = data.next_topic.topic;
            const contentType = nextTopic.content_type || 'text';
            const routes = {
                text: '/text-explanation',
                code: '/code-generation',
                audio: '/audio-learning',
                image: '/image-visualization'
            };

            const route = routes[contentType] || '/text-explanation';
            window.location.href = `${route}?topic=${encodeURIComponent(nextTopic.id)}`;
        } catch (e) {
            alert('Failed to load next topic.');
        }
    },

    trackProgress: async function(modality) {
        if (!this.currentTopicId) return;
        const token = localStorage.getItem('auth_token');
        const headers = token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };

        // Best-effort time spent since page load, in minutes (int)
        const minutes = Math.max(0, Math.round((Date.now() - (this.pageStartTs || Date.now())) / 60000));

        try {
            const resp = await fetch('/api/update-progress', {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    topic_id: this.currentTopicId,
                    completed: true,
                    time_spent: minutes,
                    modality,
                    event: 'generated'
                })
            });

            try {
                const data = await resp.json();
                // Removed auto-navigation to quiz
            } catch (e) {
                // ignore
            }
        } catch (e) {
            // non-fatal
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
                    audio_type: 'tts'
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
    
    formatText: function(text) {
        // Basic text formatting
        let formatted = text
            // Convert line breaks to paragraphs
            .split('\n\n')
            .map(paragraph => {
                if (paragraph.trim()) {
                    // Format bold text (assuming **text** or *text* format)
                    paragraph = paragraph.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    paragraph = paragraph.replace(/\*(.*?)\*/g, '<em>$1</em>');
                    
                    // Convert single line breaks to <br> within paragraphs
                    paragraph = paragraph.replace(/\n/g, '<br>');
                    
                    return '<p>' + paragraph + '</p>';
                }
                return '';
            })
            .join('');
        
        // Handle headings (assuming # Heading format)
        formatted = formatted.replace(/^<p># (.*?)<\/p>$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^<p>## (.*?)<\/p>$/gm, '<h4>$1</h4>');
        
        // Handle lists (assuming - item format)
        formatted = formatted.replace(/<p>- (.*?)<\/p>/g, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
        
        return formatted;
    },
    
    currentExplanation: null,
    currentTopicId: null,
    pageStartTs: null
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    textExplanationModule.init();
});
