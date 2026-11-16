// DataGuard AI API Client Wrapper
const API_BASE = '/api';

class DataGuardAPI {
    static getToken() {
        return localStorage.getItem('dataguard_token') || localStorage.getItem('accura_token') || '';
    }

    static setToken(token) {
        localStorage.setItem('dataguard_token', token);
    }

    static getHeaders(isJson = true) {
        const headers = {};
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        if (isJson) {
            headers['Content-Type'] = 'application/json';
        }
        return headers;
    }

    // AUTH
    static async switchDemoRole(role) {
        const res = await fetch(`${API_BASE}/auth/demo-switch/${role}`, { method: 'POST' });
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        this.setToken(data.access_token);
        return data;
    }

    static async getMe() {
        const res = await fetch(`${API_BASE}/auth/me`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // TEMPLATES
    static async getTemplates(status = null) {
        let url = `${API_BASE}/templates`;
        if (status) url += `?status=${encodeURIComponent(status)}`;
        const res = await fetch(url, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async getTemplateDetail(id) {
        const res = await fetch(`${API_BASE}/templates/${id}`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async createTemplate(payload) {
        const res = await fetch(`${API_BASE}/templates`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async updateTemplateStatus(id, status) {
        const res = await fetch(`${API_BASE}/templates/${id}/status`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify({ status })
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // RULES & AI GENERATOR
    static async getRules(dataType = null) {
        let url = `${API_BASE}/rules`;
        if (dataType) url += `?data_type=${encodeURIComponent(dataType)}`;
        const res = await fetch(url, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async generateRuleWithAI(payload) {
        const res = await fetch(`${API_BASE}/rules/generate`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async createRule(payload) {
        const res = await fetch(`${API_BASE}/rules`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async assignRule(columnId, ruleId) {
        const res = await fetch(`${API_BASE}/rules/assign`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ column_id: columnId, rule_id: ruleId })
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // UPLOAD & VALIDATE
    static async validateDataset(templateId, file) {
        const formData = new FormData();
        formData.append('template_id', templateId);
        formData.append('file', file);

        const res = await fetch(`${API_BASE}/upload/validate`, {
            method: 'POST',
            headers: this.getHeaders(false),
            body: formData
        });
        if (!res.ok) {
            const errData = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(errData.detail || 'Validation failed');
        }
        return await res.json();
    }

    static async getSampleDataset(sampleKey) {
        const res = await fetch(`${API_BASE}/upload/sample/${sampleKey}`);
        if (!res.ok) throw new Error("Failed to load sample dataset");
        const blob = await res.blob();
        const templateName = res.headers.get("X-Template-Name") || "Plantilla_polizas";
        let filename = `${sampleKey}.xlsx`;
        const disp = res.headers.get("Content-Disposition");
        if (disp && disp.includes("filename=")) {
            filename = disp.split("filename=")[1].replace(/["']/g, "").trim();
        }
        return { blob, filename, templateName };
    }


    // HISTORY
    static async getHistory(limit = 100) {
        const res = await fetch(`${API_BASE}/history?limit=${limit}`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async getLoadDetail(loadId) {
        const res = await fetch(`${API_BASE}/history/${loadId}?limit=500`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // PERMISSIONS
    static async getTemplatePermissions(templateId) {
        const res = await fetch(`${API_BASE}/permissions/template/${templateId}`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async assignPermissions(templateId, userIds) {
        const res = await fetch(`${API_BASE}/permissions/assign`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ template_id: templateId, user_ids: userIds })
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // USERS
    static async getUsers() {
        const res = await fetch(`${API_BASE}/users`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async toggleUserStatus(userId) {
        const res = await fetch(`${API_BASE}/users/${userId}/status`, {
            method: 'PATCH',
            headers: this.getHeaders()
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // BENCHMARK (Paper Results)
    static async getBenchmarkMetrics() {
        const res = await fetch(`${API_BASE}/benchmark/metrics`);
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    // AUDIT & NOTIFICATIONS
    static async getNotifications() {
        const res = await fetch(`${API_BASE}/audit/notifications`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }

    static async markNotificationRead(id) {
        await fetch(`${API_BASE}/audit/notifications/${id}/read`, {
            method: 'POST',
            headers: this.getHeaders()
        });
    }

    static async getAuditLogs() {
        const res = await fetch(`${API_BASE}/audit/logs`, { headers: this.getHeaders() });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    }
}

// Alias for base paper compatibility
const AccuraAPI = DataGuardAPI;

