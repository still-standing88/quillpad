
const API_BASE_URL = 'http://localhost:8000/api';

function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return token ? { 'Authorization': `Token ${token}` } : {};
}

function apiRequest(method, endpoint, data = null, authenticated = true, isFormData = false) {
    const headers = authenticated ? getAuthHeaders() : {};
    const ajaxOptions = {
        url: `${API_BASE_URL}${endpoint}`,
        method: method,
        headers: headers,
        dataType: 'json',
        timeout: 15000,
        error: function(jqXHR, textStatus, errorThrown) {
            console.error(`API Error (${jqXHR.status} ${textStatus}): ${method} ${endpoint}`, jqXHR.responseText, errorThrown);
            let errorMsg = `Error: ${errorThrown || textStatus || 'Request Failed'}`;
            if (jqXHR.status) {
                errorMsg = `Error ${jqXHR.status}: ${errorThrown || jqXHR.statusText}`;
            }

             try {
                const responseJson = JSON.parse(jqXHR.responseText);
                if (typeof responseJson === 'object' && responseJson !== null) {
                    if (responseJson.detail) {
                         errorMsg = responseJson.detail;
                    } else {
                        errorMsg = Object.entries(responseJson)
                            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                            .join('; ');
                    }
                } else if (typeof responseJson === 'string') {
                    errorMsg = responseJson;
                }
            } catch (e) {
                 if(jqXHR.responseText && jqXHR.responseText.length < 500) {
                    errorMsg += ` | Server Response: ${jqXHR.responseText}`;
                 }
            }

            if (window.ui && window.ui.common && typeof window.ui.common.showAlert === 'function') {
                 window.ui.common.showAlert(errorMsg, 'danger');
            } else {
                 console.error("UI not ready:", errorMsg);
                 alert(errorMsg);
            }
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

    return $.ajax(ajaxOptions);
}

window.api = {
    request: apiRequest,
    getAuthHeaders: getAuthHeaders,
    BASE_URL: API_BASE_URL
};
