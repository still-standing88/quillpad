
(function(window, $, api, auth, uiCommon) {

    window.handlers = window.handlers || {};

     function handleCommentSubmit(event) {
        event.preventDefault();
        if (!auth.checkAuthStatus()) { window.router?.navigateTo('#login'); return; }

        const form = $(event.target);
        const postId = form.data('post-id');
        const parentId = form.data('parent-id') || null;
        const content = form.find('textarea[name="content"]').val();

        if (!postId) { console.error("Comment form missing post ID"); return; }
        if (!content.trim()) { uiCommon.showAlert('Comment cannot be empty.', 'warning'); return; }

        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.html();
        submitButton.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Posting...');

        api.request('POST', '/comments/', { post: postId, parent: parentId, content: content })
            .done(function(newComment) {
                form.find('textarea[name="content"]').val('');

                if(window.router && typeof window.router.loadComments === 'function') {
                    window.router.loadComments(postId);
                } else {
                     console.error("loadComments not found");
                     uiCommon.showAlert('Comment posted! Refresh page to see updates.', 'success');
                }

                 if (parentId) {
                     form.closest('.reply-form-container').slideUp(function(){ $(this).empty(); });
                 }
            })
            .fail(function() { })
             .always(function() {
                 submitButton.prop('disabled', false).html(originalButtonText);
             });
    }

    function handleReplyButtonClick(event) {
         if (!auth.checkAuthStatus()) { window.router?.navigateTo('#login'); return; }
         const button = $(event.target).closest('.btn-reply');
         const commentDiv = button.closest('.comment');
         const commentId = commentDiv.data('comment-id');

         const postId = $('#comments-section #comment-form-main').data('post-id');
         const replyContainer = commentDiv.find('.reply-form-container').first();

         if (!postId) { console.error("Can't find post ID."); return; }
         if (!commentId) { console.error("Can't find comment ID."); return; }
         if (!replyContainer.length) { console.error("Can't find reply form."); return; }

         $('.reply-form-container').not(replyContainer).slideUp(function(){ $(this).empty(); });

         if (replyContainer.is(':visible')) {
              replyContainer.slideUp(function(){ $(this).empty(); });
         } else {
             const commentFormHtml = window.ui.comments?.renderCommentForm(postId, commentId) || '<p>Error loading reply form.</p>';
             replyContainer.html(commentFormHtml).slideDown();
             replyContainer.find('textarea').focus();
         }
    }

     function handleCancelReply(event) {
        $(event.target).closest('.reply-form-container').slideUp(function(){ $(this).empty(); });
    }

     function handleDeleteComment(event) {
        if (!auth.checkAuthStatus()) { window.router?.navigateTo('#login'); return; }
        const button = $(event.target).closest('.btn-delete-comment');
        const commentId = button.data('comment-id');
        const commentElement = button.closest('.comment');

        const postId = $('#comments-section #comment-form-main').data('post-id');

        if (!commentId) { console.error("Delete button missing comment ID"); return; }

        if (confirm('Are you sure you want to delete this comment?')) {
            button.prop('disabled', true); // Disable button
            api.request('DELETE', `/comments/${commentId}/`)
                .done(function() {
                    uiCommon.showAlert('Comment deleted.', 'success');

                    if(postId && window.router && typeof window.router.loadComments === 'function') {
                        window.router.loadComments(postId);
                    } else {
                        commentElement.fadeOut(300, function() { $(this).remove(); });
                         const countDetailSpan = $('#comment-count-detail');
                         if (countDetailSpan.length) {
                            const currentCount = parseInt(countDetailSpan.text()) || 0;
                            countDetailSpan.text(Math.max(0, currentCount - 1));
                         }
                    }
                })
                .fail(function() {
                    button.prop('disabled', false);
                    
                 });
        }
    }

    window.handlers.comments = {
        handleCommentSubmit: handleCommentSubmit,
        handleReplyButtonClick: handleReplyButtonClick,
        handleCancelReply: handleCancelReply,
        handleDeleteComment: handleDeleteComment
    };

}(window, jQuery, window.api, window.auth, window.ui.common));
