/**
 * API Service - للتعامل مع Django Backend
 */

const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api',
  TIMEOUT: 30000,
};

class APIService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  /**
   * الحصول على headers الطلب
   */
  getHeaders(includeAuth = true, isFormData = false) {
    const headers = {};
    
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }
    
    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  /**
   * إرسال طلب HTTP
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(options.auth !== false, options.isFormData),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        const error = new Error(data.error || data.message || 'حدث خطأ في الطلب');
        error.details = data.details; // إضافة التفاصيل للخطأ
        error.status = response.status;
        throw error;
      }

      return data;
    } catch (error) {
      console.error('API Request Error:', error);
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, {
      method: 'GET',
      ...options,
    });
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: options.isFormData ? data : JSON.stringify(data),
      ...options,
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...options,
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, {
      method: 'DELETE',
      ...options,
    });
  }

  /**
   * تحديث التوكن
   */
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  /**
   * الحصول على التوكن
   */
  getToken() {
    return this.token;
  }

  // ========== Auth APIs ==========

  /**
   * تسجيل معلم جديد
   */
  async register(userData) {
    return this.post('/auth/register/', userData, { auth: false });
  }

  /**
   * تفعيل الحساب
   */
  async activate(email, code) {
    return this.post('/auth/activate/', { email, code }, { auth: false });
  }

  /**
   * تسجيل الدخول
   */
  async login(email, password) {
    const response = await this.post('/auth/login/', { email, password }, { auth: false });
    
    if (response.tokens) {
      this.setToken(response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);
      localStorage.setItem('teacher', JSON.stringify(response.teacher));
    }
    
    return response;
  }

  /**
   * تسجيل الخروج
   */
  logout() {
    this.setToken(null);
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('teacher');
  }

  /**
   * الحصول على ملف المعلم
   */
  async getProfile() {
    return this.get('/auth/profile/');
  }

  /**
   * تغيير كلمة المرور
   */
  async changePassword(oldPassword, newPassword) {
    return this.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }

  /**
   * الحصول على الإعدادات
   */
  async getSettings() {
    return this.get('/auth/settings/');
  }

  /**
   * تحديث الإعدادات
   */
  async updateSettings(settings) {
    return this.put('/auth/settings/', settings);
  }

  // ========== Projects APIs ==========

  /**
   * الحصول على قائمة المشاريع
   */
  async getProjects() {
    return this.get('/projects/');
  }

  /**
   * الحصول على مشروع محدد
   */
  async getProject(projectId) {
    return this.get(`/projects/${projectId}/`);
  }

  /**
   * إنشاء مشروع جديد
   */
  async createProject(projectData) {
    return this.post('/projects/', projectData);
  }

  /**
   * تحديث مشروع
   */
  async updateProject(projectId, projectData) {
    return this.put(`/projects/${projectId}/`, projectData);
  }

  /**
   * حذف مشروع
   */
  async deleteProject(projectId) {
    return this.delete(`/projects/${projectId}/`);
  }

  /**
   * الحصول على قائمة الطلاب في مشروع
   */
  async getStudents(projectId) {
    return this.get(`/projects/${projectId}/students/`);
  }

  /**
   * إضافة طالب لمشروع
   */
  async addStudent(projectId, studentData) {
    return this.post(`/projects/${projectId}/students/`, studentData);
  }

  /**
   * الحصول على التسليمات
   */
  async getSubmissions(projectId) {
    return this.get(`/projects/${projectId}/submissions/`);
  }

  /**
   * رفع تسليم
   */
  async uploadSubmission(formData) {
    return this.post('/projects/submissions/upload/', formData, {
      auth: false,
      isFormData: true,
    });
  }

  /**
   * مراجعة تسليم
   */
  async reviewSubmission(submissionId, reviewData) {
    return this.put(`/projects/submissions/${submissionId}/review/`, reviewData);
  }
}

// إنشاء نسخة واحدة من API Service
const api = new APIService();
