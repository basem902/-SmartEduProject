/**
 * Authentication Manager
 */

class AuthManager {
  constructor() {
    this.currentTeacher = this.getTeacher();
  }

  /**
   * التحقق من تسجيل الدخول
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  /**
   * الحصول على المعلم الحالي
   */
  getTeacher() {
    const teacher = localStorage.getItem('teacher');
    return teacher ? JSON.parse(teacher) : null;
  }

  /**
   * تسجيل معلم جديد
   */
  async register(fullName, email, phone, schoolName) {
    try {
      const response = await api.register({
        full_name: fullName,
        email: email,
        phone: phone,
        school_name: schoolName,
      });

      UI.showToast(response.message, 'success');
      return response;
    } catch (error) {
      UI.showToast(error.message || 'فشل التسجيل', 'error');
      throw error;
    }
  }

  /**
   * تفعيل الحساب
   */
  async activate(email, code) {
    try {
      const response = await api.activate(email, code);
      
      UI.showToast(response.message, 'success');
      return response;
    } catch (error) {
      UI.showToast(error.message || 'فشل التفعيل', 'error');
      throw error;
    }
  }

  /**
   * تسجيل الدخول
   */
  async login(email, password) {
    try {
      const response = await api.login(email, password);
      
      this.currentTeacher = response.teacher;
      UI.showToast(response.message, 'success');
      
      // الانتقال إلى لوحة التحكم
      setTimeout(() => {
        window.location.href = '/pages/dashboard.html';
      }, 1000);
      
      return response;
    } catch (error) {
      UI.showToast(error.message || 'فشل تسجيل الدخول', 'error');
      throw error;
    }
  }

  /**
   * تسجيل الخروج
   */
  logout() {
    UI.confirm(
      'هل أنت متأكد من تسجيل الخروج؟',
      () => {
        api.logout();
        this.currentTeacher = null;
        UI.showToast('تم تسجيل الخروج بنجاح', 'success');
        setTimeout(() => {
          window.location.href = '/pages/login.html';
        }, 1000);
      }
    );
  }

  /**
   * تغيير كلمة المرور
   */
  async changePassword(oldPassword, newPassword) {
    try {
      const response = await api.changePassword(oldPassword, newPassword);
      
      UI.showToast(response.message, 'success');
      return response;
    } catch (error) {
      // عرض تفاصيل الخطأ إذا كانت متوفرة
      let errorMessage = error.message || 'فشل تغيير كلمة المرور';
      
      if (error.details) {
        // عرض تفاصيل validation errors
        const details = error.details;
        if (details.new_password && details.new_password.length > 0) {
          errorMessage = details.new_password[0];
        } else if (details.old_password && details.old_password.length > 0) {
          errorMessage = details.old_password[0];
        } else {
          errorMessage = JSON.stringify(details);
        }
      }
      
      UI.showToast(errorMessage, 'error', 6000);
      throw error;
    }
  }

  /**
   * حماية الصفحات
   */
  protectPage() {
    if (!this.isAuthenticated()) {
      UI.showToast('يجب تسجيل الدخول أولاً', 'warning');
      setTimeout(() => {
        window.location.href = '/pages/login.html';
      }, 1500);
    }
  }

  /**
   * منع الوصول للصفحات العامة بعد تسجيل الدخول
   */
  redirectIfAuthenticated() {
    if (this.isAuthenticated()) {
      window.location.href = '/pages/dashboard.html';
    }
  }

  /**
   * الحصول على الاسم الأول للمعلم
   */
  getFirstName() {
    if (this.currentTeacher) {
      return this.currentTeacher.full_name.split(' ')[0];
    }
    return '';
  }

  /**
   * الحصول على الأحرف الأولى من الاسم
   */
  getInitials() {
    if (this.currentTeacher) {
      const names = this.currentTeacher.full_name.split(' ');
      if (names.length >= 2) {
        return names[0][0] + names[1][0];
      }
      return names[0][0];
    }
    return '';
  }

  /**
   * تحديث معلومات المعلم
   */
  updateTeacher(teacher) {
    this.currentTeacher = teacher;
    localStorage.setItem('teacher', JSON.stringify(teacher));
  }
}

// إنشاء نسخة واحدة من Auth Manager
const auth = new AuthManager();
