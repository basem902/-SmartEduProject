/**
 * Main Application Script
 */

// تسجيل Service Worker للـ PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then(registration => {
        console.log('Service Worker registered:', registration);
      })
      .catch(error => {
        console.error('Service Worker registration failed:', error);
      });
  });
}

// إضافة دعم تثبيت PWA
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // إظهار زر التثبيت
  showInstallButton();
});

function showInstallButton() {
  const installBtn = document.createElement('button');
  installBtn.className = 'btn btn-primary';
  installBtn.style.cssText = 'position: fixed; bottom: 80px; left: 20px; z-index: 1000;';
  installBtn.innerHTML = '📱 تثبيت التطبيق';
  installBtn.onclick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        UI.showToast('تم تثبيت التطبيق بنجاح', 'success');
      }
      
      deferredPrompt = null;
      installBtn.remove();
    }
  };
  
  document.body.appendChild(installBtn);
}

// مراقبة حالة الاتصال بالإنترنت
window.addEventListener('online', () => {
  UI.showToast('تم استعادة الاتصال بالإنترنت', 'success');
});

window.addEventListener('offline', () => {
  UI.showToast('لا يوجد اتصال بالإنترنت', 'warning');
});

// التعامل مع الأخطاء العامة
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

// دوال مساعدة عامة
const App = {
  /**
   * تهيئة التطبيق
   */
  init() {
    console.log('SmartEduProject initialized');
    
    // تحميل الثيم
    if (typeof themeManager !== 'undefined') {
      themeManager.loadFromBackend();
    }
    
    // التحقق من الـ Token وتحديثه إذا لزم الأمر
    this.checkTokenExpiry();
  },

  /**
   * التحقق من انتهاء صلاحية الـ Token
   */
  async checkTokenExpiry() {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      try {
        // محاولة الحصول على الملف الشخصي للتحقق من صلاحية الـ Token
        await api.getProfile();
      } catch (error) {
        // إذا فشل، حاول تحديث الـ Token
        await this.refreshToken();
      }
    }
  },

  /**
   * تحديث الـ Token
   */
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
      try {
        const response = await fetch(`${api.baseURL}/token/refresh/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh: refreshToken }),
        });

        const data = await response.json();

        if (response.ok && data.access) {
          api.setToken(data.access);
          return true;
        } else {
          // فشل التحديث، تسجيل خروج المستخدم
          this.handleTokenExpiry();
          return false;
        }
      } catch (error) {
        console.error('Token refresh failed:', error);
        this.handleTokenExpiry();
        return false;
      }
    } else {
      this.handleTokenExpiry();
      return false;
    }
  },

  /**
   * التعامل مع انتهاء صلاحية الـ Token
   */
  handleTokenExpiry() {
    api.logout();
    UI.showToast('انتهت جلستك، يرجى تسجيل الدخول مرة أخرى', 'warning');
    
    setTimeout(() => {
      window.location.href = '/pages/login.html';
    }, 2000);
  },

  /**
   * تحديث واجهة المستخدم للمعلم الحالي
   */
  updateUserUI() {
    if (auth.isAuthenticated()) {
      const teacher = auth.getTeacher();
      
      // تحديث اسم المعلم
      const userNameElements = document.querySelectorAll('.user-name');
      userNameElements.forEach(el => {
        el.textContent = teacher.full_name;
      });
      
      // تحديث الصورة الرمزية
      const avatarElements = document.querySelectorAll('.user-avatar');
      avatarElements.forEach(el => {
        el.textContent = auth.getInitials();
      });
    }
  },

  /**
   * منع إرسال النموذج الافتراضي
   */
  preventDefaultFormSubmit() {
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
      });
    });
  },
};

// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
  App.init();
  App.preventDefaultFormSubmit();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + K: فتح البحث
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const searchInput = document.querySelector('[type="search"]');
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  // Escape: إغلاق Modal
  if (e.key === 'Escape') {
    UI.closeModal();
  }
});
