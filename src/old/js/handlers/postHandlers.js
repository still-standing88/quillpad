
(function(window, $, api, auth, uiCommon, uiPosts) {

    window.handlers = window.handlers || {};

    function handleLikeToggle(event) {
         if (!auth.checkAuthStatus()) { window.router?.navigateTo('#login'); return; }
         const button = $(event.target).closest('.btn-like');
         const slug = button.data('slug');
         if (!slug) { console.error("missing data-slug"); return; }

         button.prop('disabled', true);

         api.request('POST', `/posts/${slug}/like/`)
             .done(function(response) {
                  if(uiPosts && typeof uiPosts.updateLikeButton === 'function') {
                    uiPosts.updateLikeButton(slug, response.liked, response.like_count);
                  } else {
                    console.error("updateLikeButton function not found");
                  }
             })
             .fail(function() {})
             .always(function() {
                 button.prop('disabled', false);
             });
     }

     function handleSaveToggle(event) {
          if (!auth.checkAuthStatus()) { window.router?.navigateTo('#login'); return; }
          const button = $(event.target).closest('.btn-save');
          const slug = button.data('slug');
           if (!slug) { console.error("missing data-slug"); return; }

          button.prop('disabled', true);

         api.request('POST', `/posts/${slug}/save/`)
             .done(function(response) {
                   if(uiPosts && typeof uiPosts.updateSaveButton === 'function') {
                       uiPosts.updateSaveButton(slug, response.saved);
                   } else {
                       console.error("updateSaveButton function  not found");
                   }

                   if (window.location.hash.startsWith('#saved-posts') && !response.saved) {
                        button.closest('.post-summary, .card').fadeOut(300, function() { $(this).remove(); });
                   }
             })
             .fail(function() { })
              .always(function() {
                 button.prop('disabled', false);
             });
     }

      function handlePostSubmit(event) {
         event.preventDefault();
         if (!auth.checkAuthStatus()) { window.router?.navigateTo('#login'); return; }

         const form = $(event.target);
         const slug = form.data('slug');
         const isEdit = !!slug;
         const method = isEdit ? 'PATCH' : 'POST';
         const endpoint = isEdit ? `/posts/${slug}/` : '/posts/';

         const formData = new FormData();
         const title = $('#post-title').val();
         const categoryVal = $('#post-category').val();
         const tagsVal = $('#post-tags').val();
         const isPublished = $('#post-is-published').is(':checked');
         const isFeatured = $('#post-featured').is(':checked');

          if (!title.trim()) {
              uiCommon.showAlert('Post title cannot be empty.', 'warning');
              return;
          }


         formData.append('title', title);
         if(categoryVal) { formData.append('category', categoryVal); }
         if(tagsVal) formData.append('tags', tagsVal);
         formData.append('is_published', isPublished);
         formData.append('featured', isFeatured);


         if (window.editorInstance) {
             formData.append('content', window.editorInstance.getMarkdown());
         } else {
             console.error("Toast UI Editor instance not found");
             uiCommon.showAlert('Error: Content editor not ready.', 'danger');
             return;
         }

         const imageFile = $('#post-featured-image')[0].files[0];
         const removeImage = isEdit && $('#remove-image').is(':checked');

         if (imageFile) {
             formData.append('featured_image', imageFile);
         } else if (removeImage) {
             formData.append('featured_image', '');
         }

         const submitButton = form.find('button[type="submit"]');
         const originalButtonText = submitButton.html();
         submitButton.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...');

         api.request(method, endpoint, formData, true, true)
             .done(function(post) {
                 uiCommon.showAlert(`Post ${isEdit ? 'updated' : 'created'} successfully!`, 'success');
                 if (window.router && typeof window.router.navigateTo === 'function') {
                    window.router.navigateTo(`#posts/${post.slug}`);
                 }
             })
             .fail(function() { })
             .always(function() {
                  submitButton.prop('disabled', false).html(originalButtonText);
             });
     }

     function handleDeletePost(event) {
        if (!auth.checkAuthStatus()) { window.router?.navigateTo('#login'); return; }
        const button = $(event.target).closest('.btn-delete-post');
        const slug = button.data('slug');
        if (!slug) { console.error("missing data-slug"); return; }

         if (confirm('Are you sure you want to delete this post? This cannot be undone.')) {

             button.prop('disabled', true);
             api.request('DELETE', `/posts/${slug}/`) 
                 .done(function() {
                     uiCommon.showAlert('Post deleted successfully.', 'success');
                     const currentHash = window.location.hash;

                     if (currentHash === `#posts/${slug}` || currentHash === `#edit-post/${slug}`) {
                         window.router?.navigateTo('#/');
                     } else {

                          window.router?.handleHashChange();
                     }
                 })
                 .fail(function() {
                     button.prop('disabled', false); 

                 });
         }
     }

    window.handlers.posts = {
        handleLikeToggle: handleLikeToggle,
        handleSaveToggle: handleSaveToggle,
        handlePostSubmit: handlePostSubmit,
        handleDeletePost: handleDeletePost
    };

}(window, jQuery, window.api, window.auth, window.ui.common, window.ui.posts));
