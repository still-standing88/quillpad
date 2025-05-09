import $ from 'jquery';
import { apiRequest } from '../core/api.js';
import * as auth from '../core/auth.js';
import { showAlert } from '../ui/common.js';
import { renderCategoryForm } from '../ui/forms.js';
import { loadCategoryAdmin, navigateTo } from '../router.js';

export function handleCategorySubmit(event) { event.preventDefault(); if (!auth.isAdmin()) return; const form = $(event.target); const id = form.data('id'); const name = form.find('#category-name').val(); const isEdit = !!id; const method = isEdit ? 'PUT' : 'POST'; const endpoint = isEdit ? `/categories/${id}/` : '/categories/'; if (!name.trim()) { showAlert('Name required.', 'warning'); return; } const btn = form.find('button[type="submit"]'); const btnTxt = btn.html(); btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Saving...'); const payload = { name: name }; apiRequest(method, endpoint, payload).done(cat => { showAlert(`Category ${isEdit ? 'updated' : 'created'}.`, 'success'); form.parent().slideUp(function(){ $(this).empty().html(renderCategoryForm()).hide(); }); loadCategoryAdmin(); }).fail(() => {}).always(() => btn.prop('disabled', false).html(btnTxt)); }
export function handleEditCategoryClick(event) { if (!auth.isAdmin()) return; const btn = $(event.target).closest('button'); const id = btn.data('id'); const row = btn.closest('tr'); const name = row.find('.cat-name').text(); const slug = row.find('.cat-slug').text(); const formCont = $('#category-form-container'); const formHtml = renderCategoryForm({ id, name, slug }); formCont.html(formHtml).slideDown().find('#category-name').focus(); }
export function handleDeleteCategory(event) { if (!auth.isAdmin()) return; const btn = $(event.target).closest('button'); const id = btn.data('id'); const row = btn.closest('tr'); const name = row.find('.cat-name').text(); if (!id) return; if (confirm(`Delete category "${name}"?`)) { btn.prop('disabled', true); apiRequest('DELETE', `/categories/${id}/`).done(() => { showAlert(`Category "${name}" deleted.`, 'success'); loadCategoryAdmin(); }).fail(() => btn.prop('disabled', false)); } }

export function handleAdminUserUpdate(event) {
    event.preventDefault();
    if (!auth.isAdmin()) return;

    const form = $(event.target);
    const userId = form.data('user-id');
    if (!userId) {
        showAlert('Cannot determine user ID.', 'danger');
        return;
    }

    const updatedData = {
        username: $('#user-username').val(),
        email: $('#user-email').val(),
        first_name: $('#user-first-name').val(),
        last_name: $('#user-last-name').val(),
        bio: $('#user-bio').val(),
        role: $('#user-role').val(),
        is_staff: $('#user-is-staff').is(':checked'),
        is_active: $('#user-is-active').is(':checked'),
    };

    const btn = form.find('button[type="submit"]');
    const btnTxt = btn.html();
    btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Saving...');

    apiRequest('PATCH', `/users/${userId}/`, updatedData)
        .done(updatedUser => {
            showAlert(`User ${updatedUser.username} updated successfully.`, 'success');
            navigateTo('#admin/users');
        })
        .fail(() => {})
        .always(() => {
            btn.prop('disabled', false).html(btnTxt);
        });
}