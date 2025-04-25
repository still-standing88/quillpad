(function(window, $, api, auth, uiCommon, uiNavbar, uiPosts, uiComments, uiForms, uiProfile, uiAdmin, handlers) {

    window.router = window.router || {};

    let currentEditorInstance = null;

    function destroyEditor() {
        if (currentEditorInstance) {
            try {
                currentEditorInstance.destroy();
                 console.log("Router: Editor instance destroyed.");
            } catch (e) {
                console.error("Router: Error destroying editor instance:", e);
            }
            currentEditorInstance = null;
             if (window.editorInstance === currentEditorInstance) {
                window.editorInstance = null;
             }
        }
    }

    function initializeEditor(initialContent = '') {
        destroyEditor();
        try {
            const editorElement = document.querySelector('#toastui-editor');
            if (!editorElement) {
                console.error("Router: #toastui-editor element not found for initialization.");
                return;
            }
             if (typeof toastui === 'undefined' || typeof toastui.Editor === 'undefined') {
                console.error("Router: Toast UI Editor library not loaded.");
                $('#toastui-editor').html('<p class="text-danger">Error: Text editor library failed to load.</p>');
                return;
             }

             currentEditorInstance = new toastui.Editor({
                 el: editorElement,
                 height: '400px',
                 initialEditType: 'markdown',
                 previewStyle: 'vertical',
                 initialValue: initialContent,
                 linkAttributes: { target: '_blank', rel: 'noopener noreferrer' }
             });
             window.editorInstance = currentEditorInstance;
             console.log("Router: Toast UI Editor Initialized");
        } catch (e) {
            console.error("Router: Failed to initialize Toast UI Editor:", e);
            $('#toastui-editor').html('<p class="text-danger">Error loading text editor.</p>');
        }
    }

    function loadHomepage(limit, offset) {
        uiCommon.contentArea.html('<h2>Latest Posts</h2><div id="post-list" class="mb-3">Loading...</div><div id="pagination-controls"></div>');
        api.request('GET', `/posts/?limit=${limit}&offset=${offset}`, null, false)
            .done(function(data) {
                uiPosts.renderPostList(data.results || [], "Latest Posts");
                uiCommon.renderPagination('#pagination-controls', data.count, limit, offset, '#/');
            })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading posts.</p>'); });
    }

    function loadPostDetail(slug) {
        uiCommon.contentArea.html('<div class="text-center mt-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading post...</span></div></div>');
        api.request('POST', `/posts/${slug}/view/`, null, false)
            .fail(function(jqXHR){ console.warn("Failed to increment view count:", jqXHR.status); });

        api.request('GET', `/posts/${slug}/`, null, false)
            .done(function(post) { uiPosts.renderFullPost(post); loadComments(post.id); })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading post details.</p>'); });
    }

    function loadComments(postId) {
        const commentsList = $('#comments-list');
        if (!commentsList.length) return;
        commentsList.html('<span class="text-muted small">Loading comments...</span>');

        api.request('GET', `/comments/by_post/?post_id=${postId}`, null, false)
            .done(function(commentsData) { uiComments.renderComments(commentsData, postId); })
            .fail(function() { commentsList.html('<p class="text-danger small">Error loading comments.</p>'); });
    }
    window.router.loadComments = loadComments;

    function loadMyPosts(limit, offset) {
        if (!auth.checkAuthStatus()) { navigateTo('#login'); return; }
        uiCommon.contentArea.html('<h2>My Posts</h2><div id="post-list" class="mb-3">Loading...</div><div id="pagination-controls"></div>');
        api.request('GET', `/posts/my_posts/?limit=${limit}&offset=${offset}`)
            .done(function(data) { uiPosts.renderPostList(data.results || [], "My Posts"); uiCommon.renderPagination('#pagination-controls', data.count, limit, offset, '#my-posts'); })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading your posts.</p>'); });
    }

    function loadSavedPosts(limit, offset) {
        if (!auth.checkAuthStatus()) { navigateTo('#login'); return; }
        uiCommon.contentArea.html('<h2>Saved Posts</h2><div id="post-list" class="mb-3">Loading...</div><div id="pagination-controls"></div>');
        api.request('GET', `/posts/saved/?limit=${limit}&offset=${offset}`)
            .done(function(data) { uiPosts.renderPostList(data.results || [], "Saved Posts"); uiCommon.renderPagination('#pagination-controls', data.count, limit, offset, '#saved-posts'); })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading saved posts.</p>'); });
    }

    function loadPostsBy(type, value, limit, offset) {
        let endpoint = '', title = '', baseUrl = '';
        switch (type) {
            case 'category': endpoint = `/posts/by_category/?slug=${value}`; title = `Posts in Category: ${value}`; baseUrl = `#posts/by_category/${value}`; break;
            case 'tag': endpoint = `/posts/by_tag/?name=${value}`; title = `Posts Tagged: ${value}`; baseUrl = `#posts/by_tag/${value}`; break;
            case 'user': endpoint = `/posts/by_user/?username=${value}`; title = `Posts by User: ${value}`; baseUrl = `#posts/by_user/${value}`; break;
            default: navigateTo('#/'); return;
        }
        endpoint += `&limit=${limit}&offset=${offset}`;

        uiCommon.contentArea.html(`<h2>${title}</h2><div id="post-list" class="mb-3">Loading...</div><div id="pagination-controls"></div>`);
        api.request('GET', endpoint, null, false)
            .done(function(data) { uiPosts.renderPostList(data.results || [], title); uiCommon.renderPagination('#pagination-controls', data.count, limit, offset, baseUrl); })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading posts.</p>'); });
    }

    function loadProfilePage() {
        if (!auth.checkAuthStatus()) { navigateTo('#login'); return; }
        uiCommon.contentArea.html('<div class="text-center mt-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading profile...</span></div></div>');
        api.request('GET', '/profile/')
            .done(function(user) { uiProfile.renderProfile(user); })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading profile.</p>'); });
    }

    function loadCreateEditForm(slug = null) {
        if (!auth.checkAuthStatus()) { navigateTo('#login'); return; }
        if (!auth.canCreatePost() && !slug) { uiCommon.showAlert('You do not have permission to create posts.', 'warning'); navigateTo('#/'); return; }

        const isEdit = slug !== null;
        const title = isEdit ? 'Edit Post' : 'Create New Post';
        uiCommon.contentArea.html(`<h2>${title}</h2><div id="form-container">${uiForms.renderPostForm([], [])}</div>`);

         Promise.all([
            api.request('GET', '/categories/?limit=1000', null, false),
            api.request('GET', '/tags/?limit=1000', null, false)
         ]).then(([categoriesResponse, tagsResponse]) => {
                const categories = categoriesResponse.results || categoriesResponse || [];
                const allTags = tagsResponse.results || tagsResponse || [];

                if (isEdit) {
                    api.request('GET', `/posts/${slug}/`)
                        .done(postData => {
                            if (!auth.canEditOrDelete(postData)) { uiCommon.showAlert('You do not have permission to edit this post.', 'danger'); navigateTo(`#posts/${slug}`); return; }
                            $('#form-container').html(uiForms.renderPostForm(categories, allTags, postData));
                            initializeEditor(postData?.content || '');
                        })
                        .fail(() => { $('#form-container').html('<p>Error loading post data for editing.</p>'); });
                } else {
                     $('#form-container').html(uiForms.renderPostForm(categories, allTags));
                      initializeEditor('');
                }
         }).catch(() => { $('#form-container').html('<p>Error loading categories or tags.</p>'); });
    }

    function loadCategoryAdmin() {
       if (!auth.isAdmin()) { navigateTo('#/'); return; }
       uiCommon.contentArea.html('<div class="text-center mt-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading categories...</span></div></div>');
       api.request('GET', '/categories/?limit=1000')
           .done(function(data) { uiAdmin.renderCategoryAdminList(data.results || data || []); })
           .fail(function() { uiCommon.contentArea.html('<p>Error loading categories.</p>'); });
    }
    window.router.loadCategoryAdmin = loadCategoryAdmin;


     function loadUserAdmin(limit, offset) {
        if (!auth.isAdmin()) { navigateTo('#/'); return; }
        uiCommon.contentArea.html('<div class="text-center mt-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading users...</span></div></div>');
        api.request('GET', `/users/?limit=${limit}&offset=${offset}`)
            .done(function(data) { uiAdmin.renderUserAdminList(data.results || []); uiCommon.renderPagination('#pagination-controls', data.count, limit, offset, '#admin/users'); })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading users.</p>'); });
     }

      function loadTagAdmin(limit, offset) {
        if (!auth.isAdmin()) { navigateTo('#/'); return; }
        uiCommon.contentArea.html('<div class="text-center mt-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading tags...</span></div></div>');
        api.request('GET', `/tags/?limit=${limit}&offset=${offset}`)
            .done(function(data) { uiAdmin.renderTagAdminList(data.results || []); uiCommon.renderPagination('#pagination-controls', data.count, limit, offset, '#admin/tags'); })
            .fail(function() { uiCommon.contentArea.html('<p>Error loading tags.</p>'); });
     }

    function navigateTo(hash) {
        if (window.location.hash !== hash) {
            console.log(`Navigating to: ${hash}`);
             window.location.hash = hash;
        } else {
             console.log(`Already at ${hash}, forcing reload via handleHashChange.`);
            handleHashChange();
        }
    }
    window.router.navigateTo = navigateTo;

    function handleHashChange() {
        console.log("Router: Hash changed to:", window.location.hash);
        destroyEditor();
        uiCommon.alertContainer.empty();
        uiCommon.contentArea.off();
        uiCommon.contentArea.empty().html('<div class="text-center mt-5"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>');

        const hash = window.location.hash || '#/';

        
        if (hash === '#main-content') {

            uiCommon.contentArea.html('');

             $('#main-content').attr('tabindex', -1).focus();
            return;
        }


        const hashParts = hash.substring(1).split('?');
        const path = hashParts[0];
        const queryString = hashParts[1];
        const pathParts = path.split('/');

        const route = pathParts[0] || 'home';
        const param1 = pathParts[1];
        const param2 = pathParts[2];
        const queryParams = {};

        if (queryString) {
            queryString.split('&').forEach(pair => {
                const [key, value] = pair.split('=');
                if (key) { queryParams[key] = decodeURIComponent(value || ''); }
            });
        }

        const offset = parseInt(queryParams.offset) || 0;
        const limit = parseInt(queryParams.limit) || 10;

        console.log('Router: Routing decision:', { route, param1, param2, queryParams, offset, limit });

        switch (route) {
            case 'home': loadHomepage(limit, offset); attachPostListActionHandlers(); break;
            case 'posts':
                if (!param1) { loadHomepage(limit, offset); attachPostListActionHandlers(); }
                else if (param1 === 'by_category' && param2) { loadPostsBy('category', param2, limit, offset); attachPostListActionHandlers(); }
                else if (param1 === 'by_tag' && param2) { loadPostsBy('tag', param2, limit, offset); attachPostListActionHandlers(); }
                else if (param1 === 'by_user' && param2) { loadPostsBy('user', param2, limit, offset); attachPostListActionHandlers(); }
                else { loadPostDetail(param1); attachPostDetailActionHandlers(); }
                break;
            case 'login':
                if (auth.checkAuthStatus()) { navigateTo('#/'); break; }
                uiForms.renderLoginForm();
                uiCommon.contentArea.on('submit', '#login-form', auth.handleLogin);
                break;
            case 'register':
                if (auth.checkAuthStatus()) { navigateTo('#/'); break; }
                uiForms.renderRegisterForm();
                uiCommon.contentArea.on('submit', '#register-form', auth.handleRegister);
                break;
            case 'logout': auth.handleLogout(); break;
            case 'profile':
                 if (!auth.checkAuthStatus()) { navigateTo('#login'); break; }
                 loadProfilePage(); attachProfilePageHandlers(); break;
            case 'my-posts':
                if (!auth.checkAuthStatus()) { navigateTo('#login'); break; }
                loadMyPosts(limit, offset); attachPostListActionHandlers(); break;
            case 'saved-posts':
                if (!auth.checkAuthStatus()) { navigateTo('#login'); break; }
                loadSavedPosts(limit, offset); attachPostListActionHandlers(); break;
            case 'create-post':
                 if (!auth.checkAuthStatus()) { navigateTo('#login'); break; }
                loadCreateEditForm(); attachPostFormHandlers(); break;
             case 'edit-post':
                 if (!auth.checkAuthStatus()) { navigateTo('#login'); break; }
                 if (param1) { loadCreateEditForm(param1); attachPostFormHandlers(); }
                 else { navigateTo('#/'); } break;
             case 'admin':
                 if (!auth.isAdmin()) { navigateTo('#/'); break; }
                 if (param1 === 'categories') { loadCategoryAdmin(); attachCategoryAdminHandlers(); }
                 else if (param1 === 'users') { loadUserAdmin(limit, offset); }
                 else if (param1 === 'tags') { loadTagAdmin(limit, offset); }
                 else { navigateTo('#/'); } break;
            default: uiCommon.contentArea.html('<h2 class="text-center mt-5">404 Not Found</h2><p class="text-center">The page you requested does not exist.</p>');
        }

        updateActiveNavLink(hash);

         const navbarCollapse = document.getElementById('navbarNav');
         if (navbarCollapse?.classList.contains('show')) {
            bootstrap.Collapse.getInstance(navbarCollapse)?.hide();
         }
    }
    window.router.handleHashChange = handleHashChange;


    function updateActiveNavLink(currentHash) {
        $('.navbar-nav .nav-link').removeClass('active').removeAttr('aria-current');
        $('.navbar-nav .dropdown-toggle').removeClass('active');

        const currentBaseHash = currentHash.split('?')[0];
        let $activeLink = $(`.navbar-nav .nav-link[href="${currentBaseHash}"]`);

        if (!$activeLink.length) {
             const route = currentBaseHash.substring(1).split('/')[0] || 'home';
             const baseRoute = `#${route}`;

             $activeLink = $(`.navbar-nav .nav-link[href="${baseRoute}"]`);
             if (!$activeLink.length) {

                 $activeLink = $(`.navbar-nav .nav-link[href^="${baseRoute}/"]`);
             }
        }
         if (!$activeLink.length && (currentBaseHash === '#/' || currentBaseHash === '#')) {
              $activeLink = $('.navbar-nav .nav-link[href="#/"]');
         }

         if ($activeLink.length) {
             const linkToActivate = $activeLink.first();
              linkToActivate.addClass('active').attr('aria-current', 'page');
              linkToActivate.closest('.dropdown').find('.nav-link.dropdown-toggle').addClass('active');
         }
    }

    function attachPostListActionHandlers() {
         if (!handlers || !handlers.posts) { console.error("Post handlers not loaded"); return; }
         uiCommon.contentArea.on('click.postList', '.btn-like', handlers.posts.handleLikeToggle);
         uiCommon.contentArea.on('click.postList', '.btn-save', handlers.posts.handleSaveToggle);
         uiCommon.contentArea.on('click.postList', '.btn-delete-post', handlers.posts.handleDeletePost);
     }

     function attachPostDetailActionHandlers() {
        if (!handlers || !handlers.comments || !handlers.posts) { console.error("Comment or Post handlers not loaded"); return; }
         uiCommon.contentArea.on('submit.postDetail', '.comment-form', handlers.comments.handleCommentSubmit);
         uiCommon.contentArea.on('click.postDetail', '.btn-reply', handlers.comments.handleReplyButtonClick);
         uiCommon.contentArea.on('click.postDetail', '.btn-cancel-reply', handlers.comments.handleCancelReply);
         uiCommon.contentArea.on('click.postDetail', '.btn-delete-comment', handlers.comments.handleDeleteComment);
         uiCommon.contentArea.on('click.postDetail', '.btn-like', handlers.posts.handleLikeToggle);
         uiCommon.contentArea.on('click.postDetail', '.btn-save', handlers.posts.handleSaveToggle);
         uiCommon.contentArea.on('click.postDetail', '.btn-delete-post', handlers.posts.handleDeletePost);
     }

     function attachProfilePageHandlers() {
        if (!handlers || !handlers.profile) { console.error("Profile handlers not loaded"); return; }
        uiCommon.contentArea.on('submit.profile', '#profile-update-form', handlers.profile.handleProfileUpdate);
        uiCommon.contentArea.on('submit.profile', '#change-password-form', handlers.profile.handleChangePassword);
        uiCommon.contentArea.on('submit.profile', '#avatar-upload-form', handlers.profile.handleAvatarUpload);
     }

      function attachCategoryAdminHandlers() {
        if (!handlers || !handlers.admin || !uiForms) { console.error("Admin handlers or uiForms not loaded"); return; }
        uiCommon.contentArea.on('click.adminCat', '#add-category-btn', function() {
            const formContainer = $('#category-form-container');
            if (!formContainer.is(':visible')) {
                 const formHtml = uiForms.renderCategoryForm();
                 formContainer.html(formHtml).slideDown();
                 formContainer.find('#category-name').focus();
             }
        });
        uiCommon.contentArea.on('click.adminCat', '#cancel-category-form', function(e) {
             const formHtml = uiForms.renderCategoryForm();
            $(e.target).closest('form').parent().slideUp(function(){ $(this).empty().html(formHtml).hide(); });
        });
        uiCommon.contentArea.on('submit.adminCat', '#category-form', handlers.admin.handleCategorySubmit);
        uiCommon.contentArea.on('click.adminCat', '.btn-edit-category', handlers.admin.handleEditCategoryClick);
        uiCommon.contentArea.on('click.adminCat', '.btn-delete-category', handlers.admin.handleDeleteCategory);
     }

     function attachPostFormHandlers() {
        if (!handlers || !handlers.posts) { console.error("Post handlers not loaded"); return; }
        uiCommon.contentArea.on('submit.postForm', '#post-form', handlers.posts.handlePostSubmit);
     }


}(window, jQuery,
  window.api, window.auth,
  window.ui.common, window.ui.navbar, window.ui.posts, window.ui.comments, window.ui.forms, window.ui.profile, window.ui.admin,
  window.handlers
));