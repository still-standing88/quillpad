
(function(window, $, api, auth, uiCommon, uiAdmin, uiForms) {

    window.handlers = window.handlers || {};

    function handleCategorySubmit(event) {
        event.preventDefault();
        if (!auth.isAdmin()) return; 

        const form = $(event.target);
        const id = form.data('id');
        const name = form.find('#category-name').val();
        const isEdit = !!id;
        const method = isEdit ? 'PUT' : 'POST';
        const endpoint = isEdit ? `/categories/${id}/` : '/categories/';

        if (!name.trim()) {
            uiCommon.showAlert('Category name cannot be empty.', 'warning');
            return;
        }
         const submitButton = form.find('button[type="submit"]');
         const originalButtonText = submitButton.html();
         submitButton.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');


        const payload = { name: name };

        api.request(method, endpoint, payload)
            .done(function(category) {
                uiCommon.showAlert(`Category ${isEdit ? 'updated' : 'created'}.`, 'success');
                form.parent().slideUp(function(){

                    $(this).empty().html(uiForms?.renderCategoryForm() || '<p>Error</p>').hide();
                 });

                if (window.router && typeof window.router.loadCategoryAdmin === 'function') {
                    window.router.loadCategoryAdmin();
                } else {
                     console.error("loadCategoryAdmin function not found");
                }
            })
             .fail(function() { })
             .always(function() {
                  submitButton.prop('disabled', false).html(originalButtonText);
             });
    }

    function handleEditCategoryClick(event) {
         if (!auth.isAdmin()) return;
         const button = $(event.target).closest('button');
         const id = button.data('id');
         const row = button.closest('tr');
         const name = row.find('.cat-name').text();
         const slug = row.find('.cat-slug').text();
         const formContainer = $('#category-form-container');

         const categoryFormHtml = uiForms?.renderCategoryForm({ id, name, slug }) || '<p>Error loading edit form.</p>';
         formContainer.html(categoryFormHtml).slideDown();
         formContainer.find('#category-name').focus();
     }


    function handleDeleteCategory(event) {
        if (!auth.isAdmin()) return;
        const button = $(event.target).closest('button');
        const id = button.data('id');
        const row = button.closest('tr');
        const name = row.find('.cat-name').text();

        if (!id) { console.error("Delete button missing category ID"); return; }

        if (confirm(`Are you sure you want to delete the category "${name}"? This might affect posts using it.`)) {
            button.prop('disabled', true);
            api.request('DELETE', `/categories/${id}/`)
                .done(function() {
                    uiCommon.showAlert(`Category "${name}" deleted.`, 'success');

                     if (window.router && typeof window.router.loadCategoryAdmin === 'function') {
                        window.router.loadCategoryAdmin();
                    } else {
                         console.error("loadCategoryAdmin function  not found");
                         row.fadeOut(300, function() { $(this).remove(); });
                    }
                 })
                 .fail(function() {
                     button.prop('disabled', false);
                     
                 });
        }
    }

    window.handlers.admin = {
        handleCategorySubmit: handleCategorySubmit,
        handleEditCategoryClick: handleEditCategoryClick,
        handleDeleteCategory: handleDeleteCategory

    };

}(window, jQuery, window.api, window.auth, window.ui.common, window.ui.admin, window.ui.forms));
