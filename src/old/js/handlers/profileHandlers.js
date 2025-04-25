
(function(window, $, api, auth, uiCommon, uiProfile) {

    window.handlers = window.handlers || {};

     function handleProfileUpdate(event) {
        event.preventDefault();
        if (!auth.checkAuthStatus()) return;

        const bio = $('#profile-bio').val();
        const $button = $(event.target).find('button[type="submit"]');
        const originalButtonText = $button.html();
        $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...');

        api.request('PATCH', '/profile/', { bio: bio })
            .done(function(updatedUser) {
                if (uiCommon && uiProfile) {
                     uiCommon.showAlert('Profile updated successfully.', 'success');

                     uiProfile.renderProfile(updatedUser);
                }
            }).fail(function(){

            }).always(function(){
                 $button.prop('disabled', false).html(originalButtonText);
            });
    }

    function handleAvatarUpload(event) {
         event.preventDefault();
         if (!auth.checkAuthStatus()) return;

         const fileInput = document.getElementById('avatar-input');
         const $button = $(event.target).find('button[type="submit"]');
         const originalButtonText = $button.html();

         if (fileInput.files.length === 0) {
              if (uiCommon) uiCommon.showAlert('Please select an image file.', 'warning');
             return;
         }
         const formData = new FormData();
         formData.append('avatar', fileInput.files[0]);

          $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...');

         api.request('PATCH', '/profile/', formData, true, true)
             .done(function(updatedUser) {
                 if (uiCommon && uiProfile) {
                     uiCommon.showAlert('Avatar updated successfully.', 'success');

                     uiProfile.renderProfile(updatedUser);
                 }
             }).fail(function(){
            }).always(function(){
                $button.prop('disabled', false).html(originalButtonText);
            });
     }

     function handleChangePassword(event) {
        event.preventDefault();
        if (!auth.checkAuthStatus()) return;

        const currentPassword = $('#current-password').val();
        const newPassword = $('#new-password').val();
        const confirmPassword = $('#confirm-password').val();
        const $button = $(event.target).find('button[type="submit"]');
        const originalButtonText = $button.html();

        if (newPassword !== confirmPassword) {
             if (uiCommon) uiCommon.showAlert('New passwords do not match.', 'warning');
            return;
        }
         if (!newPassword) {
            if (uiCommon) uiCommon.showAlert('New password cannot be empty.', 'warning');
            return;
         }

          $button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Changing...');

        api.request('POST', '/change-password/', { current_password: currentPassword, new_password: newPassword })
             .done(function() {
                 if (uiCommon) uiCommon.showAlert('Password changed successfully. Logging out.', 'success');
                 auth.handleLogout();
             }).fail(function(){
             }).always(function(){
                  $button.prop('disabled', false).html(originalButtonText);
             });
     }

    window.handlers.profile = {
        handleProfileUpdate: handleProfileUpdate,
        handleAvatarUpload: handleAvatarUpload,
        handleChangePassword: handleChangePassword
    };

}(window, jQuery, window.api, window.auth, window.ui.common, window.ui.profile));
