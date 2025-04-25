
(function(window, $){

    window.ui = window.ui || {};
    window.handlers = window.handlers || {};

    const alertContainer = $('#alert-container');
    const contentArea = $('#content-area');

    function showAlert(message, type = 'info') {
        const alertId = `alert-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;

        alertContainer.prepend(alertHtml);

        // setTimeout(() => {
        //    $(`#${alertId}`).alert('close');
        // }, 5000);
    }

    function renderPagination(containerSelector, totalItems, limit, currentOffset, baseUrl) {
        const container = $(containerSelector);
        container.empty();
        if (totalItems <= limit) return;

        const totalPages = Math.ceil(totalItems / limit);
        const currentPage = Math.floor(currentOffset / limit) + 1;

        if (totalPages <= 1) return;

        let paginationHtml = '<nav aria-label="Page navigation"><ul class="pagination justify-content-center flex-wrap">';

        const maxPagesToShow = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

        startPage = Math.max(1, endPage - maxPagesToShow + 1);


        const prevDisabled = currentPage === 1 ? 'disabled' : '';
        const prevOffset = Math.max(0, currentOffset - limit);

        const prevBaseUrl = baseUrl.includes('?') ? baseUrl + '&' : baseUrl + '?';
        paginationHtml += `<li class="page-item ${prevDisabled}"><a class="page-link" href="${prevBaseUrl}offset=${prevOffset}" aria-label="Previous"><span aria-hidden="true">«</span></a></li>`;


         if (startPage > 1) {
            const firstPageBaseUrl = baseUrl.includes('?') ? baseUrl + '&' : baseUrl + '?';
             paginationHtml += `<li class="page-item"><a class="page-link" href="${firstPageBaseUrl}offset=0">1</a></li>`;
             if (startPage > 2) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
             }
         }

        for (let i = startPage; i <= endPage; i++) {
             const offset = (i - 1) * limit;
             const active = currentPage === i ? 'active' : '';
             const pageBaseUrl = baseUrl.includes('?') ? baseUrl + '&' : baseUrl + '?';
             paginationHtml += `<li class="page-item ${active}" ${active ? 'aria-current="page"' : ''}><a class="page-link" href="${pageBaseUrl}offset=${offset}">${i}</a></li>`;
        }


        if (endPage < totalPages) {
             if (endPage < totalPages - 1) {
                 paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
             }
             const lastPageOffset = (totalPages - 1) * limit;
             const lastPageBaseUrl = baseUrl.includes('?') ? baseUrl + '&' : baseUrl + '?';
            paginationHtml += `<li class="page-item"><a class="page-link" href="${lastPageBaseUrl}offset=${lastPageOffset}">${totalPages}</a></li>`;
        }


        const nextDisabled = currentPage === totalPages ? 'disabled' : '';
        const nextOffset = currentOffset + limit;
        const nextBaseUrl = baseUrl.includes('?') ? baseUrl + '&' : baseUrl + '?';
        paginationHtml += `<li class="page-item ${nextDisabled}"><a class="page-link" href="${nextBaseUrl}offset=${nextOffset}" aria-label="Next"><span aria-hidden="true">»</span></a></li>`;

        paginationHtml += '</ul></nav>';
        container.html(paginationHtml);
    }


    function sanitizeAndParseMarkdown(markdownString) {
        if (!markdownString) return '';
        try {
            if (typeof DOMPurify === 'undefined') {
                console.error("DOMPurify library is not loaded!");
                return "<p class='text-danger'>Error: Content sanitizer not available.</p>";
            }
            if (typeof marked === 'undefined') {
                 console.error("Marked library is not loaded!");
                return "<p class='text-danger'>Error: Content parser not available.</p>";
            }

             marked.setOptions({ gfm: true, breaks: true });

            const dirtyHtml = marked.parse(markdownString);

            const cleanHtml = DOMPurify.sanitize(dirtyHtml, {
                USE_PROFILES: { html: true },
                // ADD_ATTR: ['target'],
            });
            return cleanHtml;
        } catch (e) {
            console.error("Error processing Markdown content:", e);
            return "<p class='text-danger'>Error displaying content.</p>";
        }
    }


    window.ui.common = {
        showAlert: showAlert,
        renderPagination: renderPagination,
        sanitizeAndParseMarkdown: sanitizeAndParseMarkdown,
        contentArea: contentArea,
        alertContainer: alertContainer
    };

}(window, jQuery));
