(function(window, $, api, auth, uiCommon, uiNavbar, uiPosts, router) {

    function loadFooterData() {
        // console.log("Loading footer data...");
        Promise.allSettled([
            api.request('GET', '/posts/recent/?count=5', null, false),
            api.request('GET', '/tags/popular/', null, false),
            api.request('GET', '/posts/stats/', null, false)
        ]).then(results => {
            // console.log("Footer data received:", results);
            const recentPostsData = results[0].status === 'fulfilled' ? results[0].value : null;
            const popularTagsData = results[1].status === 'fulfilled' ? results[1].value : null;
            const stats = results[2].status === 'fulfilled' ? results[2].value : null;

            const recentPosts = recentPostsData?.results || recentPostsData || [];
            const popularTags = popularTagsData?.results || popularTagsData || [];

             if (uiPosts && typeof uiPosts.renderFooter === 'function') {
                 uiPosts.renderFooter(recentPosts, popularTags, stats);
             } else {
                 console.error("function not found.");
             }

        });
    }

    function initialize() {
        auth.checkAuthStatus();

        const initPromise = $.Deferred();

        if (uiNavbar && typeof uiNavbar.updateNavbar === 'function') {
             uiNavbar.updateNavbar();
        } else {
             console.error("function not available .");
        }

        if (auth.getCurrentUser().token && !auth.getCurrentUser().role) {
             auth.fetchUserProfile()
                .done(function(){

                     if (uiNavbar && typeof uiNavbar.updateNavbar === 'function') {
                          uiNavbar.updateNavbar();
                     }
                    initPromise.resolve();
                })
                .fail(function(){

                    auth.handleLogout();
                    initPromise.reject();
                });
        } else {
             initPromise.resolve();
        }

        initPromise.done(function() {

            if (router && typeof router.handleHashChange === 'function') {
                router.handleHashChange();
                $(window).on('hashchange', router.handleHashChange);
            } else {

            }

            loadFooterData();

            $(document).off('click.skipLink').on('click.skipLink', 'a[href="#main-content"]', function(e) {
                e.preventDefault();
                const target = $('#main-content');
                if (target.length) {

                    target.attr('tabindex', -1).focus();

                    target.one('blur focusout', function () {
                       target.removeAttr('tabindex');
                    });
                } else {
                }
            });


            $(document).off('click.logoutLink').on('click.logoutLink', '#logout-link', function(e) {
                 e.preventDefault();

                 auth.handleLogout();
            });


        }).fail(function(){
             console.log("Initialization failed");
        });
    }

    window.initApp = {
        initialize: initialize,
        loadFooterData: loadFooterData
    };

    $(document).ready(initialize);

}(window, jQuery, window.api, window.auth, window.ui.common, window.ui.navbar, window.ui.posts, window.router));