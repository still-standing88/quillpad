
import $ from 'jquery';
import { apiRequest } from './api.js';
import { showAlert } from '../ui/common.js';
import { updateNavbar } from '../ui/navbar.js';
import { navigateTo } from '../router.js';

let currentUser = {
    token: localStorage.getItem('authToken'),
    username: localStorage.getItem('authUsername'),
    userId: localStorage.getItem('authUserId'),
    role: localStorage.getItem('authUserRole')
};

export function getCurrentUser() { return currentUser; }
export function checkAuthStatus() { currentUser.token = localStorage.getItem('authToken'); currentUser.username = localStorage.getItem('authUsername'); currentUser.userId = localStorage.getItem('authUserId'); currentUser.role = localStorage.getItem('authUserRole'); return !!currentUser.token; }

export function fetchUserProfile() {
    const deferred = $.Deferred();
    if (!currentUser.token) { return deferred.reject().promise(); }
    apiRequest('GET', '/profile/')
        .done(function(user) { currentUser.role = user.role; currentUser.username = user.username; currentUser.userId = user.id; localStorage.setItem('authUserRole', user.role); localStorage.setItem('authUsername', user.username); localStorage.setItem('authUserId', user.id); updateNavbar(); deferred.resolve(user); })
        .fail(function() { deferred.reject(); });
    return deferred.promise();
}

export function handleLogin(event) {
    event.preventDefault();
    const username = $('#login-username').val(); const password = $('#login-password').val(); const $button = $(event.target).find('button[type="submit"]'); const originalButtonText = $button.html();
    $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Logging in...');
    apiRequest('POST', '/login/', { username, password }, false)
        .done(function(data) { currentUser.token = data.token; currentUser.username = data.username; currentUser.userId = data.user_id; localStorage.setItem('authToken', data.token); localStorage.setItem('authUsername', data.username); localStorage.setItem('authUserId', data.user_id); fetchUserProfile().always(function(){ updateNavbar(); showAlert('Login successful!', 'success'); navigateTo('#/'); }); })
        .fail(function() {})
        .always(function(){ $button.prop('disabled', false).html(originalButtonText); });
}

export function handleRegister(event) {
    event.preventDefault();
    const username = $('#register-username').val(); const email = $('#register-email').val(); const password = $('#register-password').val(); const $button = $(event.target).find('button[type="submit"]'); const originalButtonText = $button.html();
    $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Registering...');
    apiRequest('POST', '/register/', { username, email, password }, false)
        .done(function(data) { showAlert('Registration successful! Please log in.', 'success'); navigateTo('#login'); })
        .fail(function() {})
        .always(function(){ $button.prop('disabled', false).html(originalButtonText); });
}

export function handleLogout() {
    apiRequest('POST', '/auth/token/logout/').always(function() { currentUser.token = null; currentUser.username = null; currentUser.userId = null; currentUser.role = null; localStorage.clear(); updateNavbar(); showAlert('Logged out.', 'info'); navigateTo('#login'); });
}

export function canEditOrDelete(item) { if (!currentUser.token || !currentUser.role) return false; const isAdminOrEditor = ['admin', 'editor'].includes(currentUser.role); let isAuthor = false; const currentUserIdInt = parseInt(currentUser.userId); if (item?.author) { if (typeof item.author === 'string') { isAuthor = item.author === currentUser.username; } else if (typeof item.author === 'number') { isAuthor = item.author === currentUserIdInt; } else if (item.author?.id) { isAuthor = item.author.id === currentUserIdInt; } else if (item.author?.username) { isAuthor = item.author.username === currentUser.username; } } else if (item?.id && item?.username) { isAuthor = item.id === currentUserIdInt; } return isAuthor || isAdminOrEditor; }
export function isAdmin() { return currentUser.role === 'admin'; }
export function canCreatePost() { return ['admin', 'editor', 'author'].includes(currentUser.role); }
