/**
 * Admin Authentication Manager
 */

class AdminAuth {
    constructor() {
        this.token = localStorage.getItem('admin_token');
        this.user = JSON.parse(localStorage.getItem('admin_user') || 'null');
    }

    /**
     * تسجيل دخول المدير
     */
    async login(username, password) {
        try {
            // Use global API_BASE from config.js
            const API_BASE = window.API_BASE || 'http://localhost:8000/api';
            const response = await fetch(`${API_BASE}/admin-panel/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'فشل تسجيل الدخول');
            }

            // حفظ البيانات
            this.token = data.tokens.access;
            this.user = data.user;
            localStorage.setItem('admin_token', this.token);
            localStorage.setItem('admin_user', JSON.stringify(this.user));

            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    /**
     * تسجيل الخروج
     */
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        window.location.href = '/admin/';
    }

    /**
     * التحقق من تسجيل الدخول
     */
    isAuthenticated() {
        return !!this.token && this.user && this.user.is_superuser;
    }

    /**
     * حماية الصفحة - إعادة توجيه إذا لم يكن مسجلاً
     */
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/admin/';
            return false;
        }
        return true;
    }

    /**
     * الحصول على التوكن
     */
    getToken() {
        return this.token;
    }

    /**
     * الحصول على معلومات المستخدم
     */
    getUser() {
        return this.user;
    }
}

// إنشاء instance عام
const adminAuth = new AdminAuth();
