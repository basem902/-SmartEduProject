/**
 * Dark Mode Quick Init
 * ملف تهيئة سريع لإضافة Dark Mode لأي صفحة
 * 
 * الاستخدام:
 * <script src="/assets/js/dark-mode-manager.js"></script>
 * <script src="/assets/js/dark-mode-init.js"></script>
 */

document.addEventListener('DOMContentLoaded', () => {
    // تحديد الموضع بناءً على نوع الصفحة
    const pageType = document.body.dataset.pageType || 'default';
    
    let position = 'top-right';
    let size = 'medium';
    
    // تخصيص حسب نوع الصفحة
    switch (pageType) {
        case 'auth': // login, register
            position = 'top-left';
            break;
        case 'dashboard':
            position = 'top-right';
            size = 'small';
            break;
        case 'wizard': // sections-setup, create-project
            position = 'bottom-left';
            size = 'small';
            break;
        default:
            position = 'top-right';
    }
    
    // إنشاء زر Dark Mode
    darkModeManager.createToggle(null, {
        position: position,
        size: size
    });
    
    console.log('🌙 Dark Mode initialized for page type:', pageType);
});
