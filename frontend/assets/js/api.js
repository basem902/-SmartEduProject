/**
 * API Service - للتعامل مع Django Backend
 */

const API_CONFIG = {
  // Use global API_BASE from config.js with fallback
  BASE_URL: window.API_BASE || 'http://localhost:8000/api',
  TIMEOUT: 30000,
};

class APIService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.token = localStorage.getItem('access_token');
    console.log('🌐 APIService initialized with baseURL:', this.baseURL);
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
      
      // Handle 504 Gateway Timeout
      if (response.status === 504) {
        const error = new Error('⏰ السيرفر يستغرق وقتاً أطول من المعتاد. يرجى المحاولة مرة أخرى بعد قليل.');
        error.status = 504;
        error.isTimeout = true;
        throw error;
      }
      
      // Handle empty response
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.error('Invalid response type:', contentType);
        const error = new Error('⚠️ استجابة غير صالحة من السيرفر');
        error.status = response.status;
        throw error;
      }
      
      const data = await response.json();

      if (!response.ok) {
        // 🔒 Auto-logout عند 401 Unauthorized
        if (response.status === 401) {
          console.warn('⚠️ Session expired or invalid token - logging out...');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user_data');
          
          // Redirect to login إلا إذا كنا في صفحة login أصلاً
          if (!window.location.pathname.includes('login.html')) {
            window.location.href = '/pages/login.html?expired=true';
          }
        }
        
        const error = new Error(data.error || data.message || 'حدث خطأ في الطلب');
        error.details = data.details;
        error.status = response.status;
        throw error;
      }

      return data;
    } catch (error) {
      console.error('API Request Error:', error);
      
      // Handle network errors
      if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
        error.message = '❌ فشل الاتصال بالسيرفر. تحقق من الإنترنت.';
      }
      
      // Handle timeout
      if (error.isTimeout) {
        error.message = '⏰ السيرفر يستغرق وقتاً طويلاً (يستيقظ من النوم). يرجى الانتظار 30 ثانية والمحاولة مرة أخرى.';
      }
      
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
   * تسجيل الدخول (مع retry للـ 504 timeout)
   */
  async login(email, password, retryCount = 0) {
    try {
      const response = await this.post('/auth/login/', { email, password }, { auth: false });
      
      if (response.tokens) {
        this.setToken(response.tokens.access);
        localStorage.setItem('refresh_token', response.tokens.refresh);
        localStorage.setItem('teacher', JSON.stringify(response.teacher));
      }
      
      return response;
    } catch (error) {
      // إذا كان 504 وأقل من محاولتين، أعد المحاولة
      if (error.status === 504 && retryCount < 2) {
        console.log(`⏰ Timeout detected. Retrying... (${retryCount + 1}/2)`);
        await new Promise(resolve => setTimeout(resolve, 3000)); // انتظر 3 ثواني
        return this.login(email, password, retryCount + 1);
      }
      throw error;
    }
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

  /**
   * إنشاء مشروع جديد مع ملفات (FormData)
   */
  async createProjectWithFiles(formData) {
    return this.request('/projects/create-new/', {
      method: 'POST',
      body: formData,
      isFormData: true
    });
  }

  // ========== Sections & Grades APIs ==========

  /**
   * جلب جميع صفوف المعلم
   */
  async getMyGrades() {
    return this.get('/sections/my-grades/');
  }

  /**
   * جلب شُعب صف معين
   */
  async getGradeSections(gradeId) {
    return this.get(`/sections/grade/${gradeId}/sections/`);
  }

  // ========== AI Generation APIs ==========

  /**
   * توليد محتوى بالذكاء الاصطناعي
   */
  async generateAI(data) {
    return this.post('/sections/ai/generate/', data);
  }

  // ========== Teacher APIs ==========

  /**
   * جلب مواد المعلم
   */
  async getTeacherSubjects() {
    return this.get('/auth/subjects/');
  }
}

// إنشاء نسخة واحدة من API Service
const api = new APIService();
