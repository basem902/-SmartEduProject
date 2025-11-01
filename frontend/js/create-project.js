// Create Project Wizard JavaScript
// ✅ API_BASE يُعرّف في config.js - لا تعرّفه هنا!

// State Management
let currentStep = 1;
const totalSteps = 6;
let projectData = {
    title: '',
    subject: '',
    description: '',
    gradeId: null,
    sections: [],
    instructions: '',
    requirements: '',
    tips: '',
    files: {
        video: null,
        pdfs: [],
        docs: [],
        links: []
    },
    settings: {
        allowedFileTypes: ['pdf', 'doc'],
        maxFileSize: 10,
        maxGrade: 100,
        startDate: null,
        deadline: null,
        allowLateSubmission: true,
        sendReminder: true,
        aiCheck: false
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Create Project Wizard Loaded');
    
    // Check authentication
    const token = localStorage.getItem('access_token');
    if (!token) {
        showAlert('يجب تسجيل الدخول أولاً', 'error');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
        return;
    }
    
    initializeDates();
    loadGrades();
    loadTeacherSubjects(); // ✅ NEW: Load subjects
    updateButtonsVisibility();
    
    // ✅ NEW: Load draft if exists
    loadDraftFromStorage();
    
    // ✅ NEW: Setup auto-save
    setupAutoSave();
    
    // ✅ NEW: Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // ✅ NEW: Load user preferences
    loadUserPreferences();
});

// Initialize default dates
function initializeDates() {
    const now = new Date();
    const startInput = document.getElementById('startDate');
    const deadlineInput = document.getElementById('deadline');
    
    // Start date: tomorrow
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    startInput.value = formatDateTimeLocal(tomorrow);
    
    // Deadline: 30 days from now
    const deadline = new Date(now);
    deadline.setDate(deadline.getDate() + 30);
    deadlineInput.value = formatDateTimeLocal(deadline);
}

function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Navigation
function nextStep() {
    if (validateCurrentStep()) {
        saveCurrentStepData();
        if (currentStep < totalSteps) {
            currentStep++;
            updateWizard();
        }
    }
}

function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        updateWizard();
    }
}

function updateWizard() {
    // Update steps
    document.querySelectorAll('.wizard-step').forEach(step => {
        step.classList.remove('active');
    });
    document.querySelector(`.wizard-step[data-step="${currentStep}"]`).classList.add('active');
    
    // Update progress circles
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNum = index + 1;
        const circle = step.querySelector('.step-circle');
        const label = step.querySelector('.step-label');
        
        circle.classList.remove('active', 'completed');
        label.classList.remove('active');
        
        if (stepNum < currentStep) {
            circle.classList.add('completed');
            circle.textContent = '✓';
        } else if (stepNum === currentStep) {
            circle.classList.add('active');
            label.classList.add('active');
            circle.textContent = stepNum;
        } else {
            circle.textContent = stepNum;
        }
    });
    
    // Update progress bar
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
    
    // Update buttons
    updateButtonsVisibility();
    
    // Special actions for specific steps
    if (currentStep === 6) {
        populateReviewStep();
    }
}

function updateButtonsVisibility() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    prevBtn.style.display = currentStep === 1 ? 'none' : 'inline-flex';
    nextBtn.style.display = currentStep === totalSteps ? 'none' : 'inline-flex';
    submitBtn.style.display = currentStep === totalSteps ? 'inline-flex' : 'none';
}

// Validation
function validateCurrentStep() {
    let isValid = true;
    let errorMessage = '';
    
    switch(currentStep) {
        case 1:
            // Step 1: Grade, Sections, Subject
            const grade = document.getElementById('gradeSelect').value;
            const selectedSections = document.querySelectorAll('input[name="section"]:checked');
            const subject = document.getElementById('projectSubject').value;
            
            if (!grade) {
                errorMessage = 'يجب اختيار الصف الدراسي';
                isValid = false;
            } else if (selectedSections.length === 0) {
                errorMessage = 'يجب اختيار شعبة واحدة على الأقل';
                isValid = false;
            } else if (!subject) {
                errorMessage = 'المادة الدراسية مطلوبة';
                isValid = false;
            }
            break;
            
        case 2:
            // Step 2: Project Title & Description
            const title = document.getElementById('projectTitle').value.trim();
            
            if (!title || title.length < 3) {
                errorMessage = 'اسم المشروع مطلوب (3 أحرف على الأقل)';
                isValid = false;
            }
            break;
            
        case 3:
            const instructions = document.getElementById('projectInstructions').value.trim();
            const requirements = document.getElementById('projectRequirements').value.trim();
            
            if (!instructions) {
                errorMessage = 'التعليمات مطلوبة';
                isValid = false;
            } else if (!requirements) {
                errorMessage = 'الشروط مطلوبة';
                isValid = false;
            }
            break;
            
        case 5:
            const startDate = document.getElementById('startDate').value;
            const deadline = document.getElementById('deadline').value;
            const fileTypes = document.querySelectorAll('input[name="fileTypes"]:checked');
            
            if (!startDate || !deadline) {
                errorMessage = 'يجب تحديد تاريخ البداية والنهاية';
                isValid = false;
            } else if (new Date(deadline) <= new Date(startDate)) {
                errorMessage = 'الموعد النهائي يجب أن يكون بعد تاريخ البداية';
                isValid = false;
            } else if (fileTypes.length === 0) {
                errorMessage = 'يجب اختيار نوع ملف واحد على الأقل';
                isValid = false;
            }
            break;
    }
    
    if (!isValid) {
        showAlert(errorMessage, 'error');
    }
    
    return isValid;
}

function saveCurrentStepData() {
    switch(currentStep) {
        case 1:
            // Step 1: Grade, Sections, Subject
            projectData.gradeId = parseInt(document.getElementById('gradeSelect').value);
            projectData.sections = Array.from(document.querySelectorAll('input[name="section"]:checked'))
                .map(cb => parseInt(cb.value))
                .filter(id => !isNaN(id)); // Remove any NaN values
            projectData.subject = document.getElementById('projectSubject').value;
            console.log('Saved grade:', projectData.gradeId);
            console.log('Saved sections:', projectData.sections);
            console.log('Saved subject:', projectData.subject);
            break;
            
        case 2:
            // Step 2: Project Title & Description
            projectData.title = document.getElementById('projectTitle').value.trim();
            projectData.description = document.getElementById('projectDescription').value.trim();
            console.log('Saved title:', projectData.title);
            break;
            
        case 3:
            // ✅ Sync checklists to hidden textareas before saving
            if (typeof updateHiddenTextarea === 'function') {
                updateHiddenTextarea('instructions');
                updateHiddenTextarea('requirements');
                updateHiddenTextarea('tips');
            }
            
            projectData.instructions = document.getElementById('projectInstructions').value.trim();
            projectData.requirements = document.getElementById('projectRequirements').value.trim();
            projectData.tips = document.getElementById('projectTips').value.trim();
            
            console.log('✅ Saved instructions:', projectData.instructions);
            console.log('✅ Saved requirements:', projectData.requirements);
            console.log('✅ Saved tips:', projectData.tips);
            break;
            
        case 4:
            // Step 4: Files (already stored in projectData.files)
            // Just log for confirmation
            console.log('✅ Step 4 - Files status:');
            console.log('  Video:', projectData.files.video ? projectData.files.video.name : 'None');
            console.log('  PDFs:', projectData.files.pdfs.length);
            console.log('  Docs:', projectData.files.docs.length);
            console.log('  Links:', projectData.files.links.length);
            console.log('  All links:', projectData.files.links);
            break;
            
        case 5:
            projectData.settings.maxGrade = document.getElementById('maxGrade').value;
            projectData.settings.startDate = document.getElementById('startDate').value;
            projectData.settings.deadline = document.getElementById('deadline').value;
            projectData.settings.allowLateSubmission = document.getElementById('allowLateSubmission').checked;
            projectData.settings.sendReminder = document.getElementById('sendReminder').checked;
            projectData.settings.aiCheck = document.getElementById('aiCheck').checked;
            
            // ✅ Save allowed file types
            projectData.settings.allowedFileTypes = Array.from(document.querySelectorAll('input[name="fileTypes"]:checked'))
                .map(cb => cb.value);
            
            // ✅ Save max file size
            const maxFileSizeInput = document.getElementById('maxFileSize');
            if (maxFileSizeInput) {
                projectData.settings.maxFileSize = parseInt(maxFileSizeInput.value) || 10;
            }
            
            // ✅ Save Telegram settings
            projectData.telegram = {
                sendToTelegram: document.getElementById('sendToTelegram').checked,
                pinMessage: document.getElementById('pinMessage').checked,
                sendFiles: document.getElementById('sendFiles').checked
            };
            
            console.log('Saved settings:', projectData.settings);
            console.log('Saved allowedFileTypes:', projectData.settings.allowedFileTypes);
            console.log('Telegram settings:', projectData.telegram);
            break;
    }
}

// ✅ NEW: Load Teacher Subjects from Database
async function loadTeacherSubjects() {
    try {
        const data = await api.getTeacherSubjects();
        const select = document.getElementById('projectSubject');
        select.innerHTML = '<option value="">اختر المادة...</option>';
        
        data.subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject;
            option.textContent = subject;
            select.appendChild(option);
        });
        
        console.log('✅ Subjects loaded:', data.subjects.length);
    } catch (error) {
        console.error('Error loading subjects:', error);
        // Use default subjects if API fails
        const defaultSubjects = ['المهارات الرقمية', 'العلوم', 'الرياضيات'];
        const select = document.getElementById('projectSubject');
        select.innerHTML = '<option value="">اختر المادة...</option>';
        defaultSubjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject;
            option.textContent = subject;
            select.appendChild(option);
        });
    }
}

// Load Grades (with DataCache support)
async function loadGrades() {
    try {
        console.log('📚 Loading grades...');
        
        // استخدام DataCache إذا كان متوفراً
        let data;
        if (window.dataCache) {
            console.log('⚡ Using DataCache for faster loading');
            data = await window.dataCache.getGrades();
        } else {
            console.log('📡 Using API directly');
            data = await api.getMyGrades();
        }
        
        const select = document.getElementById('gradeSelect');
        select.innerHTML = '<option value="">اختر الصف...</option>';
        
        if (data.grades && data.grades.length > 0) {
            data.grades.forEach(grade => {
                const option = document.createElement('option');
                option.value = grade.id;
                option.textContent = grade.display_name;
                select.appendChild(option);
            });
            console.log('✅ Grades loaded:', data.grades.length);
        } else {
            console.warn('No grades found for teacher');
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'لا توجد صفوف مضافة';
            select.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading grades:', error);
        showAlert('فشل تحميل الصفوف', 'error');
    }
}

// Load Sections (with DataCache support)
async function loadSections() {
    const gradeId = document.getElementById('gradeSelect').value;
    const container = document.getElementById('sectionsContainer');
    
    if (!gradeId) {
        container.innerHTML = '<p style="color: var(--text-muted);">يرجى اختيار صف أولاً</p>';
        updateTelegramTargets(); // Update Telegram targets
        return;
    }
    
    try {
        console.log(`📖 Loading sections for grade ${gradeId}...`);
        
        // استخدام DataCache إذا كان متوفراً
        let data;
        if (window.dataCache) {
            console.log('⚡ Using DataCache for sections');
            data = await window.dataCache.getSections(gradeId);
        } else {
            console.log('📡 Using API directly');
            data = await api.getGradeSections(gradeId);
        }
        
        console.log('Sections loaded:', data.sections);
        const container = document.getElementById('sectionsList');
        container.innerHTML = '';
        
        data.sections.forEach(section => {
            const item = document.createElement('label');
            item.className = 'checkbox-item';
            const studentCount = section.registrations_count || section.total_students || 0;
            
            // ✅ Check if section was previously selected
            const wasSelected = projectData.sections && projectData.sections.includes(section.id);
            const checkedAttr = wasSelected ? 'checked' : '';
            
            console.log(`Section ${section.section_name}: ${studentCount} students, wasSelected: ${wasSelected}`);
            item.innerHTML = `
                <input type="checkbox" name="section" value="${section.id}" ${checkedAttr} onchange="updateSectionStats(); updateTelegramTargets();">
                <div class="checkbox-label">
                    ${section.section_name}
                    <span class="checkbox-info">${studentCount} طالب</span>
                </div>
            `;
            container.appendChild(item);
        });
        
        document.getElementById('sectionsGroup').style.display = 'block';
        document.getElementById('subjectGroup').style.display = 'block'; // ✅ Show subject field
        updateSectionStats();
        
        // ✅ Update "Select All" checkbox state
        const allCheckboxes = document.querySelectorAll('input[name="section"]');
        const allChecked = allCheckboxes.length > 0 && Array.from(allCheckboxes).every(cb => cb.checked);
        const selectAllCheckbox = document.getElementById('selectAllSections');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = allChecked;
        }
        
        // ✅ Update Telegram targets after loading sections
        setTimeout(() => updateTelegramTargets(), 100);
    } catch (error) {
        console.error('Error loading sections:', error);
        showAlert('فشل تحميل الشُعب', 'error');
    }
}

function toggleAllSections() {
    const selectAll = document.getElementById('selectAllSections').checked;
    document.querySelectorAll('input[name="section"]').forEach(cb => {
        cb.checked = selectAll;
    });
    
    // Update projectData immediately
    projectData.sections = Array.from(document.querySelectorAll('input[name="section"]:checked'))
        .map(cb => parseInt(cb.value))
        .filter(id => !isNaN(id));
    
    console.log('Toggled all sections:', projectData.sections);
    
    updateSectionStats();
    updateTelegramTargets();
}

function updateSectionStats() {
    const checkboxes = document.querySelectorAll('input[name="section"]');
    let totalStudents = 0;
    let selectedCount = 0;
    
    checkboxes.forEach(cb => {
        if (cb.checked) {
            selectedCount++;
            const info = cb.closest('.checkbox-item')?.querySelector('.checkbox-info');
            if (info && info.textContent) {
                const match = info.textContent.match(/\d+/);
                if (match && match[0]) {
                    const count = parseInt(match[0]);
                    totalStudents += count;
                }
            }
        }
    });
    
    // ✅ Update projectData.sections whenever stats are updated
    projectData.sections = Array.from(document.querySelectorAll('input[name="section"]:checked'))
        .map(cb => parseInt(cb.value))
        .filter(id => !isNaN(id));
    
    console.log(`Selected: ${selectedCount} sections (IDs: ${projectData.sections.join(', ')}), Total: ${totalStudents} students`);
    
    if (selectedCount > 0) {
        document.getElementById('selectionStats').style.display = 'block';
        document.getElementById('totalStudents').textContent = totalStudents;
        document.getElementById('selectedSections').textContent = selectedCount;
    } else {
        document.getElementById('selectionStats').style.display = 'none';
    }
}

// AI Generation Functions
async function generateDescription() {
    const title = document.getElementById('projectTitle').value.trim();
    const subject = document.getElementById('projectSubject').value;
    
    if (!title || !subject) {
        showAlert('يجب إدخال اسم المشروع والمادة أولاً', 'error');
        return;
    }
    
    const btn = event.target.closest('.ai-button');
    const icon = document.getElementById('aiDescIcon');
    const text = document.getElementById('aiDescText');
    
    btn.disabled = true;
    icon.innerHTML = '<div class="spinner"></div>';
    text.textContent = 'جاري التوليد...';
    
    try {
        const data = await api.generateAI({
            content_type: 'instructions',
            context: {
                project_name: title,
                subject: subject,
                purpose: 'وصف المشروع'
            }
        });
        console.log('AI Response:', data);
        
        // Extract text from nested structure
        let generatedText = '';
        if (data.content && typeof data.content === 'object' && data.content.generated_text) {
            generatedText = data.content.generated_text;
        } else if (typeof data.generated_text === 'string') {
            generatedText = data.generated_text;
        } else if (typeof data.text === 'string') {
            generatedText = data.text;
        }
        
        console.log('Generated Text:', generatedText);
        
        if (generatedText && typeof generatedText === 'string') {
            document.getElementById('projectDescription').value = generatedText;
            showAlert('تم توليد الوصف بنجاح', 'success');
        } else {
            showAlert('تم التوليد ولكن لا يوجد نص. تحقق من إعدادات AI.', 'warning');
        }
    } catch (error) {
        console.error('Error:', error);
        const errorMessage = typeof error === 'string' ? error : (error.message || 'حدث خطأ غير متوقع');
        showAlert('فشل توليد الوصف. ' + errorMessage, 'error');
    } finally {
        btn.disabled = false;
        icon.textContent = '✨';
        text.textContent = 'توليد الوصف بالذكاء الاصطناعي';
    }
}

async function generateInstructions() {
    const title = document.getElementById('projectTitle').value.trim();
    const subject = document.getElementById('projectSubject').value;
    
    if (!title || !subject) {
        showAlert('يجب إدخال اسم المشروع والمادة أولاً', 'error');
        return;
    }
    
    const btn = event.target.closest('.ai-button');
    const icon = document.getElementById('aiInstIcon');
    const text = document.getElementById('aiInstText');
    
    btn.disabled = true;
    icon.innerHTML = '<div class="spinner"></div>';
    text.textContent = 'جاري التوليد...';
    
    try {
        const response = await fetch(`${API_BASE}/sections/ai/generate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                content_type: 'instructions',
                context: {
                    project_name: title,
                    subject: subject
                }
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Extract text from nested structure
            let generatedText = '';
            if (data.content && typeof data.content === 'object' && data.content.generated_text) {
                generatedText = data.content.generated_text;
            } else if (typeof data.generated_text === 'string') {
                generatedText = data.generated_text;
            } else if (typeof data.instructions === 'string') {
                generatedText = data.instructions;
            } else if (typeof data.text === 'string') {
                generatedText = data.text;
            }
            
            if (generatedText && typeof generatedText === 'string') {
                document.getElementById('projectInstructions').value = generatedText;
                showAlert('تم توليد التعليمات بنجاح', 'success');
            } else {
                showAlert('تم التوليد ولكن لا يوجد نص.', 'warning');
            }
        } else {
            const errorData = await response.json().catch(() => ({}));
            const errorMsg = errorData.error || errorData.message || 'فشل التوليد';
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        const errorMessage = typeof error === 'string' ? error : (error.message || 'حدث خطأ غير متوقع');
        showAlert('فشل توليد التعليمات. ' + errorMessage, 'error');
    } finally {
        btn.disabled = false;
        icon.textContent = '✨';
        text.textContent = 'توليد التعليمات بالذكاء الاصطناعي';
    }
}

async function generateRequirements() {
    const title = document.getElementById('projectTitle').value.trim();
    const subject = document.getElementById('projectSubject').value;
    
    if (!title || !subject) {
        showAlert('يجب إدخال اسم المشروع والمادة أولاً', 'error');
        return;
    }
    
    const btn = event.target.closest('.ai-button');
    const icon = document.getElementById('aiReqIcon');
    const text = document.getElementById('aiReqText');
    
    btn.disabled = true;
    icon.innerHTML = '<div class="spinner"></div>';
    text.textContent = 'جاري التوليد...';
    
    try {
        const response = await fetch(`${API_BASE}/sections/ai/generate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                content_type: 'instructions',
                context: {
                    project_name: title,
                    subject: subject,
                    purpose: 'شروط التسليم'
                }
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Extract text from nested structure
            let generatedText = '';
            if (data.content && typeof data.content === 'object' && data.content.generated_text) {
                generatedText = data.content.generated_text;
            } else if (typeof data.generated_text === 'string') {
                generatedText = data.generated_text;
            } else if (typeof data.requirements === 'string') {
                generatedText = data.requirements;
            } else if (typeof data.text === 'string') {
                generatedText = data.text;
            }
            
            if (generatedText && typeof generatedText === 'string') {
                document.getElementById('projectRequirements').value = generatedText;
                showAlert('تم توليد الشروط بنجاح', 'success');
            } else {
                showAlert('تم التوليد ولكن لا يوجد نص.', 'warning');
            }
        } else {
            const errorData = await response.json().catch(() => ({}));
            const errorMsg = errorData.error || errorData.message || 'فشل التوليد';
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        const errorMessage = typeof error === 'string' ? error : (error.message || 'حدث خطأ غير متوقع');
        showAlert('فشل توليد الشروط. ' + errorMessage, 'error');
    } finally {
        btn.disabled = false;
        icon.textContent = '✨';
        text.textContent = 'توليد الشروط بالذكاء الاصطناعي';
    }
}

// File Handlers
function handleVideoSelect() {
    const file = document.getElementById('videoFile').files[0];
    if (file) {
        if (file.size > 100 * 1024 * 1024) {
            showAlert('حجم الفيديو يجب أن يكون أقل من 100 MB', 'error');
            document.getElementById('videoFile').value = '';
            return;
        }
        projectData.files.video = file;
        displayFile('videoPreview', file);
    }
}

function handleFileSelect(type) {
    const input = type === 'pdf' ? document.getElementById('pdfFiles') : document.getElementById('docFiles');
    const files = Array.from(input.files);
    const listId = type === 'pdf' ? 'pdfList' : 'docList';
    const storage = type === 'pdf' ? 'pdfs' : 'docs';
    
    files.forEach(file => {
        if (file.size > 10 * 1024 * 1024) {
            showAlert(`الملف ${file.name} أكبر من 10 MB`, 'error');
            return;
        }
        projectData.files[storage].push(file);
    });
    
    displayFileList(listId, projectData.files[storage], storage);
    input.value = '';
}

function displayFile(containerId, file) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="file-item">
            <span class="file-item-name">📹 ${file.name}</span>
            <span class="file-item-size">${formatFileSize(file.size)}</span>
            <span class="file-item-remove" onclick="removeFile('video')">×</span>
        </div>
    `;
}

function displayFileList(containerId, files, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    files.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <span class="file-item-name">📄 ${file.name}</span>
            <span class="file-item-size">${formatFileSize(file.size)}</span>
            <span class="file-item-remove" onclick="removeFileFromList('${type}', ${index})">×</span>
        `;
        container.appendChild(item);
    });
}

function removeFile(type) {
    projectData.files[type] = null;
    document.getElementById(type + 'Preview').innerHTML = '';
    document.getElementById(type + 'File').value = '';
}

function removeFileFromList(type, index) {
    projectData.files[type].splice(index, 1);
    const listId = type === 'pdfs' ? 'pdfList' : 'docList';
    displayFileList(listId, projectData.files[type], type);
}

function addExternalLink() {
    console.log('🔵 addExternalLink() called');
    
    const input = document.getElementById('externalLink');
    if (!input) {
        console.error('❌ Input #externalLink not found!');
        return;
    }
    
    const url = input.value.trim();
    console.log('🔍 URL from input:', url);
    
    if (!url) {
        console.warn('⚠️ Empty URL, returning...');
        return;
    }
    
    try {
        const urlObj = new URL(url);
        console.log('✅ Valid URL object:', urlObj);
        
        projectData.files.links.push(url);
        console.log('✅ Test: Link added:', url);
        console.log('📎 Test: Total links now:', projectData.files.links.length);
        console.log('📋 Test: All links:', projectData.files.links);
        
        displayLinks();
        input.value = '';
        showAlert('تم إضافة الرابط بنجاح ✓', 'success');
        
    } catch (error) {
        console.error('❌ Test: Invalid URL:', url);
        console.error('❌ Error details:', error);
        showAlert('الرجاء إدخال رابط صحيح (يجب أن يبدأ بـ http:// أو https://)', 'error');
    }
}

function displayLinks() {
    const container = document.getElementById('linksList');
    container.innerHTML = '';
    
    projectData.files.links.forEach((link, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <span class="file-item-name">🔗 ${link}</span>
            <span class="file-item-remove" onclick="removeLink(${index})">×</span>
        `;
        container.appendChild(item);
    });
}

function removeLink(index) {
    projectData.files.links.splice(index, 1);
    displayLinks();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// Review Step
function populateReviewStep() {
    saveCurrentStepData();
    
    const summary = document.getElementById('projectSummary');
    const targets = document.getElementById('notificationTargets');
    
    // Generate summary
    summary.innerHTML = `
        <div class="summary-item">
            <span class="summary-label">📌 الاسم:</span>
            <span class="summary-value">${projectData.title}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">📚 المادة:</span>
            <span class="summary-value">${projectData.subject}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">📝 الوصف:</span>
            <span class="summary-value">${projectData.description || 'لا يوجد'}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">👥 عدد الشُعب:</span>
            <span class="summary-value">${projectData.sections.length} شعبة</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">📅 البداية:</span>
            <span class="summary-value">${new Date(projectData.settings.startDate).toLocaleString('ar-SA')}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">⏰ النهاية:</span>
            <span class="summary-value">${new Date(projectData.settings.deadline).toLocaleString('ar-SA')}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">🎯 الدرجة:</span>
            <span class="summary-value">${projectData.settings.maxGrade}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">📎 الملفات المرفقة:</span>
            <span class="summary-value">
                ${projectData.files.video ? '1 فيديو، ' : ''}
                ${projectData.files.pdfs.length} PDF، 
                ${projectData.files.docs.length} Office، 
                ${projectData.files.links.length} رابط
            </span>
        </div>
    `;
    
    // Generate targets
    const totalStudents = document.getElementById('totalStudents').textContent;
    const selectedSections = document.getElementById('selectedSections').textContent;
    
    targets.innerHTML = `
        <li>Telegram: <strong>${totalStudents}</strong> طالب في <strong>${selectedSections}</strong> قروب</li>
        <li>يتضمن: رابط التسليم + التعليمات + الشروط + الملفات المساعدة</li>
    `;
}

// Submit Project
async function submitProject() {
    // ✅ Final sync: Update all checklists to textareas
    if (typeof updateHiddenTextarea === 'function') {
        updateHiddenTextarea('instructions');
        updateHiddenTextarea('requirements');
        updateHiddenTextarea('tips');
        console.log('✅ Checklists synced to textareas');
    }
    
    saveCurrentStepData();
    
    // ✅ Log current state for debugging
    console.log('📊 Final project data before validation:', {
        gradeId: projectData.gradeId,
        sections: projectData.sections,
        sectionsCount: projectData.sections?.length,
        title: projectData.title,
        subject: projectData.subject
    });
    
    // ✅ Double-check sections from DOM
    const checkedSections = Array.from(document.querySelectorAll('input[name="section"]:checked'))
        .map(cb => parseInt(cb.value));
    console.log('📋 Checked sections in DOM:', checkedSections);
    
    // ✅ Sync if mismatch detected
    if (projectData.sections.length !== checkedSections.length) {
        console.warn('⚠️ Mismatch detected! Syncing projectData.sections with DOM');
        projectData.sections = checkedSections;
    }
    
    // Validate required fields
    if (!projectData.gradeId || !projectData.sections || projectData.sections.length === 0) {
        showAlert('الرجاء اختيار صف وشُعب', 'error');
        console.error('❌ Validation failed: No sections selected');
        return;
    }
    
    console.log('✅ Validation passed. Sections:', projectData.sections);
    
    if (!projectData.settings.startDate || !projectData.settings.deadline) {
        showAlert('الرجاء تحديد تاريخ البداية والموعد النهائي', 'error');
        return;
    }
    
    // Validate instructions and requirements
    if (!projectData.instructions || projectData.instructions.trim() === '') {
        showAlert('الرجاء إضافة التعليمات (استخدم زر AI أو "تحميل مثال")', 'error');
        goToStep(3);
        return;
    }
    
    if (!projectData.requirements || projectData.requirements.trim() === '') {
        showAlert('الرجاء إضافة الشروط (استخدم زر AI أو "تحميل مثال")', 'error');
        goToStep(3);
        return;
    }
    
    // Validate file types
    if (!projectData.settings.allowedFileTypes || projectData.settings.allowedFileTypes.length === 0) {
        showAlert('الرجاء اختيار نوع ملف واحد على الأقل', 'error');
        goToStep(5);
        return;
    }
    
    // Generate tips if empty
    if (!projectData.tips) {
        await generateTipsAutomatically();
    }
    
    showLoading(true);
    
    try {
        // Create FormData
        const formData = new FormData();
        
        // Basic Info
        formData.append('title', projectData.title);
        formData.append('subject', projectData.subject);
        formData.append('description', projectData.description || '');
        
        // Target - ensure sections is an array
        formData.append('grade_id', projectData.gradeId);
        const sectionsArray = Array.isArray(projectData.sections) ? projectData.sections : [];
        
        console.log('🔍 Sections before sending:', sectionsArray);
        console.log('🔍 Grade ID:', projectData.gradeId);
        
        // ✅ استخدام native FormData arrays بدلاً من JSON.stringify
        sectionsArray.forEach(id => formData.append('section_ids', id));
        
        // Instructions
        formData.append('instructions', projectData.instructions || '');
        formData.append('requirements', projectData.requirements || '');
        formData.append('tips', projectData.tips || '');
        
        // Settings - Send as separate fields, not nested object
        const fileTypesArray = Array.isArray(projectData.settings.allowedFileTypes) && projectData.settings.allowedFileTypes.length > 0 ? 
            projectData.settings.allowedFileTypes : ['pdf', 'doc'];
        
        console.log('🔍 File types before sending:', fileTypesArray);
        
        // ✅ استخدام native FormData arrays بدلاً من JSON.stringify
        fileTypesArray.forEach(type => formData.append('allowed_file_types', type));
        formData.append('max_file_size', projectData.settings.maxFileSize || 10);
        formData.append('max_grade', projectData.settings.maxGrade || 20);
        formData.append('start_date', projectData.settings.startDate);
        formData.append('deadline', projectData.settings.deadline);
        formData.append('allow_late_submission', projectData.settings.allowLateSubmission || false);
        formData.append('send_reminder', projectData.settings.sendReminder || false);
        formData.append('ai_check_plagiarism', projectData.settings.aiCheck || false);
        
        // Telegram settings - check if user wants immediate sending
        const sendTelegramNow = document.getElementById('sendToTelegram')?.checked || false;
        formData.append('send_telegram_now', sendTelegramNow);
        console.log('📱 Send Telegram now:', sendTelegramNow);
        
        // Add files
        if (projectData.files.video) {
            formData.append('video', projectData.files.video);
        }
        projectData.files.pdfs.forEach(file => {
            formData.append('pdfs', file);
        });
        projectData.files.docs.forEach(file => {
            formData.append('docs', file);
        });
        
        // Send links - ensure it's always an array
        const linksArray = Array.isArray(projectData.files.links) ? projectData.files.links : [];
        console.log('🔍 External links before sending:', linksArray);
        
        // ✅ استخدام native FormData arrays بدلاً من JSON.stringify
        if (linksArray.length > 0) {
            linksArray.forEach(link => {
                if (link && link.trim()) {
                    formData.append('external_links', link.trim());
                }
            });
        }
        
        // Log FormData for debugging
        console.log('📤 Submitting project data:');
        console.log('projectData object:', projectData);
        
        // Group FormData entries by key
        const formDataGroups = {};
        for (let [key, value] of formData.entries()) {
            if (!formDataGroups[key]) {
                formDataGroups[key] = [];
            }
            formDataGroups[key].push(value);
        }
        
        // Log grouped data
        console.log('📋 FormData contents:');
        for (let [key, values] of Object.entries(formDataGroups)) {
            if (values.length === 1) {
                console.log(`  ${key}:`, values[0]);
            } else {
                console.log(`  ${key}: [${values.join(', ')}]`);
            }
        }
        
        // 🚀 PRODUCTION MODE: Save to database
        console.log('🚀 PRODUCTION MODE: Data will be saved to database');
        
        const data = await api.createProjectWithFiles(formData);
        
        console.log('✅ Project created successfully:', data);
        
        // ✅ Save preferences for next time
        saveUserPreferences();
        
        // ✅ Clear draft after successful submission
        clearDraft();
        
        // Show success modal with project info
        showSuccessModal(data);
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message || 'حدث خطأ أثناء إنشاء المشروع', 'error');
    } finally {
        showLoading(false);
    }
}

async function generateTipsAutomatically() {
    try {
        const response = await fetch(`${API_BASE}/sections/ai/generate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                content_type: 'instructions',
                context: {
                    project_name: projectData.title,
                    subject: projectData.subject,
                    purpose: 'نصائح للطلاب'
                }
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Extract text from nested structure
            let generatedText = '';
            if (data.content && typeof data.content === 'object' && data.content.generated_text) {
                generatedText = data.content.generated_text;
            } else if (typeof data.generated_text === 'string') {
                generatedText = data.generated_text;
            } else if (typeof data.tips === 'string') {
                generatedText = data.tips;
            } else if (typeof data.text === 'string') {
                generatedText = data.text;
            }
            
            projectData.tips = generatedText || '';
        }
    } catch (error) {
        console.error('Error generating tips:', error);
    }
}

// UI Helpers
function showAlert(message, type) {
    const alertBox = document.getElementById('alertBox');
    alertBox.className = `alert alert-${type} show`;
    
    // Convert message to string if it's an object
    let displayMessage = message;
    if (typeof message === 'object') {
        displayMessage = message.message || message.error || JSON.stringify(message);
    }
    
    alertBox.textContent = displayMessage;
    
    setTimeout(() => {
        alertBox.classList.remove('show');
    }, 5000);
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.toggle('show', show);
}

// ✅ AUTO-SAVE SYSTEM
let autoSaveInterval;

function setupAutoSave() {
    // Auto-save every 30 seconds
    autoSaveInterval = setInterval(() => {
        saveDraftToStorage();
    }, 30000);
    
    console.log('💾 Auto-save enabled (every 30 seconds)');
}

function saveDraftToStorage() {
    try {
        const draft = {
            timestamp: Date.now(),
            step: currentStep,
            data: projectData,
            version: '1.0'
        };
        
        localStorage.setItem('project_draft', JSON.stringify(draft));
        console.log('💾 Draft auto-saved at', new Date().toLocaleTimeString());
    } catch (error) {
        console.error('Error saving draft:', error);
    }
}

function loadDraftFromStorage() {
    try {
        const draft = localStorage.getItem('project_draft');
        if (!draft) return;
        
        const parsed = JSON.parse(draft);
        const ageHours = (Date.now() - parsed.timestamp) / (1000 * 60 * 60);
        
        // Only load if draft is less than 24 hours old
        if (ageHours < 24) {
            if (confirm('لديك مسودة محفوظة من ' + new Date(parsed.timestamp).toLocaleString() + '. هل تريد استكمالها؟')) {
                projectData = parsed.data;
                currentStep = parsed.step || 1;
                restoreDraftToUI();
                showAlert('تم استعادة المسودة بنجاح', 'success');
            }
        } else {
            // Remove old draft
            localStorage.removeItem('project_draft');
        }
    } catch (error) {
        console.error('Error loading draft:', error);
    }
}

function restoreDraftToUI() {
    // Restore Step 1
    if (projectData.title) document.getElementById('projectTitle').value = projectData.title;
    if (projectData.subject) document.getElementById('projectSubject').value = projectData.subject;
    if (projectData.description) document.getElementById('projectDescription').value = projectData.description;
    
    // Restore Step 2
    if (projectData.gradeId) {
        document.getElementById('gradeSelect').value = projectData.gradeId;
        loadSections().then(() => {
            projectData.sections.forEach(sectionId => {
                const checkbox = document.querySelector(`input[name="section"][value="${sectionId}"]`);
                if (checkbox) checkbox.checked = true;
            });
            updateSectionStats();
        });
    }
    
    // Restore Step 3
    if (projectData.instructions) document.getElementById('projectInstructions').value = projectData.instructions;
    if (projectData.requirements) document.getElementById('projectRequirements').value = projectData.requirements;
    
    // Restore Step 5
    if (projectData.settings.maxGrade) document.getElementById('maxGrade').value = projectData.settings.maxGrade;
    if (projectData.settings.startDate) document.getElementById('startDate').value = projectData.settings.startDate;
    if (projectData.settings.deadline) document.getElementById('deadline').value = projectData.settings.deadline;
    
    // Navigate to saved step
    for (let i = 1; i < currentStep; i++) {
        updateWizard();
    }
}

function clearDraft() {
    localStorage.removeItem('project_draft');
    console.log('🧹 Draft cleared');
}

// ✅ SMART DEFAULTS SYSTEM
function saveUserPreferences() {
    try {
        const prefs = {
            defaultGrade: projectData.gradeId,
            defaultSections: projectData.sections,
            defaultSubject: projectData.subject,
            defaultFileTypes: projectData.settings.allowedFileTypes,
            defaultMaxGrade: projectData.settings.maxGrade,
            defaultDeadlineDays: calculateDays(),
            timestamp: Date.now()
        };
        
        localStorage.setItem('user_preferences', JSON.stringify(prefs));
        console.log('⚙️ Preferences saved');
    } catch (error) {
        console.error('Error saving preferences:', error);
    }
}

function loadUserPreferences() {
    try {
        const prefs = localStorage.getItem('user_preferences');
        if (!prefs) return;
        
        const parsed = JSON.parse(prefs);
        
        // Apply default subject
        if (parsed.defaultSubject) {
            setTimeout(() => {
                const select = document.getElementById('projectSubject');
                if (select.querySelector(`option[value="${parsed.defaultSubject}"]`)) {
                    select.value = parsed.defaultSubject;
                }
            }, 500);
        }
        
        // Apply default grade and sections
        if (parsed.defaultGrade) {
            setTimeout(() => {
                const gradeSelect = document.getElementById('gradeSelect');
                if (gradeSelect.querySelector(`option[value="${parsed.defaultGrade}"]`)) {
                    gradeSelect.value = parsed.defaultGrade;
                    loadSections();
                }
            }, 1000);
        }
        
        // Apply default max grade
        if (parsed.defaultMaxGrade) {
            document.getElementById('maxGrade').value = parsed.defaultMaxGrade;
        }
        
        console.log('⚙️ Preferences loaded');
    } catch (error) {
        console.error('Error loading preferences:', error);
    }
}

function calculateDays() {
    const start = new Date(document.getElementById('startDate').value);
    const end = new Date(document.getElementById('deadline').value);
    return Math.ceil((end - start) / (1000 * 60 * 60 * 24));
}

// ✅ KEYBOARD SHORTCUTS
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + Enter = Next Step
        if (e.ctrlKey && e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (currentStep < totalSteps) {
                nextStep();
            }
        }
        
        // Ctrl + Shift + Enter = Submit
        if (e.ctrlKey && e.shiftKey && e.key === 'Enter') {
            e.preventDefault();
            if (currentStep === totalSteps) {
                submitProject();
            }
        }
        
        // Ctrl + Alt + G = Generate AI
        if (e.ctrlKey && e.altKey && e.key === 'g') {
            e.preventDefault();
            if (currentStep === 1) {
                generateDescription();
            } else if (currentStep === 3) {
                const focused = document.activeElement;
                if (focused.id === 'projectInstructions') {
                    generateInstructions();
                } else if (focused.id === 'projectRequirements') {
                    generateRequirements();
                }
            }
        }
        
        // Escape = Previous Step
        if (e.key === 'Escape') {
            e.preventDefault();
            if (currentStep > 1) {
                previousStep();
            }
        }
        
        // Ctrl + S = Save Draft
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            saveDraftToStorage();
            showAlert('تم حفظ المسودة', 'success');
        }
    });
    
    console.log('⌨️ Keyboard shortcuts enabled');
}

// ✅ TAB SWITCHING FUNCTIONALITY
function switchInputTab(tabName) {
    // Remove active from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
    });
    
    // Activate selected tab
    const tabBtn = event.target.closest('.tab-btn');
    const tabContent = document.getElementById(`tab-${tabName}`);
    
    if (tabBtn) tabBtn.classList.add('active');
    if (tabContent) {
        tabContent.classList.add('active');
        tabContent.style.display = 'block';
    }
    
    console.log(`📑 Switched to ${tabName} tab`);
}

// ✅ IMAGE UPLOAD & OCR
async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file
    if (file.size > 5 * 1024 * 1024) {
        showAlert('حجم الصورة يجب أن يكون أقل من 5 MB', 'error');
        return;
    }
    
    if (!file.type.startsWith('image/')) {
        showAlert('يرجى اختيار ملف صورة فقط', 'error');
        return;
    }
    
    const preview = document.getElementById('imagePreview');
    preview.style.display = 'block';
    preview.innerHTML = `
        <div class="extraction-loading">
            <div class="loading-spinner"></div>
            <p>جاري استخراج النص من الصورة...</p>
            <small>قد تستغرق العملية بضع ثوان</small>
        </div>
    `;
    
    try {
        console.log('📷 Starting OCR...');
        
        // Initialize Tesseract Worker (v4 API)
        const worker = await Tesseract.createWorker({
            logger: m => {
                if (m.status === 'recognizing text') {
                    console.log(`OCR Progress: ${Math.round(m.progress * 100)}%`);
                }
            },
            langPath: 'https://tessdata.projectnaptha.com/4.0.0',
        });
        
        // Load Arabic first for better RTL support
        await worker.loadLanguage('ara');
        await worker.initialize('ara');
        
        // Set parameters for better Arabic recognition
        await worker.setParameters({
            tessedit_pageseg_mode: Tesseract.PSM.AUTO,
            preserve_interword_spaces: '1',
        });
        
        // Recognize text
        console.log('🔍 Recognizing text...');
        const { data: { text } } = await worker.recognize(file);
        const extractedText = text.trim();
        
        await worker.terminate();
        
        console.log('✅ OCR completed!');
        console.log('📄 Full text length:', extractedText.length, 'characters');
        console.log('📝 Full extracted text:\n', extractedText);
        
        if (!extractedText) {
            throw new Error('لم يتم العثور على نص في الصورة');
        }
        
        // Display the full extracted text (not just the first line)
        displayExtractedText(extractedText, 'image');
        
    } catch (error) {
        console.error('OCR Error:', error);
        preview.innerHTML = `
            <div class="extraction-header">
                <h4>⚠️ فشل استخراج النص</h4>
            </div>
            <div class="extraction-body">
                <p>${error.message || 'حدث خطأ أثناء قراءة الصورة'}</p>
            </div>
            <div class="extraction-footer">
                <button class="btn-retry" onclick="document.getElementById('titleImage').click()">
                    🔄 إعادة المحاولة
                </button>
            </div>
        `;
    }
}

// ✅ PDF UPLOAD & EXTRACTION
async function handlePdfUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file
    if (file.size > 10 * 1024 * 1024) {
        showAlert('حجم الـ PDF يجب أن يكون أقل من 10 MB', 'error');
        return;
    }
    
    if (file.type !== 'application/pdf') {
        showAlert('يرجى اختيار ملف PDF فقط', 'error');
        return;
    }
    
    const preview = document.getElementById('pdfPreview');
    preview.style.display = 'block';
    preview.innerHTML = `
        <div class="extraction-loading">
            <div class="loading-spinner"></div>
            <p>جاري قراءة ملف PDF...</p>
        </div>
    `;
    
    try {
        console.log('📄 Reading PDF...');
        
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
        
        console.log(`📄 PDF has ${pdf.numPages} pages`);
        
        // Read first page
        const page = await pdf.getPage(1);
        const content = await page.getTextContent();
        const text = content.items.map(item => item.str).join(' ');
        
        console.log('✅ PDF read completed');
        
        if (!text.trim()) {
            throw new Error('لم يتم العثور على نص في الملف');
        }
        
        // Extract title (first line or first 100 chars)
        const lines = text.split('\n').filter(l => l.trim());
        const extractedTitle = (lines[0] || text).trim().substring(0, 100);
        
        displayExtractedText(extractedTitle, 'pdf');
        
    } catch (error) {
        console.error('PDF Error:', error);
        preview.innerHTML = `
            <div class="extraction-header">
                <h4>⚠️ فشل قراءة الملف</h4>
            </div>
            <div class="extraction-body">
                <p>${error.message || 'حدث خطأ أثناء قراءة ملف PDF'}</p>
            </div>
            <div class="extraction-footer">
                <button class="btn-retry" onclick="document.getElementById('titlePdf').click()">
                    🔄 إعادة المحاولة
                </button>
            </div>
        `;
    }
}

// ✅ DISPLAY EXTRACTED TEXT
function displayExtractedText(text, source) {
    const previewId = source === 'image' ? 'imagePreview' : 'pdfPreview';
    const preview = document.getElementById(previewId);
    const icon = source === 'image' ? '📷' : '📄';
    
    // Escape text for safe HTML and preserve line breaks
    const escapedText = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
    
    // For the onclick button, escape quotes properly
    const textForButton = text
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '&quot;')
        .replace(/\n/g, '\\n');
    
    preview.innerHTML = `
        <div class="extraction-header">
            <h4>${icon} النص المستخرج:</h4>
            <small style="color: var(--text-secondary); font-weight: normal;">
                ${text.length} حرف · ${text.split('\n').length} سطر
            </small>
        </div>
        <div class="extraction-body" style="white-space: pre-wrap; max-height: 400px; overflow-y: auto; padding: 20px; background: var(--bg-color); border-radius: 8px; line-height: 1.8;">
            ${escapedText}
        </div>
        <div class="extraction-footer">
            <button class="btn-use" onclick="useExtractedText('${textForButton}')">
                ✓ استخدام هذا النص
            </button>
            <button class="btn-retry" onclick="document.getElementById('title${source === 'image' ? 'Image' : 'Pdf'}').click()">
                🔄 تجربة ملف آخر
            </button>
        </div>
    `;
}

// ✅ USE EXTRACTED TEXT
function useExtractedText(text) {
    // Split text into lines
    const lines = text.split('\n').filter(line => line.trim().length > 0);
    
    if (lines.length > 0) {
        // First line as title (max 150 chars)
        const title = lines[0].trim().substring(0, 150);
        document.getElementById('projectTitle').value = title;
        
        // Rest as description (if exists)
        if (lines.length > 1) {
            const description = lines.slice(1).join('\n').trim();
            document.getElementById('projectDescription').value = description;
            console.log('✅ Text split: Title + Description');
        } else {
            console.log('✅ Text copied to title only');
        }
    } else {
        // If no lines, use full text as title
        document.getElementById('projectTitle').value = text.substring(0, 150);
    }
    
    switchInputTab('text');
    showAlert('تم نسخ النص بنجاح! ✓', 'success');
}

// ✅ DRAG & DROP FUNCTIONALITY
document.addEventListener('DOMContentLoaded', function() {
    // Setup drag & drop for image
    const imageDropZone = document.getElementById('imageDropZone');
    if (imageDropZone) {
        setupDragAndDrop(imageDropZone, 'image');
    }
    
    // Setup drag & drop for PDF
    const pdfDropZone = document.getElementById('pdfDropZone');
    if (pdfDropZone) {
        setupDragAndDrop(pdfDropZone, 'pdf');
    }
});

function setupDragAndDrop(dropZone, type) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });
    
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const file = files[0];
            
            // Set file to input
            const input = document.getElementById(type === 'image' ? 'titleImage' : 'titlePdf');
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            
            // Trigger change event
            if (type === 'image') {
                handleImageUpload({ target: input });
            } else {
                handlePdfUpload({ target: input });
            }
        }
    }, false);
}

// ✅ TELEGRAM SETTINGS
function toggleTelegramOptions() {
    const enabled = document.getElementById('sendToTelegram').checked;
    const options = document.getElementById('telegramOptions');
    options.style.display = enabled ? 'block' : 'none';
}

function updateTelegramTargets() {
    const selected = document.querySelectorAll('input[name="section"]:checked');
    const targetsList = document.getElementById('telegramTargets');
    
    if (!targetsList) return;
    
    if (selected.length === 0) {
        targetsList.innerHTML = `
            <li style="position: relative; padding-right: 20px; color: #64748b;">
                <span style="position: absolute; right: 0; color: #f59e0b; font-weight: bold;">⚠</span>
                <span>لم يتم اختيار شُعب بعد</span>
            </li>`;
        return;
    }
    
    let totalStudents = 0;
    let html = '';
    
    selected.forEach(checkbox => {
        const label = checkbox.closest('.checkbox-item').querySelector('.checkbox-label');
        const sectionName = label.textContent.trim();
        const info = checkbox.closest('.checkbox-item').querySelector('.checkbox-info');
        const count = info ? parseInt(info.textContent) || 0 : 0;
        totalStudents += count;
        
        html += `
            <li style="position: relative; padding-right: 20px; margin-bottom: 8px; color: #1e293b;">
                <span style="position: absolute; right: 0; color: #10b981; font-weight: bold;">✓</span>
                <span style="font-weight: 600; color: #0f172a;">${sectionName}</span>
                <span style="color: #64748b;"> - ${count} طالب</span>
            </li>`;
    });
    
    html += `
        <li style="position: relative; padding-right: 20px; margin-top: 12px; padding-top: 12px; border-top: 2px solid #94a3b8; background: linear-gradient(90deg, rgba(6,182,212,0.1) 0%, transparent 100%); padding: 12px; padding-right: 32px; border-radius: 6px;">
            <span style="position: absolute; right: 8px; font-size: 18px;">📊</span>
            <span style="font-weight: 700; color: #0c4a6e; font-size: 15px;">الإجمالي:</span>
            <span style="font-weight: 700; color: #0369a1; font-size: 16px;"> ${totalStudents} طالب</span>
            <span style="color: #64748b;"> في ${selected.length} قروب</span>
        </li>`;
    
    targetsList.innerHTML = html;
}

// ✅ SHOW TELEGRAM RESULTS MODAL
function showTelegramResults(results) {
    if (!results || results.total === 0) return;
    
    const modal = document.createElement('div');
    modal.className = 'telegram-results-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s;
    `;
    
    let html = `
        <div style="
            background: var(--card-bg);
            border-radius: 16px;
            padding: 32px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideDown 0.4s;
        ">
            <h3 style="margin: 0 0 24px 0; font-size: 24px; color: var(--text-color);">
                📱 نتائج الإرسال للتيليجرام
            </h3>
    `;
    
    // Summary
    html += `
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            text-align: center;
        ">
            <div style="font-size: 48px; font-weight: bold;">
                ${results.success_count}/${results.total}
            </div>
            <div style="font-size: 16px; margin-top: 8px;">
                تم الإرسال بنجاح
            </div>
        </div>
    `;
    
    // Success list
    if (results.success && results.success.length > 0) {
        html += `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #16a34a; margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">✅</span>
                    <span>تم الإرسال بنجاح (${results.success.length})</span>
                </h4>
                <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 12px;">
        `;
        
        results.success.forEach(item => {
            html += `
                <div style="padding: 8px; border-bottom: 1px solid #dcfce7; display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #15803d;">${item.section_name}</strong>
                    <span style="color: #16a34a; font-size: 14px;">${item.students_count} طالب</span>
                </div>
            `;
        });
        
        html += `</div></div>`;
    }
    
    // Failed list
    if (results.failed && results.failed.length > 0) {
        html += `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #dc2626; margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">⚠️</span>
                    <span>فشل الإرسال (${results.failed.length})</span>
                </h4>
                <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 12px;">
        `;
        
        results.failed.forEach(item => {
            html += `
                <div style="padding: 8px; border-bottom: 1px solid #fee2e2;">
                    <div style="font-weight: 600; color: #991b1b;">${item.section_name}</div>
                    <div style="color: #dc2626; font-size: 13px; margin-top: 4px;">${item.error}</div>
                </div>
            `;
        });
        
        html += `</div></div>`;
    }
    
    // Footer
    html += `
            <div style="text-align: center; margin-top: 24px;">
                <button onclick="this.closest('.telegram-results-modal').remove()" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 32px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s;
                ">
                    حسناً
                </button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Export for debugging and onclick handlers
window.projectData = projectData;
window.saveDraft = saveDraftToStorage;
window.clearDraft = clearDraft;
window.switchInputTab = switchInputTab;
window.toggleTelegramOptions = toggleTelegramOptions;
window.updateTelegramTargets = updateTelegramTargets;
window.addExternalLink = addExternalLink;
window.removeLink = removeLink;
window.removeFile = removeFile;
window.removeFileFromList = removeFileFromList;
window.useExtractedText = useExtractedText;

// Dark Mode Toggle
function toggleTheme() {
    const html = document.documentElement;
    const themeToggle = document.querySelector('.theme-toggle');
    const currentTheme = html.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        html.setAttribute('data-theme', 'light');
        themeToggle.textContent = '🌙';
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        themeToggle.textContent = '☀️';
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme on page load
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const html = document.documentElement;
    const themeToggle = document.querySelector('.theme-toggle');
    
    html.setAttribute('data-theme', savedTheme);
    if (savedTheme === 'dark') {
        themeToggle.textContent = '☀️';
    } else {
        themeToggle.textContent = '🌙';
    }
}

// Initialize theme
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadTheme);
} else {
    loadTheme();
}
