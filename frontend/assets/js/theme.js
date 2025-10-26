/**
 * Theme Manager - إدارة Dark/Light Mode
 */

class ThemeManager {
  constructor() {
    this.theme = localStorage.getItem('theme') || 'light';
    this.init();
  }

  /**
   * تهيئة الثيم
   */
  init() {
    this.apply();
    this.createToggleButton();
  }

  /**
   * تطبيق الثيم
   */
  apply() {
    if (this.theme === 'dark') {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }

  /**
   * تبديل الثيم
   */
  toggle() {
    this.theme = this.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', this.theme);
    this.apply();
    this.updateToggleButton();
    
    // تحديث الثيم في Backend إذا كان المستخدم مسجلاً
    this.syncWithBackend();
  }

  /**
   * إنشاء زر التبديل
   */
  createToggleButton() {
    const button = document.createElement('button');
    button.id = 'theme-toggle-btn';
    button.className = 'theme-toggle';
    button.setAttribute('aria-label', 'تبديل الثيم');
    button.innerHTML = this.theme === 'dark' ? '☀️' : '🌙';
    button.onclick = () => this.toggle();
    
    document.body.appendChild(button);
  }

  /**
   * تحديث زر التبديل
   */
  updateToggleButton() {
    const button = document.getElementById('theme-toggle-btn');
    if (button) {
      button.innerHTML = this.theme === 'dark' ? '☀️' : '🌙';
    }
  }

  /**
   * مزامنة الثيم مع Backend
   */
  async syncWithBackend() {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await api.updateSettings({ theme: this.theme });
      }
    } catch (error) {
      console.error('Failed to sync theme:', error);
    }
  }

  /**
   * تحميل الثيم من Backend
   */
  async loadFromBackend() {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const response = await api.getSettings();
        if (response.settings && response.settings.theme) {
          this.theme = response.settings.theme;
          localStorage.setItem('theme', this.theme);
          this.apply();
          this.updateToggleButton();
        }
      }
    } catch (error) {
      console.error('Failed to load theme:', error);
    }
  }

  /**
   * الحصول على الثيم الحالي
   */
  getTheme() {
    return this.theme;
  }
}

// إنشاء نسخة واحدة من Theme Manager
const themeManager = new ThemeManager();

// تحميل الثيم عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
  themeManager.loadFromBackend();
});
