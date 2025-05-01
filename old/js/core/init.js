
import $ from 'jquery';
import { apiRequest } from './api.js';
import * as auth from './auth.js';
import * as uiCommon from '../ui/common.js';
import * as uiNavbar from '../ui/navbar.js';
import * as uiPosts from '../ui/posts.js';
import * as router from '../router.js';

function loadFooterData() {
    Promise.allSettled([apiRequest('GET', '/posts/recent/?count=5', null, false), apiRequest('GET', '/tags/popular/', null, false), apiRequest('GET', '/posts/stats/', null, false)])
    .then(results => {
        const recentPostsData = results[0].status === 'fulfilled' ? results[0].value : null; const popularTagsData = results[1].status === 'fulfilled' ? results[1].value : null; const stats = results[2].status === 'fulfilled' ? results[2].value : null;
        const recentPosts = recentPostsData?.results || recentPostsData || []; const popularTags = popularTagsData?.results || popularTagsData || [];
        if (uiPosts?.renderFooter) { uiPosts.renderFooter(recentPosts, popularTags, stats); }
    });
}

export function initialize() {
    auth.checkAuthStatus();
    const initPromise = $.Deferred();
    if (uiNavbar?.updateNavbar) { uiNavbar.updateNavbar(); }

    if (auth.getCurrentUser().token && !auth.getCurrentUser().role) {
         auth.fetchUserProfile().done(() => { if (uiNavbar?.updateNavbar) { uiNavbar.updateNavbar(); } initPromise.resolve(); }).fail(() => { auth.handleLogout(); initPromise.reject(); });
    } else { initPromise.resolve(); }

    initPromise.done(function() {
        if (router?.handleHashChange) { router.handleHashChange(); $(window).on('hashchange', router.handleHashChange); }
        loadFooterData();
        $(document).off('click.skipLink').on('click.skipLink', 'a[href="#main-content"]', function(e) { e.preventDefault(); const target = $('#main-content'); if (target.length) { target.attr('tabindex', -1).focus().one('blur focusout', () => target.removeAttr('tabindex')); } });
        $(document).off('click.logoutLink').on('click.logoutLink', '#logout-link', e => { e.preventDefault(); auth.handleLogout(); });
    }).fail(() => {});
}
