/**
 * MarkIt Mistral Web Interface
 * JavaScript for UI interactions and file handling
 */

class MarkItWebUI {
    constructor() {
        this.selectedFile = null;
        this.apiKey = null;
        this.isProcessing = false;
        this.extractedImages = [];
        this.markdownContent = '';
        
        this.initializeElements();
        this.bindEvents();
        this.loadStoredApiKey();
    }

    initializeElements() {
        // File upload elements
        this.dropZone = document.getElementById('drop-zone');
        this.fileInput = document.getElementById('file-input');
        this.fileInfo = document.getElementById('file-info');
        this.fileName = document.getElementById('file-name');
        this.fileSize = document.getElementById('file-size');
        this.removeFileBtn = document.getElementById('remove-file');

        // Configuration elements
        this.apiKeyInput = document.getElementById('api-key');
        this.includeImagesCheckbox = document.getElementById('include-images');
        this.base64ImagesCheckbox = document.getElementById('base64-images');

        // Control elements
        this.processBtn = document.getElementById('process-btn');

        // Progress elements
        this.progressSection = document.getElementById('progress-section');
        this.progressText = document.getElementById('progress-text');
        this.progressPercent = document.getElementById('progress-percent');
        this.progressBar = document.getElementById('progress-bar');

        // Results elements
        this.resultsSection = document.getElementById('results-section');
        this.markdownPreview = document.getElementById('markdown-preview');
        this.imagesList = document.getElementById('images-list');
        this.imagesContainer = document.getElementById('images-container');
        this.downloadMarkdownBtn = document.getElementById('download-markdown');
        this.downloadImagesBtn = document.getElementById('download-images');
        this.downloadAllBtn = document.getElementById('download-all');

        // Error elements
        this.errorSection = document.getElementById('error-section');
        this.errorMessage = document.getElementById('error-message');
    }

    bindEvents() {
        // File upload events
        this.dropZone.addEventListener('click', () => this.fileInput.click());
        this.dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        this.dropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.dropZone.addEventListener('drop', this.handleDrop.bind(this));
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        this.removeFileBtn.addEventListener('click', this.removeFile.bind(this));

        // Configuration events
        this.apiKeyInput.addEventListener('input', this.handleApiKeyChange.bind(this));
        this.includeImagesCheckbox.addEventListener('change', this.updateProcessButton.bind(this));

        // Control events
        this.processBtn.addEventListener('click', this.processFile.bind(this));

        // Download events
        this.downloadMarkdownBtn.addEventListener('click', () => this.downloadMarkdown());
        this.downloadImagesBtn.addEventListener('click', () => this.downloadImages());
        this.downloadAllBtn.addEventListener('click', () => this.downloadAll());
    }

    loadStoredApiKey() {
        const storedKey = localStorage.getItem('mistral-api-key');
        if (storedKey) {
            this.apiKeyInput.value = storedKey;
            this.apiKey = storedKey;
            this.updateProcessButton();
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        this.dropZone.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.dropZone.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.selectFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.selectFile(files[0]);
        }
    }

    selectFile(file) {
        // Validate file type
        const allowedTypes = [
            'application/pdf',
            'image/png',
            'image/jpeg',
            'image/jpg',
            'image/tiff',
            'image/tif'
        ];

        if (!allowedTypes.includes(file.type)) {
            this.showError('Unsupported file type. Please select a PDF, PNG, JPEG, or TIFF file.');
            return;
        }

        // Validate file size (50MB limit)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('File too large. Maximum size is 50MB.');
            return;
        }

        this.selectedFile = file;
        this.showFileInfo();
        this.hideError();
        this.updateProcessButton();
    }

    removeFile() {
        this.selectedFile = null;
        this.fileInfo.classList.add('hidden');
        this.fileInput.value = '';
        this.updateProcessButton();
        this.hideResults();
    }

    showFileInfo() {
        this.fileName.textContent = this.selectedFile.name;
        this.fileSize.textContent = this.formatFileSize(this.selectedFile.size);
        this.fileInfo.classList.remove('hidden');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    handleApiKeyChange(e) {
        this.apiKey = e.target.value.trim();
        if (this.apiKey) {
            localStorage.setItem('mistral-api-key', this.apiKey);
        } else {
            localStorage.removeItem('mistral-api-key');
        }
        this.updateProcessButton();
    }

    updateProcessButton() {
        const canProcess = this.selectedFile && this.apiKey && !this.isProcessing;
        this.processBtn.disabled = !canProcess;
    }

    async processFile() {
        if (!this.selectedFile || !this.apiKey || this.isProcessing) {
            return;
        }

        this.isProcessing = true;
        this.updateProcessButton();
        this.hideError();
        this.hideResults();
        this.showProgress();

        try {
            // Update progress
            this.updateProgress('Reading file...', 10);

            // Convert file to base64
            const fileBase64 = await this.fileToBase64(this.selectedFile);
            this.updateProgress('Preparing API request...', 20);

            // Get processing options
            const includeImages = this.includeImagesCheckbox.checked;
            const base64Images = this.base64ImagesCheckbox.checked;

            // Call PyScript function to process the file
            this.updateProgress('Processing with Mistral AI...', 30);
            
            // Use PyScript to process the file
            const result = await this.callPyScriptProcessor({
                file_data: fileBase64,
                file_name: this.selectedFile.name,
                file_type: this.selectedFile.type,
                api_key: this.apiKey,
                include_images: includeImages,
                base64_images: base64Images
            });

            this.updateProgress('Processing results...', 90);

            if (result.success) {
                this.markdownContent = result.markdown;
                this.extractedImages = result.images || [];
                this.showResults();
                this.updateProgress('Complete!', 100);
                setTimeout(() => this.hideProgress(), 2000);
            } else {
                throw new Error(result.error || 'Processing failed');
            }

        } catch (error) {
            console.error('Processing error:', error);
            this.showError(error.message || 'An error occurred while processing the file.');
            this.hideProgress();
        } finally {
            this.isProcessing = false;
            this.updateProcessButton();
        }
    }

    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async callPyScriptProcessor(data) {
        // This will be called from PyScript
        return new Promise((resolve) => {
            window.pyScriptProcessFile = resolve;
            window.pyScriptData = data;
            
            // Trigger PyScript processing
            const event = new CustomEvent('processFile', { detail: data });
            document.dispatchEvent(event);
        });
    }

    showProgress() {
        this.progressSection.classList.remove('hidden');
    }

    hideProgress() {
        this.progressSection.classList.add('hidden');
    }

    updateProgress(text, percent) {
        this.progressText.textContent = text;
        this.progressPercent.textContent = `${percent}%`;
        this.progressBar.style.width = `${percent}%`;
    }

    showResults() {
        this.markdownPreview.textContent = this.markdownContent;
        
        if (this.extractedImages.length > 0) {
            this.populateImages();
            this.imagesList.classList.remove('hidden');
            this.downloadImagesBtn.classList.remove('hidden');
        } else {
            this.imagesList.classList.add('hidden');
            this.downloadImagesBtn.classList.add('hidden');
        }
        
        this.resultsSection.classList.remove('hidden');
    }

    hideResults() {
        this.resultsSection.classList.add('hidden');
    }

    populateImages() {
        this.imagesContainer.innerHTML = '';
        
        this.extractedImages.forEach((image, index) => {
            const imageDiv = document.createElement('div');
            imageDiv.className = 'border rounded-lg p-2 bg-gray-50';
            
            const img = document.createElement('img');
            img.src = image.data;
            img.alt = image.name;
            img.className = 'w-full h-24 object-cover rounded mb-2';
            
            const name = document.createElement('p');
            name.textContent = image.name;
            name.className = 'text-xs text-gray-600 truncate';
            
            imageDiv.appendChild(img);
            imageDiv.appendChild(name);
            this.imagesContainer.appendChild(imageDiv);
        });
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorSection.classList.remove('hidden');
    }

    hideError() {
        this.errorSection.classList.add('hidden');
    }

    downloadMarkdown() {
        if (!this.markdownContent) return;
        
        const blob = new Blob([this.markdownContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = this.getMarkdownFileName();
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    downloadImages() {
        if (this.extractedImages.length === 0) return;
        
        // Create a zip file with all images
        this.createImageZip();
    }

    downloadAll() {
        if (!this.markdownContent) return;
        
        // Create a zip file with markdown and images
        this.createCompleteZip();
    }

    async createImageZip() {
        // For now, download images individually
        // In a full implementation, you'd use a zip library like JSZip
        this.extractedImages.forEach((image, index) => {
            const link = document.createElement('a');
            link.href = image.data;
            link.download = image.name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    async createCompleteZip() {
        // For now, download markdown and images separately
        // In a full implementation, you'd create a proper zip file
        this.downloadMarkdown();
        if (this.extractedImages.length > 0) {
            setTimeout(() => this.downloadImages(), 500);
        }
    }

    getMarkdownFileName() {
        if (!this.selectedFile) return 'output.md';
        
        const baseName = this.selectedFile.name.replace(/\.[^/.]+$/, '');
        return `${baseName}.md`;
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.markitUI = new MarkItWebUI();
});

// Utility functions for PyScript integration
window.updateProgress = (text, percent) => {
    if (window.markitUI) {
        window.markitUI.updateProgress(text, percent);
    }
};

window.showError = (message) => {
    if (window.markitUI) {
        window.markitUI.showError(message);
    }
}; 