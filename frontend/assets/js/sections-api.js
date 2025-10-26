/**
 * Sections API Service
 * التواصل مع Backend للصفوف والشُعب
 */

class SectionsAPI {
  constructor() {
    this.baseURL = 'http://localhost:8000/api/sections';
  }

  /**
   * Get headers with JWT token
   */
  getHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
  }

  /**
   * Handle API errors
   */
  async handleResponse(response) {
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || data.message || 'حدث خطأ في الطلب');
    }
    
    return data;
  }

  // ==================== إعدادات المعلم ====================

  /**
   * إنشاء صف مع شُعبه
   */
  async setupGrade(data) {
    const response = await fetch(`${this.baseURL}/setup/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  /**
   * جلب جميع صفوف المعلم
   */
  async getMyGrades() {
    const response = await fetch(`${this.baseURL}/my-grades/`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(response);
  }

  /**
   * تفاصيل صف
   */
  async getGradeDetail(gradeId) {
    const response = await fetch(`${this.baseURL}/grade/${gradeId}/`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(response);
  }

  /**
   * تعديل صف
   */
  async updateGrade(gradeId, data) {
    const response = await fetch(`${this.baseURL}/grade/${gradeId}/`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  /**
   * حذف صف
   */
  async deleteGrade(gradeId) {
    const response = await fetch(`${this.baseURL}/grade/${gradeId}/`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });
    return this.handleResponse(response);
  }

  // ==================== إدارة الشُعب ====================

  /**
   * جلب شُعب صف
   */
  async getGradeSections(gradeId) {
    const response = await fetch(`${this.baseURL}/grade/${gradeId}/sections/`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(response);
  }

  /**
   * تفاصيل شعبة
   */
  async getSectionDetail(sectionId) {
    const response = await fetch(`${this.baseURL}/section/${sectionId}/`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(response);
  }

  /**
   * إعداد روابط شعبة
   */
  async setupSectionLink(data) {
    const response = await fetch(`${this.baseURL}/section/link/setup/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  /**
   * إحصائيات رابط شعبة
   */
  async getSectionLinkStats(sectionId) {
    const response = await fetch(`${this.baseURL}/section/${sectionId}/link/stats/`, {
      headers: this.getHeaders()
    });
    return this.handleResponse(response);
  }

  // ==================== صفحة الانضمام ====================

  /**
   * معلومات الشعبة للطالب (Public)
   */
  async getJoinPageInfo(token) {
    const response = await fetch(`${this.baseURL}/join/${token}/info/`);
    return this.handleResponse(response);
  }

  /**
   * تسجيل طالب (Public)
   */
  async registerStudent(data) {
    const response = await fetch(`${this.baseURL}/join/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  /**
   * تحديد انضمام للقروب (Public)
   */
  async markStudentJoined(token, fullName) {
    const response = await fetch(`${this.baseURL}/join/${token}/joined/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name: fullName })
    });
    return this.handleResponse(response);
  }

  // ==================== Helper Methods ====================

  /**
   * فحص صحة رابط واتساب
   */
  validateWhatsAppLink(link) {
    if (!link) return { valid: false, message: 'الرابط مطلوب' };
    
    const pattern = /(https?:\/\/)?(chat\.whatsapp\.com|wa\.me)\/.+/;
    if (!pattern.test(link)) {
      return { valid: false, message: 'رابط واتساب غير صحيح' };
    }
    
    if (!link.startsWith('https://')) {
      return { valid: false, message: 'الرابط يجب أن يبدأ بـ https://' };
    }
    
    return { valid: true, message: 'رابط صحيح' };
  }

  /**
   * فحص صحة رابط تيليجرام
   */
  validateTelegramLink(link) {
    if (!link) return { valid: false, message: 'الرابط مطلوب' };
    
    const pattern = /(https?:\/\/)?t\.me\/.+/;
    if (!pattern.test(link)) {
      return { valid: false, message: 'رابط تيليجرام غير صحيح' };
    }
    
    if (!link.startsWith('https://')) {
      return { valid: false, message: 'الرابط يجب أن يبدأ بـ https://' };
    }
    
    return { valid: true, message: 'رابط صحيح' };
  }

  /**
   * نسخ نص إلى الحافظة
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      // Fallback للمتصفحات القديمة
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    }
  }

  /**
   * مشاركة رابط
   */
  async shareLink(link, title = 'رابط الانضمام') {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: 'انضم إلى الشعبة',
          url: link
        });
        return true;
      } catch (err) {
        return false;
      }
    }
    return false;
  }

  /**
   * تنسيق التاريخ
   */
  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  /**
   * حساب الأيام المتبقية
   */
  getDaysRemaining(expiryDate) {
    const now = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }

  /**
   * جلب قائمة الطلاب المسجلين في شعبة
   */
  async getSectionStudents(sectionId) {
    return await api.get(`/sections/section/${sectionId}/students/`);
  }
}

// إنشاء instance واحد
const sectionsAPI = new SectionsAPI();
