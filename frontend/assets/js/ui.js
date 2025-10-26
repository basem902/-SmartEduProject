/**
 * UI Helper Functions
 */

const UI = {
  /**
   * إظهار Toast notification
   */
  showToast(message, type = 'info', duration = 3000) {
    // إزالة أي toast موجود
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
      existingToast.remove();
    }

    // إنشاء toast جديد
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fade-in`;
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 20px;">${this.getToastIcon(type)}</span>
        <span>${message}</span>
      </div>
    `;

    document.body.appendChild(toast);

    // إزالة بعد المدة المحددة
    setTimeout(() => {
      toast.classList.add('slide-out');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  /**
   * الحصول على أيقونة Toast حسب النوع
   */
  getToastIcon(type) {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️',
    };
    return icons[type] || icons.info;
  },

  /**
   * إظهار Modal
   */
  showModal(title, content, actions = []) {
    const modalHTML = `
      <div class="modal-overlay fade-in" id="customModal">
        <div class="modal zoom-in">
          <div class="modal-header">
            <h3>${title}</h3>
            <button class="btn btn-icon" onclick="UI.closeModal()">✕</button>
          </div>
          <div class="modal-body">
            ${content}
          </div>
          ${actions.length > 0 ? `
            <div class="modal-footer">
              ${actions.map(action => `
                <button class="btn ${action.class || 'btn-primary'}" 
                        onclick="${action.onclick}">
                  ${action.text}
                </button>
              `).join('')}
            </div>
          ` : ''}
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // إغلاق عند الضغط على الخلفية
    document.getElementById('customModal').addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        this.closeModal();
      }
    });
  },

  /**
   * إغلاق Modal
   */
  closeModal() {
    const modal = document.getElementById('customModal');
    if (modal) {
      modal.classList.add('fade-out');
      setTimeout(() => modal.remove(), 300);
    }
  },

  /**
   * إظهار تأكيد
   */
  confirm(message, onConfirm, onCancel) {
    this.showModal(
      'تأكيد',
      `<p>${message}</p>`,
      [
        {
          text: 'نعم',
          class: 'btn-primary',
          onclick: `UI.closeModal(); (${onConfirm})();`,
        },
        {
          text: 'إلغاء',
          class: 'btn-secondary',
          onclick: onCancel ? `UI.closeModal(); (${onCancel})();` : 'UI.closeModal()',
        },
      ]
    );
  },

  /**
   * إظهار Loading Spinner
   */
  showLoading(container) {
    const spinner = `
      <div class="text-center" style="padding: 40px;">
        <div class="spinner" style="margin: 0 auto;"></div>
        <p class="mt-2 text-muted">جاري التحميل...</p>
      </div>
    `;
    
    if (typeof container === 'string') {
      document.querySelector(container).innerHTML = spinner;
    } else {
      container.innerHTML = spinner;
    }
  },

  /**
   * إظهار Empty State
   */
  showEmpty(container, message, icon = '📭') {
    const emptyHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">${icon}</div>
        <p class="empty-state-text">${message}</p>
      </div>
    `;
    
    if (typeof container === 'string') {
      document.querySelector(container).innerHTML = emptyHTML;
    } else {
      container.innerHTML = emptyHTML;
    }
  },

  /**
   * إظهار Error
   */
  showError(container, message) {
    const errorHTML = `
      <div class="card" style="border-right: 4px solid var(--danger-color);">
        <div style="display: flex; align-items: center; gap: 15px;">
          <span style="font-size: 32px;">⚠️</span>
          <div>
            <h4 class="text-danger">حدث خطأ</h4>
            <p class="text-muted">${message}</p>
          </div>
        </div>
      </div>
    `;
    
    if (typeof container === 'string') {
      document.querySelector(container).innerHTML = errorHTML;
    } else {
      container.innerHTML = errorHTML;
    }
  },

  /**
   * التحقق من صحة النموذج
   */
  validateForm(formElement) {
    const inputs = formElement.querySelectorAll('[required]');
    let isValid = true;

    inputs.forEach(input => {
      const errorElement = input.nextElementSibling;
      
      if (!input.value.trim()) {
        isValid = false;
        input.style.borderColor = 'var(--danger-color)';
        
        if (errorElement && errorElement.classList.contains('form-error')) {
          errorElement.textContent = 'هذا الحقل مطلوب';
        } else {
          const error = document.createElement('div');
          error.className = 'form-error';
          error.textContent = 'هذا الحقل مطلوب';
          input.parentNode.insertBefore(error, input.nextSibling);
        }
      } else {
        input.style.borderColor = '';
        if (errorElement && errorElement.classList.contains('form-error')) {
          errorElement.remove();
        }
      }
    });

    return isValid;
  },

  /**
   * تنسيق التاريخ
   */
  formatDate(dateString) {
    const date = new Date(dateString);
    const options = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    };
    return date.toLocaleDateString('ar-SA', options);
  },

  /**
   * تنسيق حجم الملف
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 بايت';
    
    const k = 1024;
    const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  },

  /**
   * تنسيق الوقت المتبقي
   */
  formatTimeRemaining(deadline) {
    const now = new Date();
    const end = new Date(deadline);
    const diff = end - now;

    if (diff < 0) {
      return 'انتهى الموعد';
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (days > 0) {
      return `${days} يوم و ${hours} ساعة`;
    } else if (hours > 0) {
      return `${hours} ساعة و ${minutes} دقيقة`;
    } else {
      return `${minutes} دقيقة`;
    }
  },

  /**
   * إضافة تأثير Skeleton Loading
   */
  createSkeleton(count = 3) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += `
        <div class="card">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-text"></div>
          <div class="skeleton skeleton-text" style="width: 80%;"></div>
        </div>
      `;
    }
    return html;
  },

  /**
   * Debounce function
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Copy to clipboard
   */
  copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      this.showToast('تم النسخ بنجاح', 'success');
    }).catch(() => {
      this.showToast('فشل النسخ', 'error');
    });
  },

  /**
   * Scroll to element
   */
  scrollTo(element, offset = 0) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (el) {
      const top = el.getBoundingClientRect().top + window.pageYOffset - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  },
};

// التأكد من تحميل UI قبل استخدامه
window.UI = UI;
