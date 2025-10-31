/**
 * نظام إضافة الطلاب الاحترافي
 * Professional Student Management System
 */

class StudentManagementSystem {
    constructor() {
        this.apiUrl = window.API_BASE || 'http://localhost:8000/api';
        this.students = [];
        this.currentSectionId = null;
        this.init();
    }

    init() {
        console.log('🚀 StudentManagementSystem initialized');
        console.log('📡 API URL:', this.apiUrl);
        
        // Check authentication - try both token names
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) {
            console.error('❌ No authentication token found');
            console.log('📋 localStorage keys:', Object.keys(localStorage));
            this.showToast('يرجى تسجيل الدخول أولاً', 'error');
            setTimeout(() => {
                window.location.href = '/pages/login.html';
            }, 2000);
            return;
        }
        
        console.log('✅ Token found:', token.substring(0, 20) + '...');
        
        this.setupEventListeners();
        this.loadGrades();
        this.applyTheme();
    }

    // ==================== Event Listeners ====================
    
    setupEventListeners() {
        console.log('🎧 Setting up event listeners...');
        
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
        
        // Tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });
        
        // Manual form - Grade change listener
        const gradeSelect = document.getElementById('gradeSelect');
        const gradeSelectExcel = document.getElementById('gradeSelectExcel');
        
        if (gradeSelect) {
            console.log('✅ gradeSelect found, adding change listener');
            gradeSelect.addEventListener('change', (e) => {
                console.log('🔔 Grade changed to:', e.target.value);
                this.loadSections(e.target.value, 'sectionSelect');
            });
        } else {
            console.error('❌ gradeSelect not found!');
        }
        
        if (gradeSelectExcel) {
            console.log('✅ gradeSelectExcel found, adding change listener');
            gradeSelectExcel.addEventListener('change', (e) => {
                console.log('🔔 Grade (Excel) changed to:', e.target.value);
                this.loadSections(e.target.value, 'sectionSelectExcel');
            });
        } else {
            console.error('❌ gradeSelectExcel not found!');
        }
        
        document.getElementById('studentName').addEventListener('input', () => this.validateName());
        document.getElementById('studentPhone').addEventListener('input', () => this.validatePhone());
        
        document.getElementById('manualForm').addEventListener('submit', (e) => this.handleManualSubmit(e));
        document.getElementById('addAndContinue').addEventListener('click', () => this.addStudent(true));
        document.getElementById('saveAllBtn').addEventListener('click', () => this.saveAll());
        
        // Excel upload
        const fileInput = document.getElementById('fileInput');
        const uploadZone = document.getElementById('uploadZone');
        
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                this.handleFileSelect({target: fileInput});
            }
        });
        
        document.getElementById('downloadTemplate').addEventListener('click', () => this.downloadTemplate());
        
        console.log('✅ All event listeners set up successfully');
    }

    // ==================== Theme ====================
    
    applyTheme() {
        const theme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', theme);
        this.updateThemeButton(theme);
    }

    toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeButton(newTheme);
    }

    updateThemeButton(theme) {
        const icon = document.getElementById('themeIcon');
        const text = document.getElementById('themeText');
        
        if (theme === 'dark') {
            icon.textContent = '☀️';
            text.textContent = 'وضع فاتح';
        } else {
            icon.textContent = '🌙';
            text.textContent = 'وضع داكن';
        }
    }

    // ==================== Tabs ====================
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // Update content sections
        document.getElementById('manualSection').classList.toggle('active', tabName === 'manual');
        document.getElementById('excelSection').classList.toggle('active', tabName === 'excel');
    }

    // ==================== API Calls ====================
    
    async loadGrades() {
        try {
            console.log('📚 Loading grades from API...');
            const token = localStorage.getItem('access_token') || localStorage.getItem('token');
            
            const url = `${this.apiUrl}/sections/my-grades/`;
            console.log('🔗 API URL:', url);
            
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('📡 Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ API Error:', response.status, errorText);
                throw new Error(`API Error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('📊 Response data:', data);
            
            if (data.grades && data.grades.length > 0) {
                console.log('✅ Grades found:', data.grades.length);
                this.populateGrades(data.grades);
            } else {
                console.warn('⚠️ No grades found');
                this.showToast('لا توجد صفوف متاحة. يرجى إنشاء صفوف أولاً.', 'warning');
            }
        } catch (error) {
            console.error('❌ Error loading grades:', error);
            this.showToast('خطأ في تحميل الصفوف. تحقق من اتصالك بالإنترنت.', 'error');
        }
    }

    populateGrades(grades) {
        console.log('📝 Populating grades in select elements...');
        console.log('📊 Full grades data:', JSON.stringify(grades, null, 2));
        
        const select1 = document.getElementById('gradeSelect');
        const select2 = document.getElementById('gradeSelectExcel');
        
        if (!select1 || !select2) {
            console.error('❌ Grade select elements not found!');
            return;
        }
        
        console.log('✅ Select elements found');
        
        // Clear existing options (keep placeholder)
        select1.innerHTML = '<option value="">اختر الصف</option>';
        select2.innerHTML = '<option value="">اختر الصف</option>';
        
        grades.forEach((grade, index) => {
            console.log(`\n  📚 Grade ${index + 1}:`, {
                id: grade.id,
                name: grade.display_name,
                sections: grade.sections
            });
            
            const option1 = new Option(grade.display_name, grade.id);
            const option2 = new Option(grade.display_name, grade.id);
            
            const sectionsData = JSON.stringify(grade.sections || []);
            console.log(`  💾 Sections data to save:`, sectionsData);
            
            option1.dataset.sections = sectionsData;
            option2.dataset.sections = sectionsData;
            
            select1.add(option1);
            select2.add(option2);
            
            // Verify it was saved
            console.log(`  ✓ Saved in option dataset:`, option1.dataset.sections);
        });
        
        console.log('\n✅ Grades populated successfully');
    }

    loadSections(gradeId, selectId) {
        console.log(`📖 Loading sections for grade ${gradeId} into ${selectId}`);
        const select = document.getElementById(selectId);
        
        if (!select) {
            console.error(`❌ Section select element ${selectId} not found!`);
            return;
        }
        
        select.innerHTML = '<option value="">اختر الشعبة</option>';
        select.disabled = !gradeId;
        
        if (gradeId) {
            const gradeSelect = selectId.includes('Excel') ? document.getElementById('gradeSelectExcel') : document.getElementById('gradeSelect');
            
            if (!gradeSelect || !gradeSelect.selectedOptions[0]) {
                console.error('❌ Grade select or selected option not found');
                return;
            }
            
            const sectionsData = gradeSelect.selectedOptions[0].dataset.sections;
            console.log('📊 Sections data from dataset:', sectionsData);
            
            const sections = JSON.parse(sectionsData || '[]');
            console.log(`✅ Found ${sections.length} sections`);
            
            sections.forEach(section => {
                console.log(`  📖 Adding section: ${section.section_name}`);
                select.add(new Option(section.section_name, section.id));
            });
            
            select.disabled = false;
            console.log('✅ Sections loaded successfully');
        }
    }

    // ==================== Validation ====================
    
    validateName() {
        const input = document.getElementById('studentName');
        const feedback = document.getElementById('nameFeedback');
        const value = input.value.trim();
        
        if (!value) {
            this.showFeedback(feedback, '', '');
            return false;
        }
        
        const arabicPattern = /^[\u0600-\u06FF\s]+$/;
        if (!arabicPattern.test(value)) {
            this.showFeedback(feedback, '❌ يجب أن يكون الاسم بالعربية فقط', 'error');
            return false;
        }
        
        const parts = value.split(/\s+/).filter(p => p);
        if (parts.length < 4) {
            this.showFeedback(feedback, `⚠️ الاسم يجب أن يكون رباعياً (${parts.length}/4)`, 'warning');
            return false;
        }
        
        this.showFeedback(feedback, '✅ الاسم صحيح', 'success');
        return true;
    }

    validatePhone() {
        const input = document.getElementById('studentPhone');
        const feedback = document.getElementById('phoneFeedback');
        const value = input.value.trim();
        
        if (!value) {
            this.showFeedback(feedback, '', '');
            return false;
        }
        
        const phonePattern = /^(05|5)\d{8}$/;
        if (!phonePattern.test(value.replace(/[^\d]/g, ''))) {
            this.showFeedback(feedback, '❌ رقم الجوال غير صحيح', 'error');
            return false;
        }
        
        this.showFeedback(feedback, '✅ رقم صحيح', 'success');
        return true;
    }

    showFeedback(element, message, type) {
        element.textContent = message;
        element.className = `feedback ${type}`;
        element.style.display = message ? 'block' : 'none';
    }

    // ==================== Manual Add ====================
    
    handleManualSubmit(e) {
        e.preventDefault();
        this.addStudent(false);
    }

    addStudent(continueAdding) {
        const name = document.getElementById('studentName').value.trim();
        const phone = document.getElementById('studentPhone').value.trim();
        const sectionId = document.getElementById('sectionSelect').value;
        
        if (!this.validateName() || !this.validatePhone() || !sectionId) {
            this.showToast('يرجى إكمال جميع الحقول بشكل صحيح', 'error');
            return;
        }
        
        // تنسيق رقم الجوال
        const formattedPhone = phone.startsWith('05') ? phone : '0' + phone.replace(/^5/, '');
        
        this.students.push({
            full_name: name,
            phone: formattedPhone
        });
        
        this.currentSectionId = parseInt(sectionId);
        this.renderStudentsList();
        this.showToast(`تم إضافة ${name} بنجاح`, 'success');
        
        if (continueAdding) {
            document.getElementById('studentName').value = '';
            document.getElementById('studentPhone').value = '';
            document.getElementById('studentName').focus();
            this.showFeedback(document.getElementById('nameFeedback'), '', '');
            this.showFeedback(document.getElementById('phoneFeedback'), '', '');
        }
    }

    renderStudentsList() {
        const container = document.getElementById('studentsList');
        const preview = document.getElementById('studentsPreview');
        const count = document.getElementById('studentsCount');
        
        preview.style.display = this.students.length > 0 ? 'block' : 'none';
        count.textContent = this.students.length;
        
        container.innerHTML = this.students.map((student, index) => `
            <div class="student-card">
                <div class="student-number">${index + 1}</div>
                <div class="student-info">
                    <div class="name">${student.full_name}</div>
                    <div class="phone">📱 ${student.phone}</div>
                </div>
                <div class="student-actions">
                    <button class="btn-icon delete" onclick="sms.removeStudent(${index})">
                        🗑️
                    </button>
                </div>
            </div>
        `).join('');
    }

    removeStudent(index) {
        if (confirm(`هل تريد حذف ${this.students[index].full_name}؟`)) {
            this.students.splice(index, 1);
            this.renderStudentsList();
            this.showToast('تم الحذف بنجاح', 'success');
        }
    }

    async saveAll() {
        if (this.students.length === 0) {
            this.showToast('لا يوجد طلاب لحفظهم', 'error');
            return;
        }
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        try {
            this.showLoadingModal(true);
            this.updateProgress(0);
            
            const response = await fetch(`${this.apiUrl}/sections/students/add-manually/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    section_id: this.currentSectionId,
                    students: this.students
                })
            });
            
            const data = await response.json();
            
            this.updateProgress(100);
            
            setTimeout(() => {
                this.showLoadingModal(false);
                
                if (data.success) {
                    this.showSuccessModal(data);
                    this.students = [];
                    this.renderStudentsList();
                    document.getElementById('manualForm').reset();
                } else {
                    this.showToast(data.message || 'حدث خطأ', 'error');
                }
            }, 500);
            
        } catch (error) {
            this.showLoadingModal(false);
            console.error('Error saving students:', error);
            this.showToast('حدث خطأ في الحفظ', 'error');
        }
    }

    // ==================== Excel Upload ====================
    
    async handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const sectionId = document.getElementById('sectionSelectExcel').value;
        if (!sectionId) {
            this.showToast('يرجى اختيار الشعبة أولاً', 'error');
            return;
        }
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const formData = new FormData();
        formData.append('file', file);
        formData.append('section_id', sectionId);
        
        try {
            this.showLoadingModal(true);
            this.updateProgress(30);
            
            const response = await fetch(`${this.apiUrl}/sections/students/upload-excel/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            this.updateProgress(80);
            const data = await response.json();
            this.updateProgress(100);
            
            setTimeout(() => {
                this.showLoadingModal(false);
                
                if (data.success) {
                    this.showSuccessModal(data);
                    document.getElementById('fileInput').value = '';
                } else {
                    this.showToast(data.message || 'حدث خطأ في رفع الملف', 'error');
                }
            }, 500);
            
        } catch (error) {
            this.showLoadingModal(false);
            console.error('Error uploading Excel:', error);
            this.showToast('حدث خطأ في رفع الملف', 'error');
        }
    }

    async downloadTemplate() {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        
        try {
            const response = await fetch(`${this.apiUrl}/sections/students/excel-template/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'template_students.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showToast('تم تحميل النموذج بنجاح', 'success');
        } catch (error) {
            console.error('Error downloading template:', error);
            this.showToast('حدث خطأ في تحميل النموذج', 'error');
        }
    }

    // ==================== UI Helpers ====================
    
    showLoadingModal(show) {
        const modal = document.getElementById('loadingModal');
        if (show) {
            modal.classList.add('active');
        } else {
            modal.classList.remove('active');
        }
    }

    updateProgress(percent) {
        const fill = document.getElementById('progressFill');
        const text = document.getElementById('progressText');
        fill.style.width = percent + '%';
        text.textContent = percent + '%';
    }

    showSuccessModal(data) {
        const stats = data.stats;
        let message = `تم إضافة ${stats.added} طالب بنجاح`;
        
        if (stats.errors > 0) {
            message += `\n⚠️ ${stats.errors} سجل يحتوي على أخطاء`;
        }
        
        if (stats.duplicates > 0) {
            message += `\n🔄 ${stats.duplicates} طالب مكرر`;
        }
        
        alert(message);
        this.playConfetti();
    }

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">${type === 'success' ? '✅' : '❌'}</div>
            <div class="toast-message">
                <div class="title">${type === 'success' ? 'نجح' : 'خطأ'}</div>
                <div class="text">${message}</div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    playConfetti() {
        const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#10b981'];
        const count = 50;
        
        for (let i = 0; i < count; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
                document.body.appendChild(confetti);
                
                setTimeout(() => confetti.remove(), 3000);
            }, i * 30);
        }
    }
}

// Initialize
const sms = new StudentManagementSystem();
window.sms = sms;

// Add slide out animation for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
