
import $ from 'jquery';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

const alertContainer = $('#alert-container');
const contentArea = $('#content-area');

export function showAlert(message, type = 'info') {
    const alertId = `alert-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
    alertContainer.prepend(alertHtml);
}

export function renderPagination(containerSelector, totalItems, limit, currentOffset, baseUrl) {
    const container = $(containerSelector);
    container.empty();
    if (totalItems <= limit) return;
    const totalPages = Math.ceil(totalItems / limit);
    const currentPage = Math.floor(currentOffset / limit) + 1;
    if (totalPages <= 1) return;
    let paginationHtml = '<nav><ul class="pagination justify-content-center flex-wrap">';
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
    startPage = Math.max(1, endPage - maxPagesToShow + 1);
    const prevDisabled = currentPage === 1 ? 'disabled' : '';
    const prevOffset = Math.max(0, currentOffset - limit);
    const prevLink = `${baseUrl.split('?')[0]}?offset=${prevOffset}`;
    paginationHtml += `<li class="page-item ${prevDisabled}"><a class="page-link" href="${prevLink}">«</a></li>`;
     if (startPage > 1) { const firstLink = `${baseUrl.split('?')[0]}?offset=0`; paginationHtml += `<li class="page-item"><a class="page-link" href="${firstLink}">1</a></li>`; if (startPage > 2) { paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`; } }
    for (let i = startPage; i <= endPage; i++) { const offset = (i - 1) * limit; const active = currentPage === i ? 'active' : ''; const pageLink = `${baseUrl.split('?')[0]}?offset=${offset}`; paginationHtml += `<li class="page-item ${active}" ${active ? 'aria-current="page"' : ''}><a class="page-link" href="${pageLink}">${i}</a></li>`; }
    if (endPage < totalPages) { if (endPage < totalPages - 1) { paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`; } const lastPageOffset = (totalPages - 1) * limit; const lastLink = `${baseUrl.split('?')[0]}?offset=${lastPageOffset}`; paginationHtml += `<li class="page-item"><a class="page-link" href="${lastLink}">${totalPages}</a></li>`; }
    const nextDisabled = currentPage === totalPages ? 'disabled' : '';
    const nextOffset = currentOffset + limit;
    const nextLink = `${baseUrl.split('?')[0]}?offset=${nextOffset}`;
    paginationHtml += `<li class="page-item ${nextDisabled}"><a class="page-link" href="${nextLink}">»</a></li>`;
    paginationHtml += '</ul></nav>';
    container.html(paginationHtml);
}

export function sanitizeAndParseMarkdown(markdownString) {
    if (!markdownString) return '';
    try {
        const dirtyHtml = marked.parse(markdownString);
        const cleanHtml = DOMPurify.sanitize(dirtyHtml, { USE_PROFILES: { html: true } });
        return cleanHtml;
    } catch (e) {
        console.error("Markdown error:", e);
        return "<p class='text-danger'>Error</p>";
    }
}

export { contentArea, alertContainer };
