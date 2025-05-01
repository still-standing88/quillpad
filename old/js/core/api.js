
const API_BASE_URL = '/api';

export function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return token ? { 'Authorization': `Token ${token}` } : {};
}

export function apiRequest(method, endpoint, data = null, authenticated = true, isFormData = false) {
    const showAlert = window.ui?.common?.showAlert || window.alert;

    const headers = authenticated ? getAuthHeaders() : {};
    const ajaxOptions = {
        url: `${API_BASE_URL}${endpoint}`,
        method: method,
        headers: headers,
        dataType: 'json',
        timeout: 15000,
        error: function(jqXHR, textStatus, errorThrown) {

            let errorMsg = `Error: ${errorThrown || textStatus || 'Request Failed'}`;
             if (jqXHR.status) { errorMsg = `Error ${jqXHR.status}: ${errorThrown || jqXHR.statusText}`; }
             try {
                const responseJson = JSON.parse(jqXHR.responseText);
                if (typeof responseJson === 'object' && responseJson !== null) {
                    if (responseJson.detail) { errorMsg = responseJson.detail; }
                    else { errorMsg = Object.entries(responseJson).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; '); }
                } else if (typeof responseJson === 'string') { errorMsg = responseJson; }
            } catch (e) { if(jqXHR.responseText && jqXHR.responseText.length < 500) { errorMsg += ` | Server: ${jqXHR.responseText}`; } }
            showAlert(errorMsg, 'danger');
        }
    };

    if (data) {
        if (isFormData) {
            ajaxOptions.data = data;
            ajaxOptions.processData = false;
            ajaxOptions.contentType = false;
        } else {
            ajaxOptions.data = JSON.stringify(data);
            ajaxOptions.contentType = 'application/json; charset=utf-8';
        }
    }
    return window.$.ajax(ajaxOptions);
}
