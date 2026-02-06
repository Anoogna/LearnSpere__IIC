/**
 * Authentication Handler
 * Manages user authentication state on the client side
 */

const authManager = {
    init: function() {
        console.log('Auth manager initialized');
        this.checkAuthStatus();
        this.setupAuthUI();
    },
    
    checkAuthStatus: async function() {
        try {
            const token = localStorage.getItem('auth_token');
            const headers = token ? {'Authorization': `Bearer ${token}`} : {};
            
            const response = await fetch('/api/check-auth', { headers });
            const data = await response.json();
            
            if (data.authenticated) {
                this.setAuthenticated(data.username);
            } else {
                this.setUnauthenticated();
            }
        } catch (error) {
            console.error('Auth check error:', error);
            this.setUnauthenticated();
        }
    },
    
    setAuthenticated: function(username) {
        console.log('User authenticated:', username);
        
        // Update UI
        document.getElementById('userDisplay').style.display = 'inline';
        document.getElementById('currentUser').textContent = `Welcome, ${username}!`;
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('registerBtn').style.display = 'none';
        document.getElementById('logoutBtn').style.display = 'inline-block';
        
        // Store username
        sessionStorage.setItem('username', username);
    },
    
    setUnauthenticated: function() {
        console.log('User not authenticated');
        
        // Update UI
        document.getElementById('userDisplay').style.display = 'none';
        document.getElementById('loginBtn').style.display = 'inline-block';
        document.getElementById('registerBtn').style.display = 'inline-block';
        document.getElementById('logoutBtn').style.display = 'none';
        
        // Clear stored username
        sessionStorage.removeItem('username');
        localStorage.removeItem('auth_token');
    },
    
    setupAuthUI: function() {
        // Setup logout form to prevent default and clear data
        const logoutForm = document.getElementById('logoutForm');
        if (logoutForm) {
            logoutForm.addEventListener('submit', (e) => {
                localStorage.removeItem('auth_token');
                sessionStorage.removeItem('username');
            });
        }
    },
    
    logout: function() {
        localStorage.removeItem('auth_token');
        sessionStorage.removeItem('username');
        this.setUnauthenticated();
        window.location.href = '/';
    },
    
    isAuthenticated: function() {
        const token = localStorage.getItem('auth_token');
        const user = sessionStorage.getItem('username');
        return !!(token || user);
    },
    
    getUsername: function() {
        return sessionStorage.getItem('username');
    },
    
    getAuthToken: function() {
        return localStorage.getItem('auth_token');
    }
};

// Initialize auth manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => authManager.init());
} else {
    authManager.init();
}
