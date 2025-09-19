/*
RapidAPI Utilities JavaScript Module
Enhanced client-side functionality for RapidAPI components

This module provides client-side utilities for enhanced user experience including:
- Real-time validation feedback
- Progress tracking enhancements
- UI state management
- Clipboard operations
- Local storage management
- Performance monitoring

JavaScript Architecture:
- Modular design with clear separation of concerns
- Event-driven programming for responsive UI
- Error handling and fallback mechanisms
- Performance optimization techniques
- Cross-browser compatibility
- Accessibility enhancements
*/

// ============================================================================
// CORE UTILITY FUNCTIONS
// ============================================================================

/**
 * RapidAPI Utilities Namespace
 * Central namespace for all RapidAPI-related JavaScript functionality
 */
const RapidAPIUtils = {
    
    // Configuration and constants
    config: {
        API_KEY_LENGTH: 50,
        API_KEY_PATTERN: /^[a-zA-Z0-9]+msh[a-zA-Z0-9]+jsn[a-zA-Z0-9]+$/,
        REQUIRED_MARKERS: ['msh', 'jsn'],
        VALIDATION_DEBOUNCE_MS: 500,
        PROGRESS_UPDATE_INTERVAL_MS: 100,
        LOCAL_STORAGE_PREFIX: 'rapidapi_'
    },
    
    // ============================================================================
    // API KEY VALIDATION UTILITIES
    // ============================================================================
    
    /**
     * Real-time API key format validation
     * Provides immediate feedback without server calls
     * 
     * @param {string} apiKey - API key to validate
     * @returns {Object} Validation result with status and message
     */
    validateApiKeyFormat: function(apiKey) {
        console.log(`[RapidAPIUtils] Validating API key format - Length: ${apiKey.length}`);
        
        // Input validation
        if (!apiKey || typeof apiKey !== 'string') {
            return {
                valid: false,
                message: 'API key must be a non-empty string',
                details: 'Please enter a valid RapidAPI key'
            };
        }
        
        // Remove whitespace
        apiKey = apiKey.trim();
        
        // Length validation
        if (apiKey.length !== this.config.API_KEY_LENGTH) {
            return {
                valid: false,
                message: `Invalid length: expected ${this.config.API_KEY_LENGTH}, got ${apiKey.length}`,
                details: 'RapidAPI keys are exactly 50 characters long'
            };
        }
        
        // Character validation
        const allowedChars = /^[a-zA-Z0-9]+$/;
        if (!allowedChars.test(apiKey)) {
            return {
                valid: false,
                message: 'Contains invalid characters',
                details: 'API keys should only contain letters and numbers'
            };
        }
        
        // Required markers validation
        const missingMarkers = this.config.REQUIRED_MARKERS.filter(
            marker => !apiKey.toLowerCase().includes(marker)
        );
        
        if (missingMarkers.length > 0) {
            return {
                valid: false,
                message: `Missing required markers: ${missingMarkers.join(', ')}`,
                details: 'Valid RapidAPI keys contain both "msh" and "jsn" markers'
            };
        }
        
        // Pattern validation
        if (!this.config.API_KEY_PATTERN.test(apiKey)) {
            return {
                valid: false,
                message: 'Invalid API key pattern',
                details: 'Expected format: [alphanumeric]msh[alphanumeric]jsn[alphanumeric]'
            };
        }
        
        console.log('[RapidAPIUtils] API key format validation successful');
        return {
            valid: true,
            message: 'API key format is valid',
            details: 'All format requirements met'
        };
    },
    
    /**
     * Debounced validation for real-time input feedback
     * Prevents excessive validation calls during typing
     * 
     * @param {string} apiKey - API key to validate
     * @param {Function} callback - Callback function for validation result
     */
    debouncedValidation: function(apiKey, callback) {
        // Clear existing timeout
        if (this._validationTimeout) {
            clearTimeout(this._validationTimeout);
        }
        
        // Set new timeout for debounced validation
        this._validationTimeout = setTimeout(() => {
            const result = this.validateApiKeyFormat(apiKey);
            callback(result);
        }, this.config.VALIDATION_DEBOUNCE_MS);
    },
    
    // ============================================================================
    // CLIPBOARD UTILITIES
    // ============================================================================
    
    /**
     * Copy text to clipboard with fallback support
     * Provides cross-browser clipboard functionality
     * 
     * @param {string} text - Text to copy to clipboard
     * @returns {Promise<boolean>} Success status
     */
    copyToClipboard: async function(text) {
        console.log(`[RapidAPIUtils] Copying text to clipboard - Length: ${text.length}`);
        
        try {
            // Modern clipboard API (preferred)
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
                console.log('[RapidAPIUtils] Text copied using modern clipboard API');
                return true;
            }
            
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (successful) {
                console.log('[RapidAPIUtils] Text copied using fallback method');
                return true;
            }
            
            throw new Error('Copy command failed');
            
        } catch (error) {
            console.error('[RapidAPIUtils] Failed to copy text:', error);
            return false;
        }
    },
    
    /**
     * Copy download link with user feedback
     * Specialized function for copying download links
     * 
     * @param {string} downloadLink - Download link to copy
     * @param {string} fileName - File name for feedback message
     */
    copyDownloadLink: async function(downloadLink, fileName = 'file') {
        console.log(`[RapidAPIUtils] Copying download link for: ${fileName}`);
        
        const success = await this.copyToClipboard(downloadLink);
        
        if (success) {
            this.showNotification(`✅ Download link copied for ${fileName}`, 'success');
        } else {
            this.showNotification(`❌ Failed to copy download link`, 'error');
        }
    },
    
    // ============================================================================
    // LOCAL STORAGE UTILITIES
    // ============================================================================
    
    /**
     * Save data to local storage with prefix
     * Provides persistent storage for user preferences
     * 
     * @param {string} key - Storage key
     * @param {any} data - Data to store
     */
    saveToLocalStorage: function(key, data) {
        try {
            const prefixedKey = this.config.LOCAL_STORAGE_PREFIX + key;
            const serializedData = JSON.stringify(data);
            localStorage.setItem(prefixedKey, serializedData);
            console.log(`[RapidAPIUtils] Data saved to local storage: ${prefixedKey}`);
        } catch (error) {
            console.error('[RapidAPIUtils] Failed to save to local storage:', error);
        }
    },
    
    /**
     * Load data from local storage
     * Retrieves persistent user preferences
     * 
     * @param {string} key - Storage key
     * @param {any} defaultValue - Default value if key not found
     * @returns {any} Stored data or default value
     */
    loadFromLocalStorage: function(key, defaultValue = null) {
        try {
            const prefixedKey = this.config.LOCAL_STORAGE_PREFIX + key;
            const serializedData = localStorage.getItem(prefixedKey);
            
            if (serializedData === null) {
                return defaultValue;
            }
            
            const data = JSON.parse(serializedData);
            console.log(`[RapidAPIUtils] Data loaded from local storage: ${prefixedKey}`);
            return data;
            
        } catch (error) {
            console.error('[RapidAPIUtils] Failed to load from local storage:', error);
            return defaultValue;
        }
    },
    
    /**
     * Clear specific item from local storage
     * 
     * @param {string} key - Storage key to clear
     */
    clearFromLocalStorage: function(key) {
        try {
            const prefixedKey = this.config.LOCAL_STORAGE_PREFIX + key;
            localStorage.removeItem(prefixedKey);
            console.log(`[RapidAPIUtils] Cleared from local storage: ${prefixedKey}`);
        } catch (error) {
            console.error('[RapidAPIUtils] Failed to clear from local storage:', error);
        }
    },
    
    // ============================================================================
    // UI ENHANCEMENT UTILITIES
    // ============================================================================
    
    /**
     * Show temporary notification to user
     * Provides non-intrusive user feedback
     * 
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {number} duration - Display duration in milliseconds
     */
    showNotification: function(message, type = 'info', duration = 3000) {
        console.log(`[RapidAPIUtils] Showing notification: ${type} - ${message}`);
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `rapidapi-notification rapidapi-notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            zIndex: '9999',
            fontWeight: '500',
            maxWidth: '400px',
            wordWrap: 'break-word'
        });
        
        // Set colors based on type
        const colors = {
            success: { bg: '#2ecc71', color: 'white' },
            error: { bg: '#e74c3c', color: 'white' },
            warning: { bg: '#f39c12', color: 'white' },
            info: { bg: '#3498db', color: 'white' }
        };
        
        const colorScheme = colors[type] || colors.info;
        notification.style.backgroundColor = colorScheme.bg;
        notification.style.color = colorScheme.color;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
    },
    
    /**
     * Enhance form inputs with real-time validation
     * Adds visual feedback for form validation
     * 
     * @param {string} inputId - Input element ID
     * @param {Function} validator - Validation function
     */
    enhanceInput: function(inputId, validator) {
        const input = document.getElementById(inputId);
        if (!input) {
            console.warn(`[RapidAPIUtils] Input element not found: ${inputId}`);
            return;
        }
        
        console.log(`[RapidAPIUtils] Enhancing input: ${inputId}`);
        
        // Add validation on input change
        input.addEventListener('input', (event) => {
            const value = event.target.value;
            
            // Debounced validation
            this.debouncedValidation(value, (result) => {
                // Update input styling based on validation
                input.classList.remove('rapidapi-key-valid', 'rapidapi-key-invalid');
                
                if (value.trim()) {
                    if (result.valid) {
                        input.classList.add('rapidapi-key-valid');
                    } else {
                        input.classList.add('rapidapi-key-invalid');
                    }
                }
            });
        });
    },
    
    // ============================================================================
    // PROGRESS TRACKING UTILITIES
    // ============================================================================
    
    /**
     * Enhanced progress tracking with smooth animations
     * Provides smooth progress bar updates
     * 
     * @param {string} progressBarId - Progress bar element ID
     * @param {number} percentage - Progress percentage (0-100)
     * @param {boolean} animate - Whether to animate the progress
     */
    updateProgress: function(progressBarId, percentage, animate = true) {
        const progressBar = document.getElementById(progressBarId);
        if (!progressBar) {
            console.warn(`[RapidAPIUtils] Progress bar not found: ${progressBarId}`);
            return;
        }
        
        console.log(`[RapidAPIUtils] Updating progress: ${percentage}%`);
        
        if (animate) {
            // Smooth animation
            progressBar.style.transition = 'width 0.3s ease';
        } else {
            progressBar.style.transition = 'none';
        }
        
        progressBar.style.width = `${Math.min(100, Math.max(0, percentage))}%`;
    },
    
    /**
     * Create animated counter for metrics
     * Provides smooth number animations
     * 
     * @param {string} elementId - Target element ID
     * @param {number} targetValue - Target number value
     * @param {number} duration - Animation duration in milliseconds
     */
    animateCounter: function(elementId, targetValue, duration = 1000) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`[RapidAPIUtils] Counter element not found: ${elementId}`);
            return;
        }
        
        console.log(`[RapidAPIUtils] Animating counter to: ${targetValue}`);
        
        const startValue = parseInt(element.textContent) || 0;
        const increment = (targetValue - startValue) / (duration / 16); // 60fps
        let currentValue = startValue;
        
        const timer = setInterval(() => {
            currentValue += increment;
            
            if ((increment > 0 && currentValue >= targetValue) || 
                (increment < 0 && currentValue <= targetValue)) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            
            element.textContent = Math.round(currentValue).toLocaleString();
        }, 16);
    },
    
    // ============================================================================
    // URL AND LINK UTILITIES
    // ============================================================================
    
    /**
     * Validate TeraBox URL format
     * Client-side validation for TeraBox URLs
     * 
     * @param {string} url - URL to validate
     * @returns {Object} Validation result
     */
    validateTeraBoxUrl: function(url) {
        console.log(`[RapidAPIUtils] Validating TeraBox URL: ${url.substring(0, 50)}...`);
        
        if (!url || typeof url !== 'string') {
            return {
                valid: false,
                message: 'URL must be a non-empty string'
            };
        }
        
        // Protocol validation
        if (!url.toLowerCase().startsWith('http://') && !url.toLowerCase().startsWith('https://')) {
            return {
                valid: false,
                message: 'URL must start with http:// or https://'
            };
        }
        
        // Domain validation
        const teraboxDomains = [
            'terabox.com', 'terabox.app', '1024terabox.com', '1024tera.com',
            'terasharelink.com', 'terafileshare.com', 'teraboxapp.com',
            'freeterabox.com', 'nephobox.com'
        ];
        
        const urlLower = url.toLowerCase();
        const isValidDomain = teraboxDomains.some(domain => urlLower.includes(domain));
        
        if (!isValidDomain) {
            return {
                valid: false,
                message: 'URL does not contain a recognized TeraBox domain'
            };
        }
        
        console.log('[RapidAPIUtils] TeraBox URL validation successful');
        return {
            valid: true,
            message: 'Valid TeraBox URL format'
        };
    },
    
    /**
     * Extract short URL (surl) from TeraBox link
     * Extracts the unique identifier from TeraBox URLs
     * 
     * @param {string} url - TeraBox URL
     * @returns {string|null} Extracted surl or null if not found
     */
    extractSurl: function(url) {
        console.log(`[RapidAPIUtils] Extracting surl from URL: ${url.substring(0, 50)}...`);
        
        const patterns = [
            /surl=([a-zA-Z0-9_-]+)/,  // Query parameter format
            /\/s\/([a-zA-Z0-9_-]+)/   // Path format
        ];
        
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) {
                const surl = match[1];
                console.log(`[RapidAPIUtils] Surl extracted: ${surl}`);
                return surl;
            }
        }
        
        console.warn('[RapidAPIUtils] Could not extract surl from URL');
        return null;
    },
    
    // ============================================================================
    // FILE SIZE AND FORMAT UTILITIES
    // ============================================================================
    
    /**
     * Format file size in human-readable format
     * Converts bytes to appropriate units
     * 
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 B';
        
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        const size = bytes / Math.pow(1024, i);
        
        const formatted = `${size.toFixed(1)} ${sizes[i]}`;
        console.log(`[RapidAPIUtils] Formatted file size: ${bytes} bytes -> ${formatted}`);
        
        return formatted;
    },
    
    /**
     * Calculate download speed and ETA
     * Provides real-time download metrics
     * 
     * @param {number} downloaded - Bytes downloaded
     * @param {number} total - Total bytes
     * @param {number} elapsedSeconds - Elapsed time in seconds
     * @returns {Object} Speed and ETA information
     */
    calculateDownloadMetrics: function(downloaded, total, elapsedSeconds) {
        if (elapsedSeconds <= 0 || downloaded <= 0) {
            return {
                speed: 0,
                speedFormatted: '0 B/s',
                eta: 0,
                etaFormatted: 'Calculating...',
                percentage: 0
            };
        }
        
        const speed = downloaded / elapsedSeconds; // bytes per second
        const speedFormatted = this.formatFileSize(speed) + '/s';
        
        const percentage = (downloaded / total) * 100;
        
        let eta = 0;
        let etaFormatted = 'Unknown';
        
        if (speed > 0 && total > downloaded) {
            const remainingBytes = total - downloaded;
            eta = remainingBytes / speed;
            
            const minutes = Math.floor(eta / 60);
            const seconds = Math.floor(eta % 60);
            
            if (minutes > 0) {
                etaFormatted = `${minutes}m ${seconds}s`;
            } else {
                etaFormatted = `${seconds}s`;
            }
        }
        
        return {
            speed,
            speedFormatted,
            eta,
            etaFormatted,
            percentage: Math.min(100, Math.max(0, percentage))
        };
    },
    
    // ============================================================================
    // PERFORMANCE MONITORING
    // ============================================================================
    
    /**
     * Performance timer for operation monitoring
     * Tracks operation performance for optimization
     * 
     * @param {string} operationName - Name of operation to track
     * @returns {Object} Timer object with stop method
     */
    startPerformanceTimer: function(operationName) {
        console.log(`[RapidAPIUtils] Starting performance timer: ${operationName}`);
        
        const startTime = performance.now();
        
        return {
            stop: () => {
                const endTime = performance.now();
                const duration = endTime - startTime;
                console.log(`[RapidAPIUtils] Performance timer completed: ${operationName} - ${duration.toFixed(2)}ms`);
                return duration;
            }
        };
    },
    
    /**
     * Monitor memory usage (if available)
     * Tracks memory consumption for optimization
     * 
     * @returns {Object|null} Memory information or null if not available
     */
    getMemoryInfo: function() {
        if (performance.memory) {
            const memory = performance.memory;
            return {
                used: this.formatFileSize(memory.usedJSHeapSize),
                total: this.formatFileSize(memory.totalJSHeapSize),
                limit: this.formatFileSize(memory.jsHeapSizeLimit)
            };
        }
        return null;
    },
    
    // ============================================================================
    // EVENT HANDLING UTILITIES
    // ============================================================================
    
    /**
     * Add event listener with automatic cleanup
     * Prevents memory leaks from event listeners
     * 
     * @param {string|Element} target - Target element or selector
     * @param {string} event - Event type
     * @param {Function} handler - Event handler function
     * @returns {Function} Cleanup function
     */
    addEventListenerWithCleanup: function(target, event, handler) {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        
        if (!element) {
            console.warn(`[RapidAPIUtils] Event target not found: ${target}`);
            return () => {};
        }
        
        element.addEventListener(event, handler);
        console.log(`[RapidAPIUtils] Event listener added: ${event} on ${target}`);
        
        // Return cleanup function
        return () => {
            element.removeEventListener(event, handler);
            console.log(`[RapidAPIUtils] Event listener removed: ${event} on ${target}`);
        };
    },
    
    /**
     * Throttle function execution
     * Limits function execution frequency
     * 
     * @param {Function} func - Function to throttle
     * @param {number} limit - Throttle limit in milliseconds
     * @returns {Function} Throttled function
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * Debounce function execution
     * Delays function execution until after calls have stopped
     * 
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce: function(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    },
    
    // ============================================================================
    // INITIALIZATION AND SETUP
    // ============================================================================
    
    /**
     * Initialize RapidAPI utilities
     * Sets up global functionality and event listeners
     */
    init: function() {
        console.log('[RapidAPIUtils] Initializing RapidAPI utilities');
        
        // Initialize performance monitoring
        this.performanceStart = performance.now();
        
        // Set up global error handling
        window.addEventListener('error', (event) => {
            console.error('[RapidAPIUtils] Global error caught:', event.error);
        });
        
        // Set up unhandled promise rejection handling
        window.addEventListener('unhandledrejection', (event) => {
            console.error('[RapidAPIUtils] Unhandled promise rejection:', event.reason);
        });
        
        // Log memory info if available
        const memoryInfo = this.getMemoryInfo();
        if (memoryInfo) {
            console.log('[RapidAPIUtils] Memory info:', memoryInfo);
        }
        
        console.log('[RapidAPIUtils] Initialization completed');
    }
};

// ============================================================================
// AUTO-INITIALIZATION
// ============================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        RapidAPIUtils.init();
    });
} else {
    RapidAPIUtils.init();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RapidAPIUtils;
}

// Global assignment for browser usage
window.RapidAPIUtils = RapidAPIUtils;
