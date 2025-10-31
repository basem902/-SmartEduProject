/**
 * 🎯 نظام التحقق من الطالب - Smart Name Verification
 * 
 * يتحقق من:
 * 1. صحة الاسم (4 أجزاء)
 * 2. وجود الطالب في القائمة
 * 3. عضوية التليجرام
 * 4. عدم الرفع السابق
 */

class StudentVerification {
    constructor(projectId) {
        this.projectId = projectId;
        this.API_URL = 'http://localhost:8000/api/projects';
    }

    /**
     * التحقق من صحة الاسم محلياً (قبل إرسال الطلب)
     */
    validateNameFormat(studentName) {
        // 1. التحقق من أن الاسم غير فارغ
        if (!studentName || studentName.trim() === '') {
            return {
                valid: false,
                error: 'يرجى إدخال الاسم الكامل'
            };
        }

        // 2. إزالة المسافات الزائدة
        const cleanName = studentName.trim().replace(/\s+/g, ' ');

        // 3. التحقق من عدد الأجزاء (يجب أن يكون 4 أجزاء على الأقل)
        const parts = cleanName.split(' ');
        if (parts.length < 4) {
            return {
                valid: false,
                error: `الاسم يجب أن يكون رباعياً (${parts.length}/4 أجزاء)`,
                hint: 'مثال: محمد أحمد علي حسن'
            };
        }

        // 4. التحقق من أن كل جزء يحتوي على حروف فقط
        const arabicLettersOnly = /^[\u0600-\u06FF\s]+$/;
        if (!arabicLettersOnly.test(cleanName)) {
            return {
                valid: false,
                error: 'الاسم يجب أن يحتوي على حروف عربية فقط',
                hint: 'تأكد من عدم وجود أرقام أو رموز'
            };
        }

        // 5. التحقق من طول كل جزء
        for (let i = 0; i < parts.length; i++) {
            if (parts[i].length < 2) {
                return {
                    valid: false,
                    error: `الجزء ${i + 1} من الاسم قصير جداً: "${parts[i]}"`,
                    hint: 'كل جزء يجب أن يكون حرفين على الأقل'
                };
            }
        }

        return {
            valid: true,
            cleanName: cleanName
        };
    }

    /**
     * التحقق من الطالب عبر API
     */
    async verifyStudent(studentName) {
        try {
            // 1. التحقق المحلي أولاً
            const localValidation = this.validateNameFormat(studentName);
            if (!localValidation.valid) {
                return {
                    success: false,
                    ...localValidation
                };
            }

            // 2. إظهار مؤشر التحميل
            this.showLoading('جاري التحقق من الاسم...');

            // 3. إرسال الطلب للـ API
            const response = await fetch(`${this.API_URL}/verify-student/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    student_name: localValidation.cleanName,
                    project_id: this.projectId
                })
            });

            const data = await response.json();

            // 4. معالجة النتيجة
            this.hideLoading();

            if (data.success) {
                // ✅ نجح التحقق
                return {
                    success: true,
                    student: data.student,
                    project: data.project,
                    uploadToken: data.upload_token,
                    expiresAt: data.expires_at
                };
            } else {
                // ❌ فشل التحقق
                return {
                    success: false,
                    error: data.error,
                    message: data.message,
                    suggestions: data.suggestions || [],
                    action: data.action,
                    actionSteps: data.action_steps || [],
                    telegramLink: data.telegram_link
                };
            }

        } catch (error) {
            console.error('خطأ في التحقق:', error);
            this.hideLoading();
            
            return {
                success: false,
                error: 'connection_error',
                message: 'فشل الاتصال بالخادم',
                hint: 'تحقق من اتصال الإنترنت وحاول مرة أخرى'
            };
        }
    }

    /**
     * عرض نتيجة التحقق للمستخدم
     */
    displayResult(result) {
        const container = document.getElementById('verification-result');
        if (!container) return;

        container.innerHTML = '';

        if (result.success) {
            // ✅ نجح التحقق
            container.innerHTML = `
                <div class="alert alert-success">
                    <div class="alert-icon">✅</div>
                    <div class="alert-content">
                        <h4>مرحباً ${result.student.name}!</h4>
                        <p>تم التحقق من هويتك بنجاح</p>
                        
                        <div class="student-info">
                            <p><strong>الصف:</strong> ${result.student.grade}</p>
                            <p><strong>الشعبة:</strong> ${result.student.section}</p>
                            <p><strong>المدرسة:</strong> ${result.student.school}</p>
                        </div>
                        
                        <div class="project-info">
                            <h5>معلومات المشروع:</h5>
                            <p><strong>العنوان:</strong> ${result.project.title}</p>
                            <p><strong>الموعد النهائي:</strong> ${this.formatDate(result.project.deadline)}</p>
                            <p><strong>أنواع الملفات المسموحة:</strong> ${result.project.allowed_file_types.join(', ')}</p>
                            <p><strong>الحجم الأقصى:</strong> ${this.formatSize(result.project.max_file_size)}</p>
                        </div>
                        
                        <div class="upload-token">
                            <p class="text-muted">⏰ صالح لمدة 30 دقيقة</p>
                        </div>
                        
                        <button class="btn btn-primary btn-large" onclick="proceedToUpload()">
                            📤 متابعة إلى رفع الملف
                        </button>
                    </div>
                </div>
            `;

            // حفظ الـ token
            sessionStorage.setItem('uploadToken', result.uploadToken);
            sessionStorage.setItem('tokenExpiry', result.expiresAt);
            
        } else {
            // ❌ فشل التحقق
            let alertClass = 'alert-danger';
            let icon = '❌';
            
            if (result.error === 'student_not_found' && result.suggestions && result.suggestions.length > 0) {
                alertClass = 'alert-warning';
                icon = '⚠️';
            } else if (result.error === 'telegram_not_verified') {
                alertClass = 'alert-info';
                icon = '📱';
            }
            
            let html = `
                <div class="alert ${alertClass}">
                    <div class="alert-icon">${icon}</div>
                    <div class="alert-content">
                        <h4>${this.getErrorTitle(result.error)}</h4>
                        <p>${result.message}</p>
            `;

            // إضافة الاقتراحات إذا وجدت
            if (result.suggestions && result.suggestions.length > 0) {
                html += `
                    <div class="suggestions">
                        <p><strong>هل تقصد أحد هذه الأسماء؟</strong></p>
                        <ul>
                            ${result.suggestions.map(name => 
                                `<li><a href="#" onclick="fillName('${name}')">${name}</a></li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            }

            // إضافة الخطوات المطلوبة
            if (result.actionSteps && result.actionSteps.length > 0) {
                html += `
                    <div class="action-steps">
                        <p><strong>الخطوات المطلوبة:</strong></p>
                        <ol>
                            ${result.actionSteps.map(step => `<li>${step}</li>`).join('')}
                        </ol>
                    </div>
                `;
            }

            // إضافة رابط التليجرام إذا وجد
            if (result.telegramLink) {
                html += `
                    <a href="${result.telegramLink}" target="_blank" class="btn btn-primary">
                        📱 الانضمام إلى القروب
                    </a>
                `;
            }

            // إضافة نصيحة إذا وجدت
            if (result.hint) {
                html += `<p class="hint">💡 ${result.hint}</p>`;
            }

            // إضافة الإجراء المقترح
            if (result.action) {
                html += `<p class="action-text"><strong>الحل:</strong> ${result.action}</p>`;
            }

            html += `
                        <button class="btn btn-secondary" onclick="tryAgain()">
                            🔄 حاول مرة أخرى
                        </button>
                    </div>
                </div>
            `;

            container.innerHTML = html;
        }
    }

    /**
     * الدوال المساعدة
     */
    getErrorTitle(errorCode) {
        const titles = {
            'missing_name': 'الاسم مطلوب',
            'invalid_name': 'اسم غير صحيح',
            'student_not_found': 'الطالب غير موجود',
            'telegram_not_verified': 'التليجرام غير مفعّل',
            'already_submitted': 'تم الرفع مسبقاً',
            'deadline_expired': 'انتهى الموعد',
            'project_not_found': 'المشروع غير موجود',
            'connection_error': 'خطأ في الاتصال',
            'server_error': 'خطأ في الخادم'
        };
        return titles[errorCode] || 'خطأ';
    }

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

    formatSize(bytes) {
        const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت'];
        if (bytes === 0) return '0 بايت';
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }

    showLoading(message) {
        const container = document.getElementById('verification-result');
        if (container) {
            container.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    hideLoading() {
        // يتم إخفاؤه تلقائياً عند عرض النتيجة
    }
}

/**
 * الدوال العامة للاستخدام في HTML
 */
let verifier;

function initVerification(projectId) {
    verifier = new StudentVerification(projectId);
}

async function verifyAndProceed() {
    const nameInput = document.getElementById('student-name');
    const studentName = nameInput.value;
    
    if (!verifier) {
        alert('خطأ: لم يتم تهيئة النظام');
        return;
    }
    
    const result = await verifier.verifyStudent(studentName);
    verifier.displayResult(result);
}

function fillName(name) {
    document.getElementById('student-name').value = name;
}

function tryAgain() {
    document.getElementById('verification-result').innerHTML = '';
    document.getElementById('student-name').focus();
}

function proceedToUpload() {
    // الانتقال لصفحة رفع الملف
    window.location.href = 'upload.html';
}
