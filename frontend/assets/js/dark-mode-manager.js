/**
 * Dark Mode Manager - SmartEduProject
 * نظام موحّد لإدارة الوضع الداكن عبر جميع الصفحات
 * يحفظ التفضيلات في localStorage
 */

class DarkModeManager {
    constructor() {
        this.storageKey = 'smartedu_darkMode';
        this.toggleBtn = null;
        this.init();
    }

    /**
     * تهيئة النظام
     */
    init() {
        // ✅ Check for existing data-theme attribute (for compatibility)
        const existingTheme = document.body.dataset.theme;
        
        // تحميل الحالة من localStorage
        const savedMode = this.getStoredMode();
        
        // If page has data-theme="dark", respect it if no saved preference
        const initialMode = localStorage.getItem(this.storageKey) === null && existingTheme === 'dark' 
            ? true 
            : savedMode;
        
        // تطبيق الوضع المحفوظ
        this.setMode(initialMode, false);
        
        // الاستماع لتغييرات localStorage من علامات تبويب أخرى
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey) {
                const newMode = e.newValue === 'true';
                this.setMode(newMode, false);
            }
        });
        
        console.log('✅ Dark Mode Manager initialized:', initialMode ? 'Dark' : 'Light');
    }

    /**
     * الحصول على الوضع المحفوظ
     * @returns {boolean}
     */
    getStoredMode() {
        const stored = localStorage.getItem(this.storageKey);
        
        // إذا لم يكن محفوظ، استخدم تفضيل النظام
        if (stored === null) {
            return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
        
        return stored === 'true';
    }

    /**
     * تعيين الوضع
     * @param {boolean} isDark - هل الوضع داكن؟
     * @param {boolean} save - هل يتم الحفظ في localStorage؟
     */
    setMode(isDark, save = true) {
        // تطبيق على body
        document.body.classList.toggle('dark-mode', isDark);
        document.documentElement.classList.toggle('dark-mode', isDark);
        
        // تحديث meta theme-color
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', isDark ? '#1a1a2e' : '#00ADEF');
        }
        
        // حفظ في localStorage
        if (save) {
            localStorage.setItem(this.storageKey, isDark.toString());
            console.log('💾 Dark Mode saved:', isDark ? 'Dark' : 'Light');
        }
        
        // تحديث زر التبديل
        this.updateToggleButton(isDark);
        
        // إطلاق حدث مخصص
        window.dispatchEvent(new CustomEvent('darkmodechange', { detail: { isDark } }));
    }

    /**
     * تبديل الوضع
     */
    toggle() {
        const currentMode = this.isEnabled();
        const newMode = !currentMode;
        
        this.setMode(newMode);
        
        // Haptic feedback (إذا كان متاحاً)
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
        
        return newMode;
    }

    /**
     * التحقق إذا كان الوضع الداكن مفعّل
     * @returns {boolean}
     */
    isEnabled() {
        return document.body.classList.contains('dark-mode');
    }

    /**
     * إنشاء زر التبديل
     * @param {HTMLElement} container - الحاوية التي سيُضاف فيها الزر
     * @param {Object} options - خيارات التخصيص
     */
    createToggle(container, options = {}) {
        const {
            position = 'top-right',
            size = 'medium',
            showLabel = false,
            customClass = ''
        } = options;

        // إنشاء الزر
        const toggle = document.createElement('button');
        toggle.className = `dark-mode-toggle ${position} ${size} ${customClass}`;
        toggle.setAttribute('aria-label', 'تبديل الوضع الداكن');
        toggle.setAttribute('title', 'تبديل الوضع الداكن');
        
        // الأيقونات
        const sunIcon = '☀️';
        const moonIcon = '🌙';
        
        toggle.innerHTML = `
            <span class="icon sun">${sunIcon}</span>
            <span class="icon moon">${moonIcon}</span>
            ${showLabel ? '<span class="label">الوضع الداكن</span>' : ''}
        `;
        
        // إضافة event listener
        toggle.addEventListener('click', () => {
            this.toggle();
        });
        
        // حفظ المرجع
        this.toggleBtn = toggle;
        
        // إضافة إلى الحاوية
        if (container) {
            container.appendChild(toggle);
        } else {
            document.body.appendChild(toggle);
        }
        
        // تحديث الحالة الأولية
        this.updateToggleButton(this.isEnabled());
        
        return toggle;
    }

    /**
     * تحديث زر التبديل
     * @param {boolean} isDark
     */
    updateToggleButton(isDark) {
        if (!this.toggleBtn) return;
        
        this.toggleBtn.classList.toggle('dark', isDark);
        this.toggleBtn.setAttribute('aria-checked', isDark.toString());
    }

    /**
     * تفعيل الوضع الداكن
     */
    enable() {
        this.setMode(true);
    }

    /**
     * تعطيل الوضع الداكن
     */
    disable() {
        this.setMode(false);
    }

    /**
     * إعادة تعيين إلى الافتراضي (حسب تفضيل النظام)
     */
    reset() {
        localStorage.removeItem(this.storageKey);
        const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.setMode(systemPreference, false);
    }
}

// CSS Styles للزر
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    .dark-mode-toggle {
        position: fixed;
        background: var(--bg-card, #fff);
        border: 2px solid var(--border-color, #e0e0e0);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        z-index: 9998;
        overflow: hidden;
    }

    .dark-mode-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    }

    .dark-mode-toggle:active {
        transform: scale(0.95);
    }

    /* Positions */
    .dark-mode-toggle.top-right {
        top: 20px;
        right: 20px;
    }

    .dark-mode-toggle.top-left {
        top: 20px;
        left: 20px;
    }

    .dark-mode-toggle.bottom-right {
        bottom: 20px;
        right: 20px;
    }

    .dark-mode-toggle.bottom-left {
        bottom: 20px;
        left: 20px;
    }

    /* Sizes */
    .dark-mode-toggle.small {
        width: 40px;
        height: 40px;
        font-size: 18px;
    }

    .dark-mode-toggle.large {
        width: 60px;
        height: 60px;
        font-size: 28px;
    }

    /* Icons */
    .dark-mode-toggle .icon {
        position: absolute;
        transition: all 0.3s ease;
        font-size: 24px;
    }

    .dark-mode-toggle .icon.sun {
        opacity: 1;
        transform: rotate(0deg) scale(1);
    }

    .dark-mode-toggle .icon.moon {
        opacity: 0;
        transform: rotate(180deg) scale(0);
    }

    .dark-mode-toggle.dark .icon.sun {
        opacity: 0;
        transform: rotate(-180deg) scale(0);
    }

    .dark-mode-toggle.dark .icon.moon {
        opacity: 1;
        transform: rotate(0deg) scale(1);
    }

    /* Dark Mode Styles */
    body.dark-mode .dark-mode-toggle {
        background: var(--bg-card-dark, #2d2d3d);
        border-color: var(--border-color-dark, #444);
    }

    /* Mobile */
    @media (max-width: 768px) {
        .dark-mode-toggle {
            width: 45px;
            height: 45px;
        }

        .dark-mode-toggle.top-right,
        .dark-mode-toggle.bottom-right {
            right: 15px;
        }

        .dark-mode-toggle.top-left,
        .dark-mode-toggle.bottom-left {
            left: 15px;
        }
    }

    /* Label (optional) */
    .dark-mode-toggle .label {
        position: absolute;
        right: 60px;
        background: var(--bg-card, #fff);
        padding: 8px 16px;
        border-radius: 8px;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .dark-mode-toggle:hover .label {
        opacity: 1;
    }
`;
document.head.appendChild(styleSheet);

// إنشاء instance عالمي
const darkModeManager = new DarkModeManager();

// تصدير للاستخدام في modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkModeManager;
}
