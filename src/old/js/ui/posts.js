
(function(window, $, uiCommon, auth) { // Depends on uiCommon, auth

    window.ui = window.ui || {}; // Ensure base object exists

    function renderPostList(posts, title = "Posts") {
         uiCommon.contentArea.html(`<h2>${title}</h2><div id="post-list" class="mb-3">Loading...</div><div id="pagination-controls"></div>`);
         const postListContainer = $('#post-list');
         if (posts && posts.length > 0) {
             postListContainer.empty();
             posts.forEach(post => postListContainer.append(renderPostSummary(post))); // Uses renderPostSummary from this module
         } else {
             postListContainer.html('<p>No posts found.</p>');
         }
         checkAllLikeSaveStatus(posts.map(p=>p.slug)); // Uses checkAllLikeSaveStatus from this module
         // Pagination is rendered by the caller (router) using uiCommon.renderPagination
     }

     function renderPostSummary(post) {
         const summaryLength = 200;
         let excerpt = '';
         if (post.content) {
             const cleanHtml = uiCommon.sanitizeAndParseMarkdown(post.content);
             const tempDiv = $('<div>').html(cleanHtml);
             const textContent = tempDiv.text();
             excerpt = textContent.length > summaryLength ? textContent.substring(0, summaryLength) + '...' : textContent;
         }

        const canModify = auth.canEditOrDelete(post);
        const postDate = post.created_at ? new Date(post.created_at).toLocaleDateString() : 'N/A';

        return `
            <div class="card post-summary mb-4" data-slug="${post.slug}">
                 ${post.featured_image_url ? `<a href="#posts/${post.slug}"><img src="${post.featured_image_url}" class="card-img-top" alt="${post.title}" style="max-height: 250px; object-fit: cover;"></a>` : ''}
                <div class="card-body">
                    <h3 class="card-title mb-1"><a href="#posts/${post.slug}" class="text-decoration-none">${post.title || 'Untitled Post'}</a></h3>
                    <p class="post-meta card-subtitle mb-2 text-muted">
                        <i class="bi bi-person"></i> <a href="#posts/by_user/${post.author}" class="text-muted text-decoration-none">${post.author || 'Unknown Author'}</a>
                        <i class="bi bi-calendar-event ms-2"></i> ${postDate}
                        ${post.category ? `<i class="bi bi-folder ms-2"></i> <a href="#posts/by_category/${post.category}" class="text-muted text-decoration-none">${post.category}</a>` : ''}
                         <br class="d-sm-none">
                         <span class="ms-sm-2"><i class="bi bi-chat-dots"></i> ${post.comment_count !== undefined ? post.comment_count : 'N/A'}</span>
                         <span class="ms-2"><i class="bi bi-eye"></i> ${post.view_count !== undefined ? post.view_count : 'N/A'}</span>
                         <span class="ms-2"><i class="bi bi-hand-thumbs-up"></i> <span class="like-count">${post.likes?.length || 0}</span></span>
                    </p>
                    <p class="card-text">${excerpt || 'No content preview available.'}</p>
                    <div class="mb-2">
                        ${post.tags && post.tags.length > 0 ? '<i class="bi bi-tags me-1"></i>' : ''}
                        ${(post.tags || []).map(tag => `<a href="#posts/by_tag/${tag}" class="tag">${tag}</a>`).join('')}
                    </div>
                     <a href="#posts/${post.slug}" class="btn btn-sm btn-outline-primary mt-1"><i class="bi bi-book me-1"></i>Read More</a>
                     ${auth.getCurrentUser().token ? `
                         <button class="btn btn-sm btn-outline-danger mt-1 btn-like" data-slug="${post.slug}" data-liked="false"><i class="bi bi-heart"></i><i class="bi bi-heart-fill"></i> Like</button>
                         <button class="btn btn-sm btn-outline-success mt-1 btn-save" data-slug="${post.slug}" data-saved="false"><i class="bi bi-bookmark"></i><i class="bi bi-bookmark-fill"></i> Save</button>
                     ` : ''}
                     ${ canModify ? `
                        <a href="#edit-post/${post.slug}" class="btn btn-sm btn-outline-warning mt-1"><i class="bi bi-pencil"></i> Edit</a>
                        <button class="btn btn-sm btn-outline-danger mt-1 btn-delete-post" data-slug="${post.slug}"><i class="bi bi-trash"></i> Delete</button>
                     ` : ''}
                </div>
            </div>`;
    }

     function renderFullPost(post) {
        const canModify = auth.canEditOrDelete(post);
        const postContentHtml = uiCommon.sanitizeAndParseMarkdown(post.content);
        const postDate = post.created_at ? new Date(post.created_at).toLocaleDateString() : 'N/A';
        // Ensure window.ui.comments exists before calling renderCommentForm
        const commentFormHtml = window.ui && window.ui.comments ? window.ui.comments.renderCommentForm(post.id) : '<p>Error loading comment form.</p>';

        const postHtml = `
            <article class="card">
              <div class="card-body">
                ${post.featured_image_url ? `<img src="${post.featured_image_url}" class="img-fluid rounded mb-3 mx-auto d-block" alt="${post.title}" style="max-height: 400px;">` : ''}
                <h1 class="card-title">${post.title || 'Untitled Post'}</h1>
                <p class="post-meta text-muted mb-3">
                        <i class="bi bi-person"></i> <a href="#posts/by_user/${post.author}" class="text-muted text-decoration-none">${post.author || 'Unknown Author'}</a>
                        <i class="bi bi-calendar-event ms-2"></i> ${postDate}
                        ${post.category ? `<i class="bi bi-folder ms-2"></i> <a href="#posts/by_category/${post.category}" class="text-muted text-decoration-none">${post.category}</a>` : ''}
                         <br>
                         <span class="ms-0"><i class="bi bi-chat-dots"></i> <span id="comment-count-detail">${post.comment_count !== undefined ? post.comment_count : 'N/A'}</span> comments</span>
                         <span class="ms-2"><i class="bi bi-eye"></i> ${post.view_count !== undefined ? post.view_count : 'N/A'} views</span>
                         <span class="ms-2"><i class="bi bi-hand-thumbs-up"></i> <span id="like-count">${post.likes?.length || 0}</span> Likes</span>
                </p>

                <div id="post-content" class="mb-4">${postContentHtml}</div>

                 <div class="mb-3">
                     ${post.tags && post.tags.length > 0 ? '<i class="bi bi-tags me-1"></i>' : ''}
                     ${(post.tags || []).map(tag => `<a href="#posts/by_tag/${tag}" class="tag">${tag}</a>`).join('')}
                 </div>

                 <div class="d-flex flex-wrap gap-2 border-top pt-3">
                     ${auth.getCurrentUser().token ? `
                         <button class="btn btn-outline-danger btn-like" data-slug="${post.slug}" data-liked="false"><i class="bi bi-heart"></i><i class="bi bi-heart-fill"></i> Like</button>
                         <button class="btn btn-outline-success btn-save" data-slug="${post.slug}" data-saved="false"><i class="bi bi-bookmark"></i><i class="bi bi-bookmark-fill"></i> Save</button>
                     ` : ''}
                     ${ canModify ? `
                         <a href="#edit-post/${post.slug}" class="btn btn-warning"><i class="bi bi-pencil"></i> Edit Post</a>
                         <button class="btn btn-danger btn-delete-post" data-slug="${post.slug}"><i class="bi bi-trash"></i> Delete Post</button>
                     ` : ''}
                      <a href="#/" class="btn btn-secondary ms-auto"><i class="bi bi-arrow-left"></i> Back to posts</a>
                 </div>
                </div>
            </article>
            <hr>
            <section id="comments-section" class="mt-4">
                <h3>Comments</h3>
                <div id="comments-list" class="mb-4">Loading comments...</div>
                ${auth.getCurrentUser().token ? commentFormHtml : '<p><a href="#login">Log in</a> or <a href="#register">register</a> to leave a comment.</p>'}
            </section>
        `;
        uiCommon.contentArea.html(postHtml);
        checkAllLikeSaveStatus([post.slug]); // Use checkAllLikeSaveStatus from this module
    }

    function updateLikeButton(slug, liked, likeCount) {
        const button = $(`.btn-like[data-slug="${slug}"]`);
        if (button.length === 0) return;
        button.toggleClass('liked', liked);
        button.data('liked', liked);

        const likeCountSpan = button.closest('.card-body, .pt-3').find('.like-count, #like-count');
        if(likeCountSpan.length) likeCountSpan.text(likeCount);
    }

    function updateSaveButton(slug, saved) {
        const button = $(`.btn-save[data-slug="${slug}"]`);
         if (button.length === 0) return;
        button.toggleClass('saved', saved);
         button.data('saved', saved);
    }

     function checkAllLikeSaveStatus(postSlugs) {
         if (!auth.getCurrentUser().token || !postSlugs || postSlugs.length === 0) return;

         // Depends on window.api being loaded
         if (!window.api) {
            console.error("API module not loaded for checkAllLikeSaveStatus");
            return;
         }

         window.api.request('GET', '/posts/saved/?limit=1000')
             .done(savedData => {
                 const savedResults = savedData.results || savedData || [];
                 const savedSlugsSet = new Set(savedResults.map(p => p.slug));
                 postSlugs.forEach(slug => {
                     const isSaved = savedSlugsSet.has(slug);
                     updateSaveButton(slug, isSaved); // Use updateSaveButton from this module
                 });
             }).fail(err => {
                 console.error("Failed to fetch saved posts for status check:", err);
             });
     }

     // Assumed to be called from init.js or similar
     function renderFooter(recentPosts, popularTags, stats) {
        const recentList = $('#footer-recent-posts');
        const tagsList = $('#footer-popular-tags');
        const statsList = $('#footer-site-stats');

        recentList.empty();
        if (recentPosts && recentPosts.length > 0) {
             recentPosts.forEach(post => recentList.append(`<li><a href="#posts/${post.slug}" class="text-decoration-none text-muted">${post.title}</a></li>`));
        } else {
             recentList.html('<li class="text-muted small">No recent posts.</li>');
        }

        tagsList.empty();
         if (popularTags && popularTags.length > 0) {
              popularTags.forEach(tag => tagsList.append(`<a href="#posts/by_tag/${tag.name}" class="tag me-1 mb-1">${tag.name} (${tag.post_count})</a> `));
         } else {
              tagsList.html('<li class="text-muted small">No popular tags.</li>');
         }

        statsList.empty();
        if (stats) {
             statsList.append(`<li class="text-muted"><i class="bi bi-file-earmark-text me-1"></i> Posts: ${stats.total_posts || 0} (${stats.published_posts || 0} published)</li>`);
             statsList.append(`<li class="text-muted"><i class="bi bi-chat-dots me-1"></i> Comments: ${stats.total_comments || 0}</li>`);
             statsList.append(`<li class="text-muted"><i class="bi bi-folder me-1"></i> Categories: ${stats.total_categories || 0}</li>`);
             statsList.append(`<li class="text-muted"><i class="bi bi-tags me-1"></i> Tags: ${stats.total_tags || 0}</li>`);
        } else {
              statsList.html('<li class="text-muted small">Stats unavailable.</li>');
        }
    }

    // Add functions to the global ui object
    window.ui.posts = {
        renderPostList: renderPostList,
        renderPostSummary: renderPostSummary,
        renderFullPost: renderFullPost,
        updateLikeButton: updateLikeButton,
        updateSaveButton: updateSaveButton,
        checkAllLikeSaveStatus: checkAllLikeSaveStatus,
        renderFooter: renderFooter // Moved here for now
    };

}(window, jQuery, window.ui.common, window.auth)); // Pass dependencies
