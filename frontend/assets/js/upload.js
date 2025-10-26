/**
 * File Upload Manager with Security
 */

class FileUploadManager {
  constructor() {
    this.allowedExtensions = ['pdf', 'docx', 'xlsx', 'jpg', 'jpeg', 'png', 'mp4', 'mp3', 'wav'];
    this.maxFileSize = 100 * 1024 * 1024; // 100MB
  }

  /**
   * التحقق من صحة الملف
   */
  validateFile(file) {
    // التحقق من وجود الملف
    if (!file) {
      return { valid: false, error: 'لم يتم اختيار أي ملف' };
    }

    // التحقق من الامتداد
    const extension = this.getFileExtension(file.name);
    if (!this.allowedExtensions.includes(extension)) {
      return {
        valid: false,
        error: `امتداد الملف غير مسموح. الامتدادات المسموحة: ${this.allowedExtensions.join(', ')}`,
      };
    }

    // التحقق من الحجم
    if (file.size > this.maxFileSize) {
      const maxSizeMB = this.maxFileSize / (1024 * 1024);
      return {
        valid: false,
        error: `حجم الملف كبير جداً. الحد الأقصى: ${maxSizeMB}MB`,
      };
    }

    // التحقق من نوع MIME
    const mimeValidation = this.validateMimeType(file, extension);
    if (!mimeValidation.valid) {
      return mimeValidation;
    }

    return { valid: true, error: null };
  }

  /**
   * التحقق من نوع MIME
   */
  validateMimeType(file, extension) {
    const validMimeTypes = {
      pdf: ['application/pdf'],
      docx: [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
      ],
      xlsx: [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
      ],
      jpg: ['image/jpeg'],
      jpeg: ['image/jpeg'],
      png: ['image/png'],
      mp4: ['video/mp4'],
      mp3: ['audio/mpeg', 'audio/mp3'],
      wav: ['audio/wav', 'audio/wave', 'audio/x-wav'],
    };

    const expectedMimes = validMimeTypes[extension];
    if (expectedMimes && !expectedMimes.includes(file.type)) {
      return {
        valid: false,
        error: 'نوع الملف لا يتطابق مع امتداده',
      };
    }

    return { valid: true, error: null };
  }

  /**
   * الحصول على امتداد الملف
   */
  getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
  }

  /**
   * رفع ملف
   */
  async uploadFile(file, projectId, studentId = null, groupId = null, onProgress = null) {
    // التحقق من صحة الملف
    const validation = this.validateFile(file);
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    // إنشاء FormData
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);
    
    if (studentId) {
      formData.append('student_id', studentId);
    }
    
    if (groupId) {
      formData.append('group_id', groupId);
    }

    try {
      // رفع الملف مع متابعة التقدم
      const response = await this.uploadWithProgress(formData, onProgress);
      return response;
    } catch (error) {
      throw new Error(error.message || 'فشل رفع الملف');
    }
  }

  /**
   * رفع الملف مع متابعة التقدم
   */
  uploadWithProgress(formData, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // متابعة التقدم
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });

      // عند الانتهاء
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } else {
          const error = JSON.parse(xhr.responseText);
          reject(new Error(error.error || 'فشل رفع الملف'));
        }
      });

      // عند حدوث خطأ
      xhr.addEventListener('error', () => {
        reject(new Error('فشل رفع الملف'));
      });

      // عند الإلغاء
      xhr.addEventListener('abort', () => {
        reject(new Error('تم إلغاء رفع الملف'));
      });

      // إرسال الطلب
      xhr.open('POST', `${api.baseURL}/projects/submissions/upload/`);
      xhr.send(formData);
    });
  }

  /**
   * إنشاء منطقة رفع الملفات بالسحب والإفلات
   */
  createDropZone(containerId, onFileDrop) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const dropZone = document.createElement('div');
    dropZone.className = 'file-upload';
    dropZone.innerHTML = `
      <div class="file-upload-icon">📤</div>
      <p class="file-upload-text"><strong>اسحب الملف هنا</strong> أو انقر للاختيار</p>
      <p class="file-upload-hint">الامتدادات المسموحة: ${this.allowedExtensions.join(', ')}</p>
      <p class="file-upload-hint">الحد الأقصى: ${this.maxFileSize / (1024 * 1024)}MB</p>
      <input type="file" id="fileInput" style="display: none;" 
             accept="${this.allowedExtensions.map(ext => '.' + ext).join(',')}">
    `;

    container.appendChild(dropZone);

    const fileInput = dropZone.querySelector('#fileInput');

    // النقر للاختيار
    dropZone.addEventListener('click', () => {
      fileInput.click();
    });

    // اختيار ملف
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        onFileDrop(e.target.files[0]);
      }
    });

    // السحب والإفلات
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      
      if (e.dataTransfer.files.length > 0) {
        onFileDrop(e.dataTransfer.files[0]);
      }
    });
  }

  /**
   * عرض معاينة الملف
   */
  showFilePreview(file, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const fileSize = UI.formatFileSize(file.size);
    const fileIcon = this.getFileIcon(file.name);

    const previewHTML = `
      <div class="file-preview fade-in">
        <div class="file-info">
          <div class="file-icon">${fileIcon}</div>
          <div>
            <div><strong>${file.name}</strong></div>
            <div class="text-muted" style="font-size: 14px;">${fileSize}</div>
          </div>
        </div>
        <button class="btn btn-danger btn-sm" onclick="uploadManager.clearFile('${containerId}')">
          حذف
        </button>
      </div>
      <div class="progress">
        <div class="progress-bar" id="uploadProgress" style="width: 0%;"></div>
      </div>
    `;

    container.innerHTML = previewHTML;
  }

  /**
   * الحصول على أيقونة الملف
   */
  getFileIcon(filename) {
    const extension = this.getFileExtension(filename);
    const icons = {
      pdf: '📄',
      docx: '📝',
      xlsx: '📊',
      jpg: '🖼️',
      jpeg: '🖼️',
      png: '🖼️',
      mp4: '🎬',
      mp3: '🎵',
      wav: '🎵',
    };
    return icons[extension] || '📎';
  }

  /**
   * تحديث شريط التقدم
   */
  updateProgress(percent) {
    const progressBar = document.getElementById('uploadProgress');
    if (progressBar) {
      progressBar.style.width = `${percent}%`;
    }
  }

  /**
   * مسح الملف
   */
  clearFile(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = '';
      this.createDropZone(containerId, (file) => {
        this.handleFileDrop(file, containerId);
      });
    }
  }

  /**
   * التعامل مع إفلات الملف
   */
  handleFileDrop(file, containerId) {
    const validation = this.validateFile(file);
    
    if (!validation.valid) {
      UI.showToast(validation.error, 'error');
      return;
    }

    this.showFilePreview(file, containerId);
    UI.showToast('تم اختيار الملف بنجاح', 'success');
  }
}

// إنشاء نسخة واحدة من Upload Manager
const uploadManager = new FileUploadManager();
