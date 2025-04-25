
(function(window, $, auth) {

    window.ui = window.ui || {};

    function renderLoginForm() {

        const contentArea = window.ui.common.contentArea || $('#content-area');
        contentArea.html(`
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <h2 class="text-center mb-4">Login</h2>
                    <form id="login-form">
                        <div class="mb-3">
                            <label for="login-username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="login-username" required autocomplete="username">
                        </div>
                        <div class="mb-3">
                            <label for="login-password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="login-password" required autocomplete="current-password">
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Login</button>
                        </div>
                         <p class="mt-3 text-center">Don't have an account? <a href="#register">Register here</a>.</p>
                    </form>
                </div>
            </div>
        `);
    }

     function renderRegisterForm() {
        const contentArea = window.ui.common.contentArea || $('#content-area');
        contentArea.html(`
             <div class="row justify-content-center">
                <div class="col-md-6">
                    <h2 class="text-center mb-4">Register</h2>
                    <form id="register-form">
                        <div class="mb-3">
                            <label for="register-username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="register-username" required autocomplete="username">
                        </div>
                         <div class="mb-3">
                            <label for="register-email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="register-email" required autocomplete="email">
                        </div>
                        <div class="mb-3">
                            <label for="register-password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="register-password" required minlength="8" autocomplete="new-password">
                             <div class="form-text">Minimum 8 characters.</div>
                        </div>
                         <div class="d-grid">
                            <button type="submit" class="btn btn-primary">Register</button>
                         </div>
                          <p class="mt-3 text-center">Already have an account? <a href="#login">Login here</a>.</p>
                    </form>
                 </div>
             </div>
        `);
    }

    function renderPostForm(categories = [], allTags = [], post = null) {
        const isEdit = post !== null;
        const currentTags = post ? (post.tags || []).join(', ') : '';
        const title = isEdit ? 'Edit Post' : 'Create New Post';

        const editorContainerHtml = `<div id="toastui-editor" style="min-height: 400px;"></div>`;

        return `
            <form id="post-form" data-slug="${isEdit ? post.slug : ''}">
                 <div class="row">
                     <div class="col-md-8">
                        <div class="mb-3">
                            <label for="post-title" class="form-label">Title</label>
                            <input type="text" class="form-control" id="post-title" value="${post?.title || ''}" required>
                        </div>
                         <div class="mb-3">
                            <label for="toastui-editor" class="form-label">Content</label>
                            ${editorContainerHtml}
                         </div>
                     </div>
                     <div class="col-md-4">
                         <div class="mb-3">
                            <label for="post-category" class="form-label">Category</label>
                            <select class="form-select" id="post-category">
                                <option value="">-- Select Category --</option>
                                ${categories.map(cat => `<option value="${cat.name}" ${post?.category === cat.name ? 'selected' : ''}>${cat.name}</option>`).join('')}
                             </select>
                             ${auth.isAdmin() ? '<div class="form-text"><a href="#admin/categories">Manage Categories</a></div>' : ''}
                        </div>
                         <div class="mb-3">
                            <label for="post-tags" class="form-label">Tags (comma-separated)</label>
                            <input type="text" class="form-control" id="post-tags" value="${currentTags}">
                            <div class="form-text">Suggested: ${allTags.slice(0, 10).map(t => t.name).join(', ')}</div>
                        </div>
                         <div class="mb-3">
                             <label for="post-featured-image" class="form-label">Featured Image</label>
                             <input type="file" class="form-control" id="post-featured-image" accept="image/*">
                             ${post?.featured_image_url ? `<div class="mt-2"><img src="${post.featured_image_url}" alt="Current image" class="img-thumbnail" style="max-height: 100px;"><label class="form-check-label ms-2 small" for="remove-image"><input type="checkbox" class="form-check-input" id="remove-image"> Remove</label></div>` : ''}
                         </div>
                         <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="post-is-published" ${post?.is_published !== false ? 'checked' : ''}>
                            <label class="form-check-label" for="post-is-published">
                                Published
                            </label>
                        </div>
                         <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" id="post-featured" ${post?.featured ? 'checked' : ''}>
                            <label class="form-check-label" for="post-featured">
                                Featured Post
                            </label>
                        </div>
                         <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">${isEdit ? 'Update Post' : 'Create Post'}</button>
                            <a href="${isEdit ? `#posts/${post.slug}` : '#/'}" class="btn btn-secondary">Cancel</a>
                         </div>
                     </div>
                 </div>
            </form>
          `;
     }

     function renderCategoryForm(category = null) {
         const isEdit = category !== null;
         const id = isEdit ? category.id : '';
         const name = isEdit ? category.name : '';
         return `
             <form id="category-form" data-id="${id}" class="card card-body">
                <h5>${isEdit ? 'Edit' : 'Add New'} Category</h5>
                <input type="hidden" id="category-id" value="${id}">
                <div class="mb-2">
                    <label for="category-name" class="form-label">Name</label>
                    <input type="text" id="category-name" class="form-control" value="${name}" required>
                </div>
                 <div class="d-flex">
                     <button type="submit" class="btn btn-success btn-sm">${isEdit ? 'Update' : 'Create'}</button>
                     <button type="button" class="btn btn-secondary btn-sm ms-2" id="cancel-category-form">Cancel</button>
                 </div>
             </form>
         `;
     }


    window.ui.forms = {
        renderLoginForm: renderLoginForm,
        renderRegisterForm: renderRegisterForm,
        renderPostForm: renderPostForm,
        renderCategoryForm: renderCategoryForm
    };

}(window, jQuery, window.auth));
