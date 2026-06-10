// Global notification display
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;

    notification.textContent = message;
    notification.className = `notification show ${type}`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Logout handler
function logout() {
    if (!confirm('Are you sure you want to logout?')) return;

    fetch('/auth/logout', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/auth/';
            }, 500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Logout failed', 'error');
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Debounce function for search
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Initialize tooltips
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const tooltip = event.target.getAttribute('data-tooltip');
    console.log(tooltip);
}

function hideTooltip(event) {
    // Tooltip hidden
}

// Make amount input accept only numbers
document.addEventListener('DOMContentLoaded', function() {
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Initialize tooltips
    initializeTooltips();

    // Handle responsive sidebar
    const toggleSidebar = document.querySelector('.toggle-sidebar');
    if (toggleSidebar) {
        toggleSidebar.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('active');
        });
    }
});

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    return response.json();
}

// Get user categories
async function getUserCategories(type = '') {
    let url = '/api/categories';
    if (type) {
        url += `?type=${type}`;
    }
    return apiRequest(url);
}

// Create new category
async function createCategory(name, type, color) {
    return apiRequest('/api/categories', {
        method: 'POST',
        body: JSON.stringify({
            category_name: name,
            category_type: type,
            color: color
        })
    });
}

// Update category
async function updateCategory(categoryId, updates) {
    return apiRequest(`/api/categories/${categoryId}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
    });
}

// Delete category
async function deleteCategory(categoryId) {
    return apiRequest(`/api/categories/${categoryId}`, {
        method: 'DELETE'
    });
}

// Get dashboard stats
async function getDashboardStats() {
    return apiRequest('/api/dashboard/stats');
}

// Get recent transactions
async function getRecentTransactions(limit = 10) {
    return apiRequest(`/api/dashboard/recent?limit=${limit}`);
}

// Quick add transaction
async function quickAddTransaction(amount, categoryId, description = '') {
    return apiRequest('/api/transactions/quick', {
        method: 'POST',
        body: JSON.stringify({
            amount: amount,
            category_id: categoryId,
            description: description
        })
    });
}

// Search transactions (placeholder for future implementation)
function searchTransactions(query) {
    console.log('Searching for:', query);
    // To be implemented
}

// Print report (placeholder for future implementation)
function printReport() {
    window.print();
}

// Handle form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// Export helper
function downloadCSV(csvContent, filename) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Theme management (for future light/dark mode)
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Initialize app on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initializeTheme();
    });
} else {
    initializeTheme();
}

// Service Worker registration (for offline support - future enhancement)
if ('serviceWorker' in navigator) {
    // navigator.serviceWorker.register('/static/js/sw.js');
}

// Keep session alive (ping server every 5 minutes)
function keepSessionAlive() {
    fetch('/api/health')
        .catch(error => console.log('Session check failed:', error));
}

setInterval(keepSessionAlive, 5 * 60 * 1000);
