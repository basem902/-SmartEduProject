/**
 * نظام التحقق من الطالب للانضمام
 * Professional Student Join Verification System
 */

class StudentJoinVerification {
    constructor(config) {
        this.apiUrl = config.apiUrl;
        this.sectionId = config.sectionId;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSectionInfo();
    }

    setupEventListeners() {
        const form = document.getElementById('verificationForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Real-time validation
        const nameInput = document.getElementById('studentName');
        if (nameInput) {
            nameInput.addEventListener('input', () => this.validateName());
        }
    }

    async loadSectionInfo() {
        // عرض معلومات الشعبة إذا كان متاحاً
        try {
            const response = await fetch(`${this.apiUrl}/sections/section/${this.sectionId}/`);
            const data = await response.json();
            
            if (data.section) {
                document.getElementById('gradeName').textContent = data.section.grade || '';
                document.getElementById('sectionName').textContent = data.section.name || '';
            }
        } catch (error) {
            console.log('Could not load section info:', error);
        }
    }

    validateName() {
        const input = document.getElementById('studentName');
        const value = input.value.trim();
        const feedback = document.getElementById('nameFeedback');
        
        if (!value) {
            this.showFeedback(feedback, '', 'none');
            return false;
        }

        // Check Arabic only
        const arabicPattern = /^[\u0600-\u06FF\s]+$/;
        if (!arabicPattern.test(value)) {
            this.showFeedback(feedback, '❌ يجب أن يكون الاسم بالعربية فقط', 'error');
            return false;
        }

        // Check parts
        const parts = value.split(/\s+/).filter(p => p.length > 0);
        if (parts.length < 4) {
            this.showFeedback(feedback, `⚠️ الاسم يجب أن يكون رباعياً (${parts.length}/4)`, 'warning');
            return false;
        }

        this.showFeedback(feedback, '✅ الاسم صحيح', 'success');
        return true;
    }

    showFeedback(element, message, type) {
        element.textContent = message;
        element.className = `feedback ${type}`;
        element.style.display = message ? 'block' : 'none';
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const studentName = document.getElementById('studentName').value.trim();
        const submitBtn = document.getElementById('submitBtn');
        
        // Validate
        if (!this.validateName()) {
            return;
        }

        // Disable button
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> جاري التحقق...';

        try {
            const response = await fetch(`${this.apiUrl}/sections/verify-student-join/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    student_name: studentName,
                    section_id: this.sectionId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess(data);
            } else {
                this.showError(data);
            }

        } catch (error) {
            console.error('Error:', error);
            this.showError({
                error: 'network_error',
                message: 'حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى'
            });
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '✅ تحقق واستمر';
        }
    }

    showSuccess(data) {
        // Hide form
        document.getElementById('formSection').style.display = 'none';
        
        // Show success
        const successSection = document.getElementById('successSection');
        successSection.style.display = 'block';

        // Fill data
        document.getElementById('successName').textContent = data.student.name;
        document.getElementById('successGrade').textContent = data.student.grade;
        document.getElementById('successSection').textContent = data.student.section;
        document.getElementById('successSchool').textContent = data.student.school;

        // Telegram group
        if (data.telegram_group) {
            document.getElementById('groupName').textContent = data.telegram_group.name;
            document.getElementById('joinBtn').href = data.telegram_group.invite_link;
            
            // Store for later
            this.telegramLink = data.telegram_group.invite_link;
        }

        // Animation
        this.playSuccessAnimation();
    }

    showError(data) {
        // Hide form
        document.getElementById('formSection').style.display = 'none';
        
        // Show error
        const errorSection = document.getElementById('errorSection');
        errorSection.style.display = 'block';

        // Fill error
        document.getElementById('errorMessage').textContent = data.message;
        document.getElementById('errorAction').textContent = data.action || '';

        // Suggestions
        const suggestionsDiv = document.getElementById('suggestions');
        if (data.suggestions && data.suggestions.length > 0) {
            suggestionsDiv.style.display = 'block';
            const list = document.getElementById('suggestionsList');
            list.innerHTML = '';
            
            data.suggestions.forEach(suggestion => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="suggestion-name">${suggestion.name}</span>
                    <span class="suggestion-similarity">${suggestion.similarity}%</span>
                `;
                li.onclick = () => {
                    document.getElementById('studentName').value = suggestion.name;
                    this.tryAgain();
                };
                list.appendChild(li);
            });
        } else {
            suggestionsDiv.style.display = 'none';
        }
    }

    tryAgain() {
        document.getElementById('formSection').style.display = 'block';
        document.getElementById('successSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';
        document.getElementById('studentName').focus();
    }

    playSuccessAnimation() {
        // Confetti animation
        const duration = 3 * 1000;
        const animationEnd = Date.now() + duration;
        const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];

        (function frame() {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) return;

            const particleCount = 2;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'confetti-particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.background = colors[Math.floor(Math.random() * colors.length)];
                particle.style.animationDuration = (Math.random() * 3 + 2) + 's';
                document.body.appendChild(particle);

                setTimeout(() => particle.remove(), 5000);
            }

            requestAnimationFrame(frame);
        }());
    }
}

// Export for use
window.StudentJoinVerification = StudentJoinVerification;
