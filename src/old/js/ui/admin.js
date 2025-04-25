
(function(window, $, uiCommon, auth) {

    window.ui = window.ui || {};

    function getRoleBadgeClass(role) {
         switch (role) {
             case 'admin': return 'danger';
             case 'editor': return 'warning';
             case 'author': return 'info';
             case 'reader': return 'secondary';
             default: return 'light';
         }
     }

     function renderCategoryAdminList(categories) {
        const contentArea = uiCommon.contentArea || $('#content-area');
        const categoryFormHtml = window.ui.forms?.renderCategoryForm() || '<p>Category form unavailable.</p>';

         contentArea.html(`
            <div class="d-flex justify-content-between align-items-center mb-3">
                 <h2>Manage Categories</h2>
                 <button class="btn btn-primary" id="add-category-btn"><i class="bi bi-plus-circle"></i> Add Category</button>
            </div>

            <div id="category-form-container" class="mb-3" style="display: none;">
                 ${categoryFormHtml}
            </div>
             <table class="table table-striped table-hover align-middle">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Slug</th>
                        <th class="text-end">Actions</th> 
                    </tr>
                </thead>
                <tbody id="category-list">
                    ${categories && categories.length > 0 ? categories.map(cat => `
                        <tr data-id="${cat.id}" data-name="${cat.name}" data-slug="${cat.slug}">
                            <td>${cat.id}</td>
                            <td class="cat-name">${cat.name}</td>
                            <td class="cat-slug">${cat.slug}</td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-warning btn-edit-category me-1" data-id="${cat.id}" title="Edit"><i class="bi bi-pencil"></i></button>
                                <button class="btn btn-sm btn-danger btn-delete-category" data-id="${cat.id}" title="Delete"><i class="bi bi-trash"></i></button>
                            </td>
                        </tr>`).join('') : `<tr><td colspan="4" class="text-center text-muted">No categories found.</td></tr>`
                    }
                </tbody>
            </table>
         `);
     }


     function renderUserAdminList(users) {
        const contentArea = uiCommon.contentArea || $('#content-area');
        contentArea.html(`
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h2>Manage Users</h2>
                <a href="/admin/users/user/add/" target="_blank" class="btn btn-primary"><i class="bi bi-plus-circle"></i> Add User (Admin)</a>
             </div>
             <p class="text-muted small">Full user management available in the <a href="/admin/users/" target="_blank">Django Admin interface</a>.</p>
             <table class="table table-striped table-hover align-middle">
                 <thead>
                     <tr>
                         <th>ID</th>
                         <th>Username</th>
                         <th>Email</th>
                         <th>Role</th>
                         <th>Staff</th>
                         <th>Joined</th>
                         <th class="text-end">Actions</th>
                     </tr>
                 </thead>
                 <tbody>
                     ${users && users.length > 0 ? users.map(user => `
                         <tr>
                             <td>${user.id}</td>
                             <td>${user.username}</td>
                             <td>${user.email || '-'}</td>
                             <td><span class="badge bg-${getRoleBadgeClass(user.role)}">${user.role}</span></td>
                             <td>${user.is_staff ? '<i class="bi bi-check-circle-fill text-success"></i> Yes' : '<i class="bi bi-x-circle text-danger"></i> No'}</td>
                             <td>${new Date(user.date_joined).toLocaleDateString()}</td>
                             <td class="text-end">
                                 <a href="/admin/users/user/${user.id}/change/" target="_blank" class="btn btn-sm btn-secondary" title="Edit in Django Admin"><i class="bi bi-pencil-square"></i></a>
                                  </td>
                         </tr>
                     `).join('') : `<tr><td colspan="7" class="text-center text-muted">No users found.</td></tr>`}
                 </tbody>
             </table>
             <div id="pagination-controls"></div>
         `);
     }


      function renderTagAdminList(tags) {
          const contentArea = uiCommon.contentArea || $('#content-area');
          contentArea.html(`
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h2>View Tags</h2>
                <span class="text-muted small">Tags are managed via posts</span>
             </div>
             <div class="d-flex flex-wrap gap-2">
                 ${tags && tags.length > 0 ? tags.map(tag => `
                      <a href="#posts/by_tag/${tag.name}" class="tag fs-6" title="${tag.post_count} posts">
                          ${tag.name} <span class="badge bg-secondary rounded-pill ms-1">${tag.post_count}</span>
                      </a>
                 `).join('') : '<p class="text-muted">No tags found.</p>'}
             </div>
             <div id="pagination-controls" class="mt-3"></div>
         `);
     }


    window.ui.admin = {
        renderCategoryAdminList: renderCategoryAdminList,
        renderUserAdminList: renderUserAdminList,
        renderTagAdminList: renderTagAdminList,
        getRoleBadgeClass: getRoleBadgeClass
    };

}(window, jQuery, window.ui.common, window.auth));
