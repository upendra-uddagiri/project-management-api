const BASE = 'http://localhost:8000';

const API = {

    // ── Core request helper ──────────────────────────────────────────────
    async req(method, path, body = null) {
        const opts = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${AUTH.getToken()}`
            }
        };
        if (body) opts.body = JSON.stringify(body);

        const res = await fetch(`${BASE}${path}`, opts);

        if (res.status === 401) { AUTH.logout(); return; }
        if (res.status === 204) return null;

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Something went wrong');
        return data;
    },

    // ── Auth ─────────────────────────────────────────────────────────────
    async register(fullName, email, password) {
        const res = await fetch(`${BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullName, email, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Registration failed');
        return data;
    },

    async login(email, password) {
        const form = new FormData();
        form.append('username', email);
        form.append('password', password);
        const res = await fetch(`${BASE}/auth/login`, { method: 'POST', body: form });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Login failed');
        return data;
    },

    // ── Users ─────────────────────────────────────────────────────────────
    async getMe()         { return this.req('GET',   '/users/me'); },
    async updateMe(data)  { return this.req('PATCH', '/users/me', data); },

    // ── Projects ──────────────────────────────────────────────────────────
    async getProjects(page = 1, pageSize = 20) {
        return this.req('GET', `/projects/?page=${page}&page_size=${pageSize}`);
    },
    async getProject(id)        { return this.req('GET',    `/projects/${id}`); },
    async createProject(data)   { return this.req('POST',   '/projects/', data); },
    async updateProject(id, d)  { return this.req('PATCH',  `/projects/${id}`, d); },
    async deleteProject(id)     { return this.req('DELETE', `/projects/${id}`); },
    async addMember(pid, uid, role = 'member') {
        return this.req('POST', `/projects/${pid}/members`, { user_id: uid, role });
    },
    async removeMember(pid, uid) {
        return this.req('DELETE', `/projects/${pid}/members/${uid}`);
    },

    // ── Tasks ─────────────────────────────────────────────────────────────
    async getTasks(pid, filters = {}) {
        const qs = new URLSearchParams(
            Object.fromEntries(Object.entries(filters).filter(([,v]) => v))
        ).toString();
        return this.req('GET', `/projects/${pid}/tasks${qs ? '?' + qs : ''}`);
    },
    async getTask(id)          { return this.req('GET',    `/tasks/${id}`); },
    async createTask(pid, d)   { return this.req('POST',   `/projects/${pid}/tasks`, d); },
    async updateTask(id, d)    { return this.req('PATCH',  `/tasks/${id}`, d); },
    async deleteTask(id)       { return this.req('DELETE', `/tasks/${id}`); },
    async assignTask(id, uid)  { return this.req('POST',   `/tasks/${id}/assign`, { assignee_id: uid }); },

    async uploadAttachment(taskId, file) {
        const form = new FormData();
        form.append('file', file);
        const res = await fetch(`${BASE}/tasks/${taskId}/attachments`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${AUTH.getToken()}` },
            body: form
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Upload failed');
        return data;
    },

    // ── Comments ──────────────────────────────────────────────────────────
    async getComments(tid)          { return this.req('GET',    `/tasks/${tid}/comments`); },
    async createComment(tid, text)  { return this.req('POST',   `/tasks/${tid}/comments`, { content: text }); },
    async deleteComment(id)         { return this.req('DELETE', `/comments/${id}`); },
};

// ── UI helpers ────────────────────────────────────────────────────────────────

function showAlert(id, message, type = 'error') {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent  = message;
    el.className    = `alert alert-${type} show`;
    setTimeout(() => el.classList.remove('show'), 4000);
}

function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

function statusBadge(status) {
    const labels = { todo:'To Do', in_progress:'In Progress', in_review:'In Review', done:'Done',
                     active:'Active', archived:'Archived', completed:'Completed' };
    return `<span class="badge badge-${status}">${labels[status] || status}</span>`;
}

function fmtDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' });
}

function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    btn.disabled    = loading;
    btn.textContent = loading ? 'Loading…' : btn.dataset.label;
}