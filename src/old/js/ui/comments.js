
(function(window, $, uiCommon, auth) {

    window.ui = window.ui || {};

    function renderComments(commentsData, postId) {
        const commentsList = $('#comments-list');
        if (!commentsList.length) return;
        commentsList.empty();

        const comments = Array.isArray(commentsData) ? commentsData : (commentsData && commentsData.results);
        const count = Array.isArray(commentsData) ? commentsData.length : (commentsData ? commentsData.count : 0);

        if (comments && comments.length > 0) {
            const commentTree = buildCommentTree(comments);
            commentTree.forEach(comment => commentsList.append(renderComment(comment))); 
        } else {
            commentsList.html('<p>No comments yet. Be the first!</p>');
        }


        const countDetailSpan = $('#comment-count-detail');
        if(countDetailSpan.length) countDetailSpan.text(count);


         if (auth.getCurrentUser().token && $('#comments-section').find('#comment-form-main').length === 0) {
              $('#comments-section').append(renderCommentForm(postId));
         }
    }


    function buildCommentTree(comments) {
        const commentMap = {};
        const rootComments = [];

        comments.forEach(comment => {
            comment.children = [];
            commentMap[comment.id] = comment;

            if (comment.author && typeof comment.author !== 'object') {
                 comment.author = { username: comment.author, avatar_url: comment.author_avatar };
            } else if (!comment.author) {
                 comment.author = { username: 'Anonymous', avatar_url: null };
            }
        });


        comments.forEach(comment => {
            if (comment.parent && commentMap[comment.parent]) {

                commentMap[comment.parent].children.push(comment);
            } else {

                rootComments.push(comment);
            }
        });

        const sortByDateDesc = (a, b) => new Date(b.created_at) - new Date(a.created_at);

        rootComments.sort(sortByDateDesc);

        Object.values(commentMap).forEach(comment => comment.children.sort(sortByDateDesc));

        return rootComments;
    }


    function renderComment(comment) {
        const childrenHtml = comment.children.map(reply => renderComment(reply)).join('');


        const avatarUrl = comment.author?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(comment.author?.username || '?')}&background=random&size=32`;
        const canModify = auth.canEditOrDelete(comment);
        const commentContentHtml = uiCommon.sanitizeAndParseMarkdown(comment.content);
        const commentDate = comment.created_at ? new Date(comment.created_at).toLocaleString() : 'N/A';


        return `
            <div class="comment border-start ps-3 mb-3" data-comment-id="${comment.id}">
                <div class="d-flex align-items-start mb-1">
                    <img src="${avatarUrl}" alt="${comment.author?.username || 'User'}'s avatar" class="avatar-sm mt-1">
                    <div class="flex-grow-1 ps-2"> {/* Added padding start */}
                         <div class="comment-meta mb-1">
                             <strong class="me-2">${comment.author?.username || 'Anonymous'}</strong>
                             <small class="text-muted">${commentDate}</small>
                         </div>
                         <div class="comment-content-display">${commentContentHtml}</div>
                         <div class="comment-actions mt-1">
                             ${auth.getCurrentUser().token ? `<button class="btn btn-sm btn-link text-decoration-none p-0 me-2 btn-reply" data-comment-id="${comment.id}"><i class="bi bi-reply"></i> Reply</button>` : ''}
                              ${ canModify ? `
                               <button class="btn btn-sm btn-link text-danger text-decoration-none p-0 btn-delete-comment" data-comment-id="${comment.id}"><i class="bi bi-trash"></i> Delete</button>
                             ` : ''}
                         </div>
                         <div class="reply-form-container mt-2" style="display: none;"></div>
                    </div>
                </div>
                <div class="comment-replies ms-4 ps-2">
                    ${childrenHtml}
                </div>
            </div>
        `;
    }

     function renderCommentForm(postId, parentId = null) {
        const formId = parentId ? `reply-form-${parentId}` : 'comment-form-main';
        const placeholder = parentId ? 'Write your reply...' : 'Leave a comment...';
        const buttonText = parentId ? 'Post Reply' : 'Post Comment';
        return `
            <form id="${formId}" class="comment-form mt-3" data-post-id="${postId}" data-parent-id="${parentId || ''}">
                <div class="mb-2">
                    <textarea class="form-control" name="content" rows="3" placeholder="${placeholder}" required></textarea>
                </div>
                 <div class="d-flex justify-content-end">
                    ${parentId ? '<button type="button" class="btn btn-secondary btn-sm me-2 btn-cancel-reply">Cancel</button>' : ''}
                    <button type="submit" class="btn btn-primary btn-sm">${buttonText}</button>
                 </div>
            </form>
        `;
    }


    window.ui.comments = {
        renderComments: renderComments,
        renderComment: renderComment,
        buildCommentTree: buildCommentTree,
        renderCommentForm: renderCommentForm
    };

}(window, jQuery, window.ui.common, window.auth)); // Pass dependencies
