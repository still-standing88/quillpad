
import $ from 'jquery';
import { getCurrentUser, canCreatePost, isAdmin } from '../core/auth.js';

const navMenu = $('#nav-menu');

export function updateNavbar() {
    if (!navMenu.length) { return; }
    navMenu.empty();
    const user = getCurrentUser();
    const loggedIn = !!user.token;
    navMenu.append(`<li class="nav-item"><a class="nav-link" href="#/">Home</a></li>`);
    if (loggedIn) {
        navMenu.append(`<li class="nav-item"><a class="nav-link" href="#my-posts">My Posts</a></li> ${canCreatePost() ? '<li class="nav-item"><a class="nav-link" href="#create-post">Create Post</a></li>' : ''} <li class="nav-item"><a class="nav-link" href="#saved-posts">Saved</a></li>`);
        if (isAdmin()) { navMenu.append(`<li class="nav-item dropdown"><a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">Admin</a><ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end"><li><a class="dropdown-item" href="#admin/categories">Categories</a></li><li><a class="dropdown-item" href="#admin/users">Users</a></li><li><a class="dropdown-item" href="#admin/tags">Tags</a></li><li><hr class="dropdown-divider"></li><li><a class="dropdown-item" href="/admin/" target="_blank">Django Admin</a></li></ul></li>`); }
        navMenu.append(`<li class="nav-item dropdown"><a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown"><i class="bi bi-person-circle me-1"></i> ${user.username || 'Account'}</a><ul class="dropdown-menu dropdown-menu-end dropdown-menu-dark"><li><a class="dropdown-item" href="#profile">Profile</a></li><li><hr class="dropdown-divider"></li><li><a class="dropdown-item" href="#logout" id="logout-link">Logout</a></li></ul></li>`);
    } else { navMenu.append(`<li class="nav-item"><a class="nav-link" href="#login">Login</a></li> <li class="nav-item"><a class="nav-link" href="#register">Register</a></li>`); }
}
