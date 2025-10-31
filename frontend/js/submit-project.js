/**
 * Submit Project JavaScript
 * التحكم في صفحة تسليم المشروع
 */

// State Management
const state = {
    currentStep: 1,
    projectId: null,
    sectionId: null,
    project: null,
    studentName: '',
    submitToken: '',
    selectedFile: null,
    validationResult: null
};

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize dark mode from localStorage
    initializeDarkMode();
    
    // الحصول على project_id من URL
    const urlParams = new URLSearchParams(window.location.search);
    
    // Check for token first (JWT)
    const token = urlParams.get('token');
    if (token) {
        try {
            // Decode JWT token to get project_id and section_id
            const payload = parseJwt(token);
            const pid = payload.project_id || payload.projectId || payload.project || payload.pid || payload.id;
            const sid = payload.section_id || payload.sectionId || payload.section;
            if (pid) {
                state.projectId = pid;
                state.sectionId = sid; // حفظ section_id من الـ token
                state.submitToken = token; // حفظ الـ token للاستخدام لاحقاً
            } else {
                // Token without project id -> ignore token and fallback
                state.projectId = urlParams.get('project_id');
                state.sectionId = urlParams.get('section_id');
                state.submitToken = '';
            }
        } catch (error) {
            console.error('Error decoding token:', error);
            showError('رابط غير صالح');
            setTimeout(() => window.location.href = '../index.html', 2000);
            return;
        }
    } else {
        // Fallback to direct project_id
        state.projectId = urlParams.get('project_id');
    }
    
    if (!state.projectId) {
        showError('معرف المشروع مفقود');
        setTimeout(() => window.location.href = '../index.html', 2000);
        return;
    }
    
    // تحميل معلومات المشروع
    await loadProjectInfo();
    
    // إعداد Event Listeners
    setupEventListeners();
});

// Helper function to decode JWT token
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('JWT parse error:', error);
        throw new Error('Invalid token format');
    }
}

// ============================================
// Load Project Info
// ============================================

async function loadProjectInfo() {
    showLoading('جاري تحميل معلومات المشروع...');
    
    try {
        // استخدم endpoint العام دائماً، وأرفق التوكن إذا كان صالحاً
        let url = `${API_BASE_URL}/projects/${state.projectId}/detail-public/`;
        const headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        };
        if (state.submitToken) {
            url += `?token=${encodeURIComponent(state.submitToken)}`;
        }
        
        const response = await fetch(url, { 
            method: 'GET',
            headers: headers,
            mode: 'cors',
            credentials: 'omit'
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'فشل تحميل المشروع');
        }
        
        const data = await response.json();
        state.project = data.project;
        
        // عرض معلومات المشروع
        displayProjectInfo(state.project);
        
        hideLoading();
    } catch (error) {
        console.error('Error loading project:', error);
        hideLoading();
        
        // User-friendly error message
        let errorMsg = 'فشل تحميل معلومات المشروع';
        if (error.message.includes('CORS') || error.message.includes('Failed to fetch')) {
            errorMsg += '. يرجى التحقق من اتصالك بالإنترنت والمحاولة مرة أخرى';
        }
        showError(errorMsg);
        
        // Retry button
        setTimeout(() => {
            if (confirm('هل تريد المحاولة مرة أخرى؟')) {
                location.reload();
            }
        }, 1000);
    }
}

function displayProjectInfo(project) {
    // العنوان والموعد النهائي
    document.getElementById('projectTitle').textContent = project.title;
    
    const deadline = new Date(project.deadline);
    const now = new Date();
    const hoursLeft = Math.floor((deadline - now) / (1000 * 60 * 60));
    document.getElementById('projectDeadline').textContent = 
        `⏰ باقي ${hoursLeft} ساعة`;
    
    // المعلومات الأساسية
    document.getElementById('projectSubject').textContent = project.subject || '-';
    document.getElementById('projectGrade').textContent = project.grade_display || '-';
    document.getElementById('projectTeacher').textContent = project.teacher_name || '-';
    
    // عرض الشعبة من الـ token أو من قائمة الشعب
    if (state.sectionId && project.sections && project.sections.length > 0) {
        const section = project.sections.find(s => s.id === state.sectionId);
        document.getElementById('projectSection').textContent = section ? section.name : 'غير محدد';
    } else if (project.sections && project.sections.length > 0) {
        document.getElementById('projectSection').textContent = project.sections[0].name;
    } else {
        document.getElementById('projectSection').textContent = 'غير محدد';
    }
    
    // التعليمات والشروط
    if (project.instructions) {
        document.getElementById('projectInstructions').textContent = project.instructions;
        document.getElementById('instructionsCard').style.display = 'block';
    }
    
    if (project.requirements) {
        document.getElementById('projectRequirements').textContent = project.requirements;
        document.getElementById('requirementsCard').style.display = 'block';
    }
    
    // قيود الملف
    document.getElementById('maxSize').textContent = `${project.max_file_size} MB`;
    document.getElementById('maxSizeText').textContent = `${project.max_file_size} MB`;
    
    // الأنواع المسموحة
    if (project.allowed_file_types && project.allowed_file_types.length > 0) {
        document.getElementById('allowedTypes').textContent = project.allowed_file_types.join(', ');
    } else {
        document.getElementById('allowedTypes').textContent = 'جميع الأنواع';
    }
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Step 1: Student Form
    document.getElementById('studentForm').addEventListener('submit', handleStudentForm);
    
    // Step 2: File Upload
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    document.getElementById('uploadBtn').addEventListener('click', handleFileUpload);
}

// ============================================
// Step 1: Student Info
// ============================================

async function handleStudentForm(e) {
    e.preventDefault();
    
    state.studentName = document.getElementById('studentName').value.trim();
    
    if (!state.studentName) {
        showError('يرجى إدخال الاسم الكامل');
        return;
    }
    
    // التحقق من الطالب قبل الانتقال
    await verifyStudent();
}

// ============================================
// Student Verification
// ============================================

async function verifyStudent() {
    showLoading('جاري التحقق من معلوماتك...');
    
    // عرض شاشة التحقق
    showVerificationProgress();
    
    try {
        const response = await fetch(`${API_BASE_URL}/projects/verify-student/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_name: state.studentName,
                project_id: state.projectId
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            // نجح التحقق
            state.uploadToken = data.upload_token;
            state.studentData = data.student;
            state.projectData = data.project;
            
            // عرض تأكيد البيانات
            showConfirmationScreen(data);
        } else {
            // فشل التحقق
            hideVerificationProgress();
            showVerificationError(data);
        }
        
    } catch (error) {
        console.error('Error verifying student:', error);
        hideLoading();
        hideVerificationProgress();
        showError('حدث خطأ أثناء التحقق. يرجى التأكد من اتصالك بالإنترنت والمحاولة مرة أخرى');
    }
}

function showVerificationProgress() {
    // يمكن إضافة عناصر UI للتحقق
    const form = document.getElementById('studentForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'جاري التحقق...';
}

function hideVerificationProgress() {
    const form = document.getElementById('studentForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = false;
    submitBtn.textContent = 'التالي: رفع الملف';
}

function showConfirmationScreen(data) {
    // إخفاء شاشة الاسم
    hideVerificationProgress();
    
    // إظهار رسالة نجاح
    const successMsg = document.createElement('div');
    successMsg.className = 'verification-success';
    successMsg.innerHTML = `
        <div class="success-icon">✅</div>
        <h3>تم التحقق بنجاح!</h3>
        <div class="student-info">
            <p><strong>الاسم:</strong> ${data.student.name}</p>
            <p><strong>الصف:</strong> ${data.student.grade}</p>
            <p><strong>الشعبة:</strong> ${data.student.section}</p>
        </div>
        <p class="info-text">يمكنك الآن رفع المشروع</p>
    `;
    
    const formCard = document.querySelector('#step1 .form-card');
    formCard.insertBefore(successMsg, formCard.firstChild);
    
    // الانتقال للخطوة التالية بعد ثانية
    setTimeout(() => {
        nextStep();
    }, 1500);
}

function showVerificationError(data) {
    const errorMessages = {
        'student_not_found': {
            title: '❌ الاسم غير موجود',
            message: data.message,
            action: data.action,
            suggestions: data.suggestions
        },
        'telegram_not_verified': {
            title: '⚠️ غير مسجل في التليجرام',
            message: data.message,
            action: data.action_steps,
            link: data.telegram_link
        },
        'already_submitted': {
            title: '✅ تم الرفع مسبقاً',
            message: data.message,
            action: data.action,
            submission: data.submission
        },
        'deadline_expired': {
            title: '⏰ انتهى الموعد النهائي',
            message: data.message,
            action: 'تواصل مع معلمك'
        },
        'invalid_name': {
            title: '❌ الاسم غير صحيح',
            message: data.message,
            action: 'يرجى إدخال الاسم الرباعي كاملاً'
        }
    };
    
    const errorInfo = errorMessages[data.error] || {
        title: '❌ خطأ',
        message: data.message || 'حدث خطأ غير متوقع'
    };
    
    // إنشاء صندوق الخطأ
    const errorBox = document.createElement('div');
    errorBox.className = 'error-box';
    errorBox.innerHTML = `
        <div class="error-icon">${errorInfo.title.split(' ')[0]}</div>
        <h3>${errorInfo.title}</h3>
        <p class="error-message">${errorInfo.message}</p>
        ${errorInfo.suggestions ? `
            <div class="suggestions">
                <h4>هل تقصد أحد هذه الأسماء؟</h4>
                <ul>
                    ${errorInfo.suggestions.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        ${errorInfo.action ? `
            <div class="action-box">
                <strong>ما الحل؟</strong>
                ${Array.isArray(errorInfo.action) ? `
                    <ol>
                        ${errorInfo.action.map(a => `<li>${a}</li>`).join('')}
                    </ol>
                ` : `<p>${errorInfo.action}</p>`}
            </div>
        ` : ''}
        ${errorInfo.link ? `
            <a href="${errorInfo.link}" target="_blank" class="btn btn-primary">الانضمام للقروب</a>
        ` : ''}
        ${errorInfo.submission ? `
            <div class="submission-info">
                <p><strong>الملف:</strong> ${errorInfo.submission.file_name}</p>
                <p><strong>التاريخ:</strong> ${new Date(errorInfo.submission.submitted_at).toLocaleString('ar-EG')}</p>
            </div>
        ` : ''}
        <button class="btn btn-secondary" onclick="location.reload()">إعادة المحاولة</button>
    `;
    
    // إضافة الصندوق للصفحة
    const formCard = document.querySelector('#step1 .form-card');
    formCard.innerHTML = '';
    formCard.appendChild(errorBox);
}

// ============================================
// Step 2: File Upload
// ============================================

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    state.selectedFile = file;
    
    // عرض معلومات الملف
    document.getElementById('dropZone').style.display = 'none';
    document.getElementById('filePreview').classList.remove('hidden');
    
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    
    // بدء التحقق
    validateFile(file);
}

function removeFile() {
    state.selectedFile = null;
    state.validationResult = null;
    
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('filePreview').classList.add('hidden');
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadBtn').disabled = true;
}

async function validateFile(file) {
    document.getElementById('validationProgress').classList.remove('hidden');
    document.getElementById('validationResults').classList.add('hidden');
    
    const steps = ['checkSize', 'checkType', 'checkVirus', 'checkAI'];
    let progress = 0;
    
    // محاكاة التقدم
    const progressInterval = setInterval(() => {
        progress += 5;
        document.getElementById('progressFill').style.width = `${Math.min(progress, 95)}%`;
    }, 200);
    
    // تحديث حالة الخطوات
    steps.forEach((step, index) => {
        setTimeout(() => {
            document.getElementById(step).classList.add('checking');
        }, index * 500);
    });
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/projects/${state.projectId}/validate/`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        clearInterval(progressInterval);
        document.getElementById('progressFill').style.width = '100%';
        
        state.validationResult = data;
        
        // عرض النتائج
        displayValidationResults(data);
        
        // تفعيل زر الرفع إذا كان الملف صالحاً
        if (data.valid) {
            document.getElementById('uploadBtn').disabled = false;
        }
        
    } catch (error) {
        console.error('Error validating file:', error);
        clearInterval(progressInterval);
        showError('فشل التحقق من الملف');
        
        // إظهار خطأ في جميع الخطوات
        steps.forEach(step => {
            const el = document.getElementById(step);
            el.classList.remove('checking');
            el.classList.add('error');
        });
    }
}

function displayValidationResults(data) {
    document.getElementById('validationProgress').classList.add('hidden');
    
    const resultsDiv = document.getElementById('validationResults');
    resultsDiv.classList.remove('hidden');
    resultsDiv.innerHTML = '';
    
    // الأخطاء
    if (data.errors && data.errors.length > 0) {
        const errorsSection = document.createElement('div');
        errorsSection.className = 'result-section';
        errorsSection.innerHTML = '<h4>❌ أخطاء:</h4>';
        
        data.errors.forEach(error => {
            const item = document.createElement('div');
            item.className = 'result-item error';
            item.innerHTML = `
                <span class="icon">❌</span>
                <span class="text">${error.message}</span>
            `;
            errorsSection.appendChild(item);
        });
        
        resultsDiv.appendChild(errorsSection);
    }
    
    // التحذيرات
    if (data.warnings && data.warnings.length > 0) {
        const warningsSection = document.createElement('div');
        warningsSection.className = 'result-section';
        warningsSection.innerHTML = '<h4>⚠️ تحذيرات:</h4>';
        
        data.warnings.forEach(warning => {
            const item = document.createElement('div');
            item.className = 'result-item warning';
            item.innerHTML = `
                <span class="icon">⚠️</span>
                <span class="text">${warning.message}</span>
            `;
            warningsSection.appendChild(item);
        });
        
        resultsDiv.appendChild(warningsSection);
    }
    
    // فحص الفيروسات
    if (data.virus_scan) {
        const virusSection = document.createElement('div');
        virusSection.className = 'result-section';
        
        if (data.virus_scan.clean) {
            virusSection.innerHTML = `
                <div class="result-item success">
                    <span class="icon">✅</span>
                    <span class="text">الملف خالي من الفيروسات</span>
                </div>
            `;
        } else if (data.virus_scan.scanned === false) {
            virusSection.innerHTML = `
                <div class="result-item warning">
                    <span class="icon">⚠️</span>
                    <span class="text">${data.virus_scan.message}</span>
                </div>
            `;
        }
        
        resultsDiv.appendChild(virusSection);
    }
    
    // التحقق بالذكاء الاصطناعي
    if (data.ai_check && data.ai_check.checked) {
        const aiSection = document.createElement('div');
        aiSection.className = 'result-section';
        aiSection.innerHTML = '<h4>🤖 التحقق بالذكاء الاصطناعي:</h4>';
        
        const compliance = data.ai_check.compliant ? 'success' : 'warning';
        const icon = data.ai_check.compliant ? '✅' : '⚠️';
        
        aiSection.innerHTML += `
            <div class="result-item ${compliance}">
                <span class="icon">${icon}</span>
                <span class="text">
                    ${data.ai_check.message}
                    <br><small>مستوى الثقة: ${data.ai_check.confidence}%</small>
                </span>
            </div>
        `;
        
        // الاقتراحات
        if (data.ai_check.suggestions && data.ai_check.suggestions.length > 0) {
            data.ai_check.suggestions.forEach(suggestion => {
                aiSection.innerHTML += `
                    <div class="result-item warning">
                        <span class="icon">💡</span>
                        <span class="text">${suggestion}</span>
                    </div>
                `;
            });
        }
        
        resultsDiv.appendChild(aiSection);
    }
    
    // رسالة النجاح الشاملة
    if (data.valid) {
        const successSection = document.createElement('div');
        successSection.className = 'result-section';
        successSection.innerHTML = `
            <div class="result-item success">
                <span class="icon">✅</span>
                <span class="text"><strong>الملف جاهز للرفع!</strong></span>
            </div>
        `;
        resultsDiv.appendChild(successSection);
    }
}

async function handleFileUpload() {
    if (!state.selectedFile) {
        showError('يرجى اختيار ملف أولاً');
        return;
    }
    
    if (!state.uploadToken) {
        showError('انتهت صلاحية الجلسة. يرجى إعادة المحاولة');
        setTimeout(() => location.reload(), 2000);
        return;
    }
    
    showLoading('جاري رفع الملف...');
    
    try {
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        formData.append('project_id', state.projectId);
        formData.append('upload_token', state.uploadToken);
        formData.append('student_name', state.studentName);
        if (state.sectionId) {
            formData.append('section_id', state.sectionId);
        }
        
        const response = await fetch(`${API_BASE_URL}/projects/submissions/upload/`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'فشل رفع الملف');
        }
        
        hideLoading();
        
        // عرض تفاصيل التسليم
        displaySubmissionDetails(data.submission);
        
        nextStep();
        
    } catch (error) {
        console.error('Error uploading file:', error);
        hideLoading();
        showError(error.message);
    }
}

// ============================================
// Step 4: Success
// ============================================

function displaySubmissionDetails(submission) {
    const detailsDiv = document.getElementById('submissionDetails');
    detailsDiv.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">اسم الملف:</span>
            <span class="detail-value">${submission.file_name}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">الحجم:</span>
            <span class="detail-value">${formatFileSize(submission.file_size)}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">تاريخ التسليم:</span>
            <span class="detail-value">${new Date(submission.submitted_at).toLocaleString('ar-EG')}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">الحالة:</span>
            <span class="detail-value">قيد المراجعة</span>
        </div>
    `;
}

// ============================================
// Navigation
// ============================================

function nextStep() {
    if (state.currentStep < 3) {
        // إخفاء الخطوة الحالية
        document.getElementById(`step${state.currentStep}`).classList.remove('active');
        document.querySelector(`.step[data-step="${state.currentStep}"]`).classList.remove('active');
        document.querySelector(`.step[data-step="${state.currentStep}"]`).classList.add('completed');
        
        // إظهار الخطوة التالية
        state.currentStep++;
        document.getElementById(`step${state.currentStep}`).classList.add('active');
        document.querySelector(`.step[data-step="${state.currentStep}"]`).classList.add('active');
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function prevStep() {
    if (state.currentStep > 1) {
        // إخفاء الخطوة الحالية
        document.getElementById(`step${state.currentStep}`).classList.remove('active');
        document.querySelector(`.step[data-step="${state.currentStep}"]`).classList.remove('active');
        
        // إظهار الخطوة السابقة
        state.currentStep--;
        document.getElementById(`step${state.currentStep}`).classList.add('active');
        document.querySelector(`.step[data-step="${state.currentStep}"]`).classList.remove('completed');
        document.querySelector(`.step[data-step="${state.currentStep}"]`).classList.add('active');
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// ============================================
// UI Helpers
// ============================================

function showLoading(text = 'جاري التحميل...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function showError(message) {
    alert('❌ ' + message);
}

function showSuccess(message) {
    alert('✅ ' + message);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================
// Dark Mode Support
// ============================================

function initializeDarkMode() {
    // Get dark mode preference from localStorage
    const darkMode = localStorage.getItem('darkMode') === 'true';
    
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
    
    // Listen for storage changes (if changed from another tab)
    window.addEventListener('storage', (e) => {
        if (e.key === 'darkMode') {
            if (e.newValue === 'true') {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
        }
    });
}
