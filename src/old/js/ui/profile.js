
(function(window, $, auth, uiCommon) {

    window.ui = window.ui || {};

    function renderProfile(user) {
         const contentArea = uiCommon.contentArea || $('#content-area');
         const avatarUrl = user.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.username || '?')}&background=random&size=150`;
         
         const safeBio = user.bio ? $('<div>').text(user.bio).html() : '';

         const badgeClass = window.ui.admin?.getRoleBadgeClass(user.role) || 'secondary';

         contentArea.html(`
             <h2>User Profile</h2>
             <div class="card mb-4">
                 <div class="card-body">
                     <div class="row">
                        <div class="col-md-4 text-center">
                            <img src="${avatarUrl}" alt="${user.username}'s avatar" class="avatar-lg img-thumbnail mb-3">
                            <form id="avatar-upload-form" class="mb-3">
                                <label for="avatar-input" class="form-label small">Change Avatar</label>
                                <input type="file" id="avatar-input" name="avatar" accept="image/*" class="form-control form-control-sm mb-2">
                                <button type="submit" class="btn btn-sm btn-secondary">Upload Image</button>
                            </form>
                        </div>
                         <div class="col-md-8">
                             <h4 class="card-title">${user.username} <span class="badge bg-${badgeClass}">${user.role}</span></h4>
                             <p class="card-text mb-1"><strong>Email:</strong> ${user.email}</p>
                             <p class="card-text text-muted small">Joined: ${new Date(user.date_joined || Date.now()).toLocaleDateString()}</p>
                             <hr>
                             <form id="profile-update-form">
                                 <div class="mb-3">
                                     <label for="profile-bio" class="form-label">Bio</label>
                                     <textarea class="form-control" id="profile-bio" name="bio" rows="4">${safeBio}</textarea>
                                 </div>
                                 <button type="submit" class="btn btn-primary">Update Bio</button>
                             </form>
                         </div>
                     </div>
                 </div>
             </div>

             <div class="card">
                <div class="card-body">
                    <h3 class="card-title">Change Password</h3>
                    <div id="change-password-section">
                        ${renderChangePasswordForm()} 
                    </div>
                 </div>
             </div>
         `);
    }


    function renderChangePasswordForm() {
         return `
            <form id="change-password-form">
                <div class="mb-3">
                    <label for="current-password" class="form-label">Current Password</label>
                    <input type="password" class="form-control" id="current-password" required autocomplete="current-password">
                </div>
                <div class="mb-3">
                    <label for="new-password" class="form-label">New Password</label>
                    <input type="password" class="form-control" id="new-password" required minlength="8" autocomplete="new-password">
                </div>
                 <div class="mb-3">
                    <label for="confirm-password" class="form-label">Confirm New Password</label>
                    <input type="password" class="form-control" id="confirm-password" required minlength="8" autocomplete="new-password">
                </div>
                <button type="submit" class="btn btn-warning">Change Password</button>
            </form>
         `;
     }

    window.ui.profile = {
        renderProfile: renderProfile,
        renderChangePasswordForm: renderChangePasswordForm
    };

}(window, jQuery, window.auth, window.ui.common));
