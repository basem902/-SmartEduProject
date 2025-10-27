/**
 * Admin API Manager
 */

class AdminAPI {
    constructor() {
        // Use global API_BASE from config.js
        const API_BASE = window.API_BASE || 'http://localhost:8000/api';
        this.baseURL = `${API_BASE}/admin-panel`;
        console.log('🔧 AdminAPI initialized with baseURL:', this.baseURL);
    }

    /**
     * عمل request مع التوكن
     */
    async request(endpoint, options = {}) {
        const token = adminAuth.getToken();
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            // معالجة 401 Unauthorized
            if (response.status === 401) {
                alert('انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى.');
                adminAuth.logout();
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.message || 'حدث خطأ');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * الحصول على قائمة الجداول
     */
    async getTables() {
        return this.request('/tables/');
    }

    /**
     * الحصول على بيانات جدول محدد
     */
    async getTableData(tableName, limit = 100, offset = 0) {
        return this.request(`/tables/${tableName}/data/?limit=${limit}&offset=${offset}`);
    }

    /**
     * حذف جميع بيانات جدول
     */
    async truncateTable(tableName) {
        return this.request(`/tables/${tableName}/truncate/`, {
            method: 'DELETE',
            body: JSON.stringify({ confirm: 'DELETE' })
        });
    }

    /**
     * حذف سجل واحد من جدول
     */
    async deleteRow(tableName, rowId) {
        return this.request(`/tables/${tableName}/row/${rowId}/`, {
            method: 'DELETE'
        });
    }

    /**
     * تصفير عداد الجدول
     */
    async resetSequence(tableName) {
        return this.request(`/tables/${tableName}/reset-sequence/`, {
            method: 'POST'
        });
    }

    /**
     * الحصول على الإحصائيات
     */
    async getStatistics() {
        return this.request('/database/stats/');
    }

    /**
     * حذف جميع البيانات (خطير جداً!)
     */
    async wipeAllData(password) {
        return this.request('/database/wipe/', {
            method: 'DELETE',
            body: JSON.stringify({
                confirm: 'DELETE ALL DATA',
                password: password
            })
        });
    }

    /**
     * حذف بيانات الشُعب والتيليجرام للمعلم (مع الاحتفاظ ببيانات المعلم)
     */
    async deleteTeacherSections(teacherId) {
        return this.request(`/teacher/${teacherId}/delete-sections/`, {
            method: 'DELETE'
        });
    }

    /**
     * الحصول على قائمة المعلمين
     */
    async getTeachers() {
        return this.request('/tables/teachers/data/?limit=1000');
    }
}

// إنشاء instance عام
const adminAPI = new AdminAPI();
