
import $ from 'jquery';
import * as uiCommon from './common.js';
import * as auth from '../core/auth.js';

export function renderComments(commentsData, postId) {
    const commentsList = $('#comments-list');
    if (!commentsList.length) return;
    commentsList.empty();
    const comments = Array.isArray(commentsData) ? commentsData : (commentsData?.results);
    const count = Array.isArray(commentsData) ? commentsData.length : (commentsData?.count ?? 0);
    if (comments?.length) { const commentTree = buildCommentTree(comments); commentTree.forEach(c => commentsList.append(renderComment(c))); }
    else { commentsList.html('<p>No comments yet.</p>'); }
    const countSpan = $('#comment-count-detail');
    if(countSpan.length) countSpan.text(count);
    if (auth.getCurrentUser().token && !$('#comments-section #comment-form-main').length) { $('#comments-section').append(renderCommentForm(postId)); }
}

function buildCommentTree(comments) {
    const map = {}; const roots = [];
    comments.forEach(c => { c.children = []; map[c.id] = c; if (c.author && typeof c.author!=='object') { c.author = { username: c.author, avatar_url: c.author_avatar }; } else if (!c.author) { c.author = { username: '?', avatar_url: null }; } });
    comments.forEach(c => { if (c.parent && map[c.parent]) { map[c.parent].children.push(c); } else { roots.push(c); } });
    const sortFn = (a,b) => new Date(b.created_at)-new Date(a.created_at); roots.sort(sortFn); Object.values(map).forEach(c => c.children.sort(sortFn));
    return roots;
}

function renderComment(comment) {
    const childrenHtml = comment.children.map(reply => renderComment(reply)).join('');
    const avatar = comment.author?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(comment.author?.username || '?')}&size=32`;
    const canModify = auth.canEditOrDelete(comment);
    const contentHtml = uiCommon.sanitizeAndParseMarkdown(comment.content);
    const date = comment.created_at ? new Date(comment.created_at).toLocaleString() : '';
    return ` <div class="comment border-start ps-3 mb-3" data-comment-id="${comment.id}"> <div class="d-flex align-items-start mb-1"> <img src="${avatar}" alt="${comment.author?.username}'s avatar" class="avatar-sm mt-1"> <div class="flex-grow-1 ps-2"> <div class="comment-meta mb-1"> <strong class="me-2">${comment.author?.username||'?'}</strong> <small class="text-muted">${date}</small> </div> <div class="comment-content-display">${contentHtml}</div> <div class="comment-actions mt-1"> ${auth.getCurrentUser().token ? `<button class="btn btn-sm btn-link text-decoration-none p-0 me-2 btn-reply" data-comment-id="${comment.id}"><i class="bi bi-reply"></i> Reply</button>` : ''} ${ canModify ? `<button class="btn btn-sm btn-link text-danger text-decoration-none p-0 btn-delete-comment" data-comment-id="${comment.id}"><i class="bi bi-trash"></i> Delete</button>` : ''} </div> <div class="reply-form-container mt-2" style="display: none;"></div> </div> </div> <div class="comment-replies ms-4 ps-2">${childrenHtml}</div> </div> `;
}

export function renderCommentForm(postId, parentId = null) {
    const formId = parentId ? `reply-form-${parentId}` : 'comment-form-main';
    const placeholder = parentId ? 'Write reply...' : 'Leave comment...';
    const btnText = parentId ? 'Reply' : 'Post';
    return ` <form id="${formId}" class="comment-form mt-3" data-post-id="${postId}" data-parent-id="${parentId || ''}"> <div class="mb-2"> <textarea class="form-control" name="content" rows="3" placeholder="${placeholder}" required></textarea> </div> <div class="d-flex justify-content-end"> ${parentId ? '<button type="button" class="btn btn-secondary btn-sm me-2 btn-cancel-reply">Cancel</button>' : ''} <button type="submit" class="btn btn-primary btn-sm">${btnText}</button> </div> </form> `;
}
