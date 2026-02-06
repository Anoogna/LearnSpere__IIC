// Code Generation Module
// Handles Python code generation for ML algorithms

const codeGenerationModule = {
    init: function() {
        console.log('Code generation module initialized');
        this.attachEventListeners();
    },
    
    attachEventListeners: function() {
        const form = document.getElementById('codeGenerationForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        const copyCodeBtn = document.getElementById('copyCodeBtn');
        if (copyCodeBtn) {
            copyCodeBtn.addEventListener('click', () => this.copyCode());
        }
        
        const downloadCodeBtn = document.getElementById('downloadCodeBtn');
        if (downloadCodeBtn) {
            downloadCodeBtn.addEventListener('click', () => this.downloadCode());
        }
        
        const executionGuideBtn = document.getElementById('executionGuideBtn');
        if (executionGuideBtn) {
            executionGuideBtn.addEventListener('click', () => this.showExecutionGuide());
        }
        
        const colonabBtn = document.getElementById('colonabBtn');
        if (colonabBtn) {
            colonabBtn.addEventListener('click', () => this.openInColab());
        }
    },
    
    handleFormSubmit: async function(e) {
        e.preventDefault();
        
        const algorithm = document.getElementById('algorithm').value;
        const complexity = document.getElementById('codeComplexity').value;
        
        if (!algorithm.trim()) {
            alert('Please enter an algorithm or concept');
            return;
        }
        
        await this.generateCode(algorithm, complexity);
    },
    
    generateCode: async function(algorithm, complexity) {
        const generateBtn = document.querySelector('#codeGenerationForm button');
        const outputSection = document.getElementById('codeOutputSection');
        const loadingIndicator = document.getElementById('codeLoadingIndicator');
        const codeContent = document.getElementById('codeContent');
        const codeTitle = document.getElementById('codeTitle');
        const dependenciesList = document.getElementById('dependenciesList');
        
        generateBtn.disabled = true;
        outputSection.style.display = 'block';
        loadingIndicator.style.display = 'block';
        
        try {
            const response = await fetch('/api/generate-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    algorithm: algorithm,
                    complexity: complexity
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                loadingIndicator.style.display = 'none';
                
                codeTitle.textContent = `${data.algorithm} - ${data.complexity}`;
                codeContent.textContent = data.code;
                this.currentCode = data.code;
                this.currentDependencies = data.dependencies;
                
                // Display dependencies
                dependenciesList.innerHTML = '';
                if (data.dependencies && data.dependencies.length > 0) {
                    data.dependencies.forEach(dep => {
                        const badge = document.createElement('span');
                        badge.className = 'dependency-badge';
                        badge.textContent = dep;
                        dependenciesList.appendChild(badge);
                    });
                } else {
                    dependenciesList.textContent = 'Only standard library';
                }
                
                // Show validity status
                if (!data.is_valid) {
                    const errorMsg = document.createElement('div');
                    errorMsg.style.background = '#f8d7da';
                    errorMsg.style.color = '#721c24';
                    errorMsg.style.padding = '1rem';
                    errorMsg.style.marginBottom = '1rem';
                    errorMsg.style.borderRadius = '5px';
                    errorMsg.textContent = 'Warning: ' + data.error;
                    codeContent.parentElement.insertBefore(errorMsg, codeContent);
                }
            } else {
                throw new Error(data.error || 'Failed to generate code');
            }
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            codeContent.textContent = 'Error: ' + error.message;
        } finally {
            generateBtn.disabled = false;
        }
    },
    
    copyCode: function() {
        if (!this.currentCode) {
            alert('No code to copy');
            return;
        }
        
        navigator.clipboard.writeText(this.currentCode).then(() => {
            alert('Code copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard');
        });
    },
    
    downloadCode: function() {
        if (!this.currentCode) {
            alert('No code to download');
            return;
        }
        
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(this.currentCode));
        element.setAttribute('download', 'ml_algorithm.py');
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    },
    
    showExecutionGuide: async function() {
        if (!this.currentCode) {
            alert('No code to get guide for');
            return;
        }
        
        const guideSection = document.getElementById('executionGuideSection');
        const guideContent = document.getElementById('guideContent');
        
        try {
            const response = await fetch('/api/code-execution-guide', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: this.currentCode
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                guideContent.textContent = data.guide;
                guideSection.style.display = 'block';
                guideSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error: ' + (data.error || 'Failed to generate guide'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        }
    },
    
    openInColab: async function() {
        if (!this.currentCode) {
            alert('No code to open');
            return;
        }
        
        try {
            const response = await fetch('/api/code-execution-guide', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: this.currentCode
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const colonabUrl = 'https://colab.research.google.com/notebook';
                alert('Colab code:\n\n' + data.colab_code + '\n\nOpen Google Colab and paste this code.');
                // In a real implementation, you would create a Colab notebook
                window.open(colonabUrl, '_blank');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        }
    },
    
    currentCode: null,
    currentDependencies: []
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    codeGenerationModule.init();
});
