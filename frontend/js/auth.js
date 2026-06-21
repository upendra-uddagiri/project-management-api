const AUTH = {
    getToken()         { return localStorage.getItem('access_token'); },
    setToken(t)        { localStorage.setItem('access_token', t); },
    getRefresh()       { return localStorage.getItem('refresh_token'); },
    setRefresh(t)      { localStorage.setItem('refresh_token', t); },
    getUser()          { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; },
    setUser(u)         { localStorage.setItem('user', JSON.stringify(u)); },

    logout() {
        localStorage.clear();
        window.location.href = 'index.html';
    },

    requireAuth() {
        if (!this.getToken()) {
            window.location.href = 'index.html';
            return false;
        }
        return true;
    },

    // Returns first two initials from a name
    initials(name) {
        if (!name) return '?';
        return name.trim().split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },

    // Populates sidebar user chip from stored user data
    populateSidebar() {
        const user = this.getUser();
        if (!user) return;
        const avatar = document.getElementById('sidebar-avatar');
        const name   = document.getElementById('sidebar-name');
        const role   = document.getElementById('sidebar-role');
        if (avatar) avatar.textContent = this.initials(user.full_name);
        if (name)   name.textContent   = user.full_name;
        if (role)   role.textContent   = user.role || 'member';
    }
};