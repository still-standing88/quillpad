
(function(window, $, api, uiCommon) {

    let currentUser = {
        token: localStorage.getItem('authToken'),
        username: localStorage.getItem('authUsername'),
        userId: localStorage.getItem('authUserId'),
        role: localStorage.getItem('authUserRole')
    };

    function getCurrentUser() {
        return currentUser;
    }

     function checkAuthStatus() {
         currentUser.token = localStorage.getItem('authToken');
         currentUser.username = localStorage.getItem('authUsername');
         currentUser.userId = localStorage.getItem('authUserId');
         currentUser.role = localStorage.getItem('authUserRole');
         return !!currentUser.token;
     }

    function fetchUserProfile() {
        const deferred = $.Deferred();
        if (!currentUser.token) {
            return deferred.reject().promise();
        }

        api.request('GET', '/profile/')
            .done(function(user) {
                currentUser.role = user.role;
                currentUser.username = user.username;
                currentUser.userId = user.id;
                localStorage.setItem('authUserRole', user.role);
                localStorage.setItem('authUsername', user.username);
                localStorage.setItem('authUserId', user.id);

                deferred.resolve(user);
            })
            .fail(function() {
                console.error("fetchUserProfile: Failed, invalid token.");
                deferred.reject();
            });
        return deferred.promise();
    }


    function handleLogin(event) {
        event.preventDefault();
        const username = $('#login-username').val();
        const password = $('#login-password').val();
        const $button = $(event.target).find('button[type="submit"]');
        const originalButtonText = $button.html();
        $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...');

        api.request('POST', '/login/', { username, password }, false)
            .done(function(data) {
                currentUser.token = data.token;
                currentUser.username = data.username;
                currentUser.userId = data.user_id;
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('authUsername', data.username);
                localStorage.setItem('authUserId', data.user_id);

                fetchUserProfile().done(function(){
                     if (uiCommon && typeof uiCommon.showAlert === 'function') {
                         uiCommon.showAlert('Login successful!', 'success');
                     }

                     if (window.ui && window.ui.navbar && typeof window.ui.navbar.updateNavbar === 'function') {
                         window.ui.navbar.updateNavbar();
                     }
                     if (window.router && typeof window.router.navigateTo === 'function') {
                         window.router.navigateTo('#/');
                     }
                }).fail(function(){
                    if (uiCommon && typeof uiCommon.showAlert === 'function') {
                        uiCommon.showAlert('Login succeeded but failed to load profile data.', 'warning');
                    }

                     if (window.ui && window.ui.navbar && typeof window.ui.navbar.updateNavbar === 'function') {
                         window.ui.navbar.updateNavbar();
                     }
                     if (window.router && typeof window.router.navigateTo === 'function') {
                         window.router.navigateTo('#/');
                     }
                });
            })
            .fail(function() {
            }).always(function(){
                $button.prop('disabled', false).html(originalButtonText);
            });
    }

    function handleRegister(event) {
        event.preventDefault();
        const username = $('#register-username').val();
        const email = $('#register-email').val();
        const password = $('#register-password').val();
        const $button = $(event.target).find('button[type="submit"]');
        const originalButtonText = $button.html();
        $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...');

        api.request('POST', '/register/', { username, email, password }, false)
            .done(function(data) {
                 if (uiCommon && typeof uiCommon.showAlert === 'function') {
                     uiCommon.showAlert('Registration successful! Please log in.', 'success');
                 }
                 if (window.router && typeof window.router.navigateTo === 'function') {
                    window.router.navigateTo('#login');
                 }
            })
            .fail(function() {
            }).always(function(){
                $button.prop('disabled', false).html(originalButtonText);
            });
    }

    function handleLogout() {
        console.log("loggdout");

        api.request('POST', '/auth/token/logout/')
            .always(function() {
                console.log("Cleanup auth state and redirect...");
                currentUser.token = null;
                currentUser.username = null;
                currentUser.userId = null;
                currentUser.role = null;
                localStorage.removeItem('authToken');
                localStorage.removeItem('authUsername');
                localStorage.removeItem('authUserId');
                localStorage.removeItem('authUserRole');

                if (window.ui && window.ui.navbar && typeof window.ui.navbar.updateNavbar === 'function') {
                    window.ui.navbar.updateNavbar();
                } else {
                    console.error("Navbar update function not available.");
                }

                if (uiCommon && typeof uiCommon.showAlert === 'function') {
                    uiCommon.showAlert('Logged out.', 'info');
                }

                if (window.router && typeof window.router.navigateTo === 'function') {
                    window.router.navigateTo('#login');
                } else {
                     console.error("function not available");

                     window.location.hash = '#login';
                     window.location.reload();
                }
            });
    }


    function canEditOrDelete(item) {
        if (!currentUser.token || !currentUser.role) return false;
        const isAdminOrEditor = ['admin', 'editor'].includes(currentUser.role);
        let isAuthor = false;

        const currentUserIdInt = parseInt(currentUser.userId);

        if (item && typeof item.author !== 'undefined' && item.author !== null) {
            if (typeof item.author === 'string') {
                isAuthor = item.author === currentUser.username;
            } else if (typeof item.author === 'number') {
                 isAuthor = item.author === currentUserIdInt;
            } else if (item.author && typeof item.author === 'object' && typeof item.author.id !== 'undefined') {
                 isAuthor = item.author.id === currentUserIdInt;
            } else if (item.author && typeof item.author === 'object' && typeof item.author.username !== 'undefined') {
                  isAuthor = item.author.username === currentUser.username;
            }
        } else if (item && typeof item.id !== 'undefined' && typeof item.username !== 'undefined') {
             isAuthor = item.id === currentUserIdInt;
        }

        return isAuthor || isAdminOrEditor;
    }

     function isAdmin() {
        return currentUser.role === 'admin';
     }
      function canCreatePost() {
         return ['admin', 'editor', 'author'].includes(currentUser.role);
      }


    window.auth = {
        getCurrentUser: getCurrentUser,
        checkAuthStatus: checkAuthStatus,
        fetchUserProfile: fetchUserProfile,
        handleLogin: handleLogin, // These might move to handlers later if preferred
        handleRegister: handleRegister,
        handleLogout: handleLogout,
        canEditOrDelete: canEditOrDelete,
        isAdmin: isAdmin,
        canCreatePost: canCreatePost
    };

}(window, jQuery, window.api, window.ui ? window.ui.common : null));
