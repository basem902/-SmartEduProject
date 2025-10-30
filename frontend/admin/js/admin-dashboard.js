/**
 * Admin Dashboard Manager
 */

class AdminDashboard {
    constructor() {
        this.stats = null;
        this.tables = [];
    }

    /**
     * تحميل وعرض الإحصائيات
     */
    async loadStatistics() {
        try {
            this.stats = await adminAPI.getStatistics();
            this.renderStatistics();
            this.renderTablesList();
            this.loadTeachersList();
        } catch (error) {
            this.showError('فشل في تحميل الإحصائيات: ' + error.message);
        }
    }

    /**
     * تحميل قائمة المعلمين
     */
    async loadTeachersList() {
        try {
            const data = await adminAPI.getTeachers();
            this.renderTeachersList(data.rows || []);
        } catch (error) {
            console.error('Failed to load teachers:', error);
            document.getElementById('teachersListContainer').innerHTML = 
                '<p style="color: #999;">فشل في تحميل قائمة المعلمين</p>';
        }
    }

    /**
     * عرض قائمة المعلمين
     */
    renderTeachersList(teachers) {
        const container = document.getElementById('teachersListContainer');
        if (!container) return;

        if (!teachers || teachers.length === 0) {
            container.innerHTML = '<p style="color: #999;">لا يوجد معلمون مسجلون</p>';
            return;
        }

        let html = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width: 5%">ID</th>
                        <th style="width: 25%">الاسم</th>
                        <th style="width: 25%">البريد الإلكتروني</th>
                        <th style="width: 15%">المدرسة</th>
                        <th style="width: 10%; text-align: center;">الحالة</th>
                        <th style="width: 20%; text-align: center;">الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
        `;

        teachers.forEach(teacher => {
            const isActive = teacher.is_active;
            const statusBadge = isActive 
                ? '<span style="background: #28a745; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem;">نشط</span>'
                : '<span style="background: #dc3545; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem;">معطل</span>';

            html += `
                <tr>
                    <td>${teacher.id}</td>
                    <td><strong>${teacher.full_name || '-'}</strong></td>
                    <td>${teacher.email || '-'}</td>
                    <td>${teacher.school_name || '-'}</td>
                    <td style="text-align: center;">${statusBadge}</td>
                    <td>
                        <div class="action-buttons" style="justify-content: center;">
                            <button class="btn btn-warning btn-sm" 
                                    onclick="dashboard.deleteTeacherSections(${teacher.id}, '${teacher.full_name}')"
                                    title="حذف بيانات الشُعب والتيليجرام">
                                🗑️ حذف الشُعب
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    /**
     * حذف بيانات الشُعب للمعلم
     */
    async deleteTeacherSections(teacherId, teacherName) {
        // تأكيد أول
        if (!confirm(`⚠️ هل أنت متأكد من حذف جميع بيانات الشُعب والتيليجرام للمعلم "${teacherName}"؟\n\nسيتم حذف:\n• الصفوف الدراسية\n• الشُعب\n• روابط الشُعب\n• تسجيلات الطلاب\n• قروبات تيليجرام\n• محتوى AI\n\nمع الاحتفاظ بحساب المعلم.\n\nهذا الإجراء لا يمكن التراجع عنه!`)) {
            return;
        }

        // تأكيد ثاني
        if (!confirm(`⚠️⚠️ تأكيد نهائي: حذف بيانات الشُعب للمعلم "${teacherName}"؟`)) {
            return;
        }

        try {
            this.showLoading(true);
            const result = await adminAPI.deleteTeacherSections(teacherId);
            
            this.showSuccess(`✅ ${result.message}\n\nتم حذف ${result.total_deleted} سجل`);
            
            // إعادة تحميل البيانات
            await this.loadStatistics();
        } catch (error) {
            this.showError('فشل في حذف البيانات: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * عرض الإحصائيات
     */
    renderStatistics() {
        const statsContainer = document.getElementById('statsContainer');
        if (!statsContainer || !this.stats) return;

        const mainTables = ['teachers', 'projects', 'students', 'submissions'];
        const icons = {
            'teachers': '👨‍🏫',
            'projects': '📁',
            'students': '👥',
            'submissions': '📤'
        };
        const labels = {
            'teachers': 'المعلمين',
            'projects': 'المشاريع',
            'students': 'الطلاب',
            'submissions': 'التسليمات'
        };

        let html = '';
        mainTables.forEach(tableName => {
            const tableInfo = this.stats.tables.find(t => t.name === tableName);
            const count = tableInfo ? tableInfo.count : 0;
            
            html += `
                <div class="stat-card">
                    <div class="icon">${icons[tableName] || '📊'}</div>
                    <div class="number">${count}</div>
                    <div class="label">${labels[tableName] || tableName}</div>
                </div>
            `;
        });

        statsContainer.innerHTML = html;
    }

    /**
     * عرض قائمة الجداول مصنفة
     */
    renderTablesList() {
        const tablesContainer = document.getElementById('tablesContainer');
        if (!tablesContainer || !this.stats) return;

        // تصنيف الجداول
        const categories = {
            accounts: {
                icon: '👥',
                label: 'الحسابات والمستخدمين',
                tables: ['teachers_pending', 'teachers', 'settings']
            },
            sections: {
                icon: '📚',
                label: 'الشُعب والطلاب',
                tables: ['school_grades', 'sections', 'section_links', 'student_registrations', 'ai_generated_content', 'telegram_groups']
            },
            projects: {
                icon: '📁',
                label: 'المشاريع والتسليمات',
                tables: ['projects', 'students', 'project_files', 'submissions']
            },
            otp: {
                icon: '🔐',
                label: 'نظام رموز OTP',
                tables: ['project_otp', 'otp_logs']
            }
        };

        let html = '';

        Object.entries(categories).forEach(([catKey, category]) => {
            const categoryTables = this.stats.tables.filter(t => category.tables.includes(t.name));
            
            if (categoryTables.length > 0) {
                html += `
                    <div class="admin-card tables-category" data-category="${catKey}">
                        <div class="category-header">
                            ${category.icon} ${category.label}
                            <span style="margin-right: auto; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 12px;">
                                ${categoryTables.length} جداول
                            </span>
                        </div>
                        <div class="category-body">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th style="width: 40%">اسم الجدول</th>
                                        <th style="width: 20%; text-align: center;">عدد السجلات</th>
                                        <th style="width: 40%; text-align: center;">الإجراءات</th>
                                    </tr>
                                </thead>
                                <tbody>
                `;

                categoryTables.forEach(table => {
                    const tableLabel = this.getTableLabel(table.name);
                    html += `
                        <tr data-table="${table.name}">
                            <td><strong>${tableLabel}</strong><br><small style="color: #999;">${table.name}</small></td>
                            <td style="text-align: center;"><span style="background: #667eea; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 600;">${table.count}</span></td>
                            <td>
                                <div class="action-buttons" style="justify-content: center;">
                                    <button class="btn btn-info btn-sm" onclick="dashboard.viewTable('${table.name}')" title="عرض البيانات">
                                        👁️ عرض
                                    </button>
                                    <button class="btn btn-success btn-sm" onclick="dashboard.exportTable('${table.name}')" title="تصدير CSV">
                                        📥 تصدير
                                    </button>
                                    <button class="btn btn-warning btn-sm" onclick="dashboard.truncateTable('${table.name}')" title="حذف جميع البيانات">
                                        🗑️ حذف
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                });

                html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }
        });

        tablesContainer.innerHTML = html;
    }

    /**
     * الحصول على اسم الجدول بالعربية
     */
    getTableLabel(tableName) {
        const labels = {
            'teachers_pending': 'المعلمون المعلقون',
            'teachers': 'المعلمون المفعلون',
            'settings': 'إعدادات المستخدمين',
            'school_grades': 'الصفوف الدراسية',
            'sections': 'الشُعب',
            'section_links': 'روابط الشُعب',
            'student_registrations': 'تسجيلات الطلاب',
            'ai_generated_content': 'محتوى الذكاء الاصطناعي',
            'telegram_groups': 'قروبات تيليجرام',
            'projects': 'المشاريع',
            'students': 'الطلاب',
            'groups': 'المجموعات',
            'project_files': 'ملفات المشاريع',
            'submissions': 'التسليمات',
            'project_otp': 'رموز OTP',
            'otp_logs': 'سجلات OTP'
        };
        return labels[tableName] || tableName;
    }

    /**
     * تصفية الجداول
     */
    filterTables() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const categoryFilter = document.getElementById('categoryFilter').value;

        const categories = document.querySelectorAll('.tables-category');
        
        categories.forEach(category => {
            const catKey = category.dataset.category;
            const rows = category.querySelectorAll('tbody tr');
            
            let categoryVisible = false;

            rows.forEach(row => {
                const tableName = row.dataset.table;
                const tableText = row.textContent.toLowerCase();
                
                const matchesSearch = !searchTerm || tableText.includes(searchTerm);
                const matchesCategory = !categoryFilter || catKey === categoryFilter;
                
                const visible = matchesSearch && matchesCategory;
                row.style.display = visible ? '' : 'none';
                
                if (visible) categoryVisible = true;
            });

            category.style.display = categoryVisible ? '' : 'none';
        });
    }

    /**
     * تصدير جدول واحد
     */
    async exportTable(tableName) {
        try {
            this.showLoading(true);
            const data = await adminAPI.getTableData(tableName, 10000);
            
            if (!data.rows || data.rows.length === 0) {
                this.showError('لا توجد بيانات للتصدير');
                return;
            }

            // تحويل إلى CSV
            const csv = this.convertToCSV(data.rows);
            
            // تحميل الملف
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `${tableName}_${new Date().toISOString().split('T')[0]}.csv`;
            link.click();
            
            this.showSuccess(`✅ تم تصدير ${data.rows.length} سجل من ${tableName}`);
        } catch (error) {
            this.showError('فشل في تصدير البيانات: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * تصدير جميع البيانات
     */
    async exportAllData() {
        if (!confirm('هل تريد تصدير جميع بيانات القاعدة؟\n\nقد يستغرق هذا بعض الوقت.')) {
            return;
        }

        try {
            this.showLoading(true);
            
            for (const table of this.stats.tables) {
                if (table.count > 0) {
                    await this.exportTable(table.name);
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }
            
            this.showSuccess('✅ تم تصدير جميع البيانات بنجاح!');
        } catch (error) {
            this.showError('فشل في تصدير البيانات: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * تحويل البيانات إلى CSV
     */
    convertToCSV(data) {
        if (!data || data.length === 0) return '';

        const headers = Object.keys(data[0]);
        const csvRows = [];

        // Headers
        csvRows.push(headers.join(','));

        // Data
        for (const row of data) {
            const values = headers.map(header => {
                const value = row[header];
                return value ? `"${value}"` : '';
            });
            csvRows.push(values.join(','));
        }

        return csvRows.join('\n');
    }

    /**
     * إظهار/إخفاء loading overlay
     */
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }

    /**
     * عرض جدول محدد
     */
    viewTable(tableName) {
        window.location.href = `/admin/table-viewer.html?table=${tableName}`;
    }

    /**
     * حذف بيانات جدول
     */
    async truncateTable(tableName) {
        if (!confirm(`⚠️ هل أنت متأكد من حذف جميع البيانات من جدول "${tableName}"؟\n\nهذا الإجراء لا يمكن التراجع عنه!`)) {
            return;
        }

        if (!confirm(`⚠️⚠️ تأكيد نهائي: سيتم حذف جميع البيانات من "${tableName}"!`)) {
            return;
        }

        try {
            const result = await adminAPI.truncateTable(tableName);
            this.showSuccess(`✅ تم حذف ${result.deleted_count} سجل من جدول ${tableName}`);
            
            // إعادة تحميل الإحصائيات
            await this.loadStatistics();
        } catch (error) {
            this.showError('فشل في حذف البيانات: ' + error.message);
        }
    }

    /**
     * حذف جميع البيانات من القاعدة
     */
    async wipeAllData() {
        const confirmText = prompt('⚠️⚠️⚠️ عملية خطرة جداً!\n\nلحذف جميع البيانات من القاعدة، اكتب بالضبط:\nDELETE ALL DATA');
        
        if (confirmText !== 'DELETE ALL DATA') {
            this.showError('تم إلغاء العملية');
            return;
        }

        const password = prompt('أدخل كلمة مرور المدير للتأكيد النهائي:');
        if (!password) {
            this.showError('تم إلغاء العملية');
            return;
        }

        try {
            const result = await adminAPI.wipeAllData(password);
            this.showSuccess(`✅ تم حذف ${result.total_deleted} سجل من القاعدة بنجاح`);
            
            // إعادة تحميل الإحصائيات
            await this.loadStatistics();
        } catch (error) {
            this.showError('فشل في حذف البيانات: ' + error.message);
        }
    }

    /**
     * حذف جدول واحد فقط
     */
    async deleteTable(tableName, modelName) {
        const tableNames = {
            'projects': 'المشاريع',
            'project_files': 'ملفات المشاريع',
            'school_grades': 'الصفوف الدراسية',
            'sections': 'الشُعب',
            'section_links': 'روابط الشُعب',
            'telegram_groups': 'قروبات Telegram',
            'student_registrations': 'تسجيلات الطلاب',
            'teacher_join_links': 'روابط المعلمين',
            'ai_generated_content': 'محتوى AI'
        };

        const arabicName = tableNames[tableName] || tableName;
        
        const confirmed = confirm(`⚠️ هل أنت متأكد من حذف جميع ${arabicName}؟\n\nهذه العملية لا يمكن التراجع عنها!`);
        
        if (!confirmed) {
            return;
        }

        try {
            this.showLoading();
            const result = await adminAPI.truncateTable(tableName);
            this.hideLoading();
            
            this.showSuccess(`✅ تم حذف ${result.deleted_count || 0} سجل من ${arabicName} بنجاح`);
            
            // إعادة تحميل الإحصائيات
            await this.loadStatistics();
        } catch (error) {
            this.hideLoading();
            this.showError(`فشل في حذف ${arabicName}: ` + error.message);
        }
    }

    /**
     * إظهار شاشة التحميل
     */
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }

    /**
     * إخفاء شاشة التحميل
     */
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    /**
     * عرض رسالة نجاح
     */
    showSuccess(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success';
        alertDiv.textContent = message;
        
        const container = document.querySelector('.admin-container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => alertDiv.remove(), 5000);
    }

    /**
     * عرض رسالة خطأ
     */
    showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger';
        alertDiv.textContent = message;
        
        const container = document.querySelector('.admin-container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// إنشاء instance عام
const dashboard = new AdminDashboard();
