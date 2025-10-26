/**
 * Telegram Preview Modal - معاينة المشروع قبل الإرسال
 * 
 * ملاحظة: API_BASE يجب أن يكون معرّف في الصفحة قبل تحميل هذا الملف
 */

// Open Telegram Send Modal with Project Preview
async function sendTelegramNow(projectId, projectTitle) {
    try {
        UI.showToast('جاري تحميل بيانات المشروع...', 'info');
        
        console.log('🔍 Test: Fetching project ID:', projectId);
        
        // Fetch full project details
        const response = await fetch(`${API_BASE}/projects/${projectId}/detail/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load project');
        
        const project = await response.json();
        
        // ✅ اختبار وجود الملفات
        console.log('📦 Test: Full project data:', project);
        console.log('📎 Test: Files array:', project.files);
        console.log('📊 Test: Files count:', project.files ? project.files.length : 0);
        
        if (project.files && project.files.length > 0) {
            console.log('✅ Test: Files found!');
            project.files.forEach((file, index) => {
                console.log(`📄 File ${index + 1}:`, {
                    name: file.file_name || file.name,
                    type: file.file_type,
                    path: file.file_path,
                    link: file.external_link,
                    size: file.file_size
                });
            });
        } else {
            console.warn('⚠️ Test: No files found in response!');
        }
        
        // Show preview modal
        showTelegramPreviewModal(project);
        
    } catch (error) {
        console.error('❌ Test: Error loading project:', error);
        UI.showToast('فشل تحميل بيانات المشروع', 'error');
    }
}

// Show Telegram Preview Modal
function showTelegramPreviewModal(project) {
    console.log('🎨 Test: Rendering modal with project:', project.title);
    console.log('📎 Test: Files in project object:', project.files);
    
    // Test each file individually
    if (project.files && project.files.length > 0) {
        project.files.forEach((file, index) => {
            console.log(`📄 Test: File ${index + 1}:`, {
                name: file.file_name || file.name,
                type: file.file_type,
                external_link: file.external_link,
                file_path: file.file_path
            });
        });
    } else {
        console.warn('⚠️ Test: No files in project!');
    }
    
    const modal = document.createElement('div');
    modal.id = 'telegramPreviewModal';
    modal.className = 'modal-overlay';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 10000; padding: 20px; overflow-y: auto;';
    
    const modalContent = `
        <div style="background: var(--card-bg); border-radius: 16px; max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; padding: 24px; border-radius: 16px 16px 0 0; position: sticky; top: 0; z-index: 1;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; font-size: 24px; font-weight: 700;">📤 معاينة قبل الإرسال</h2>
                        <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px;">راجع التفاصيل واختر الشُعب</p>
                    </div>
                    <button onclick="closeTelegramPreviewModal()" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 24px; line-height: 1; transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">&times;</button>
                </div>
            </div>
            
            <!-- Body -->
            <div style="padding: 24px;">
                <!-- Project Info -->
                <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #0ea5e9;">
                    <h3 style="margin: 0 0 16px 0; color: #0c4a6e; font-size: 18px;">📚 معلومات المشروع</h3>
                    <div style="display: grid; gap: 12px; font-size: 14px;">
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #0369a1; min-width: 120px;">📌 العنوان:</strong>
                            <span style="color: #0c4a6e; font-weight: 600;">${project.title}</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #0369a1; min-width: 120px;">📖 المادة:</strong>
                            <span style="color: #0c4a6e;">${project.subject}</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #0369a1; min-width: 120px;">🏫 الصف:</strong>
                            <span style="color: #0c4a6e;">${project.grade_display || 'غير محدد'}</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #0369a1; min-width: 120px;">🎯 الدرجة:</strong>
                            <span style="color: #0c4a6e;">${project.max_grade || 100} درجة</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #0369a1; min-width: 120px;">🟢 البداية:</strong>
                            <span style="color: #0c4a6e;">${UI.formatDate(project.start_date)}</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #0369a1; min-width: 120px;">🔴 النهاية:</strong>
                            <span style="color: #0c4a6e;">${UI.formatDate(project.deadline)}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Sections Selection -->
                <div style="background: var(--bg-color); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid var(--border-color);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3 style="margin: 0; color: var(--text-color); font-size: 18px;">📊 اختر الشُعب</h3>
                        <div style="display: flex; gap: 8px;">
                            <button onclick="selectAllSections(true)" style="padding: 6px 12px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;">✓ الكل</button>
                            <button onclick="selectAllSections(false)" style="padding: 6px 12px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;">✗ إلغاء</button>
                        </div>
                    </div>
                    <div id="sectionsListTelegram" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px;">
                        ${(project.sections || []).map(section => `
                            <label style="display: flex; align-items: center; gap: 8px; padding: 12px; background: var(--card-bg); border: 2px solid var(--border-color); border-radius: 8px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#0ea5e9'; this.style.background='rgba(14, 165, 233, 0.05)'" onmouseout="this.style.borderColor='var(--border-color)'; this.style.background='var(--card-bg)'">
                                <input type="checkbox" class="section-checkbox" value="${section.id}" checked style="width: 18px; height: 18px; cursor: pointer;">
                                <span style="font-weight: 600; color: var(--text-color);">${section.name}</span>
                            </label>
                        `).join('')}
                    </div>
                    ${(project.sections || []).length === 0 ? '<p style="color: var(--text-muted); text-align: center; padding: 20px;">⚠️ لا توجد شُعب مرتبطة بهذا المشروع</p>' : ''}
                </div>
                
                <!-- Project Details -->
                <div style="background: var(--bg-color); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid var(--border-color);">
                    <h3 style="margin: 0 0 16px 0; color: var(--text-color); font-size: 18px;">📋 تفاصيل المشروع</h3>
                    
                    ${project.description ? `
                        <div style="margin-bottom: 16px;">
                            <strong style="color: var(--text-muted); font-size: 13px;">📝 الوصف:</strong>
                            <p style="color: var(--text-color); margin: 8px 0; line-height: 1.6;">${project.description}</p>
                        </div>
                    ` : ''}
                    
                    ${project.instructions ? `
                        <div style="margin-bottom: 16px;">
                            <strong style="color: var(--text-muted); font-size: 13px;">📋 التعليمات:</strong>
                            <div style="color: var(--text-color); margin: 8px 0; line-height: 1.8;">${formatBulletList(project.instructions)}</div>
                        </div>
                    ` : ''}
                    
                    ${project.requirements ? `
                        <div style="margin-bottom: 16px;">
                            <strong style="color: var(--text-muted); font-size: 13px;">⚠️ الشروط:</strong>
                            <div style="color: var(--text-color); margin: 8px 0; line-height: 1.8;">${formatBulletList(project.requirements)}</div>
                        </div>
                    ` : ''}
                    
                    ${project.tips ? `
                        <div style="margin-bottom: 16px;">
                            <strong style="color: var(--text-muted); font-size: 13px;">💡 النصائح:</strong>
                            <div style="color: var(--text-color); margin: 8px 0; line-height: 1.8;">${formatBulletList(project.tips)}</div>
                        </div>
                    ` : ''}
                </div>
                
                <!-- File Settings -->
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #fbbf24;">
                    <h3 style="margin: 0 0 16px 0; color: #78350f; font-size: 18px;">📎 إعدادات الملفات</h3>
                    <div style="display: grid; gap: 12px; font-size: 14px;">
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #92400e; min-width: 140px;">📁 أنواع الملفات:</strong>
                            <span style="color: #78350f;">${(project.allowed_file_types || []).join(', ') || 'جميع الأنواع'}</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #92400e; min-width: 140px;">📏 الحجم الأقصى:</strong>
                            <span style="color: #78350f;">${project.max_file_size || 10} MB</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <strong style="color: #92400e; min-width: 140px;">⏰ تسليم متأخر:</strong>
                            <span style="color: #78350f;">${project.allow_late_submission ? '✅ مسموح' : '❌ غير مسموح'}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Attached Files -->
                ${(project.files && project.files.length > 0) ? `
                    <div style="background: var(--bg-color); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid var(--border-color);">
                        <h3 style="margin: 0 0 16px 0; color: var(--text-color); font-size: 18px;">📎 الملفات والروابط المساعدة (${project.files.length})</h3>
                        <div style="display: grid; gap: 12px;">
                            ${project.files.map(file => {
                                const isLink = file.file_type === 'link' || file.external_link;
                                const fileName = file.name || file.file_name || 'ملف';
                                const fileIcon = isLink ? '🔗' : (
                                    file.file_type === 'video' ? '🎥' : 
                                    file.file_type === 'pdf' ? '📄' : 
                                    file.file_type === 'doc' ? '📝' : '📎'
                                );
                                
                                if (isLink) {
                                    const link = file.external_link || file.file_path || fileName;
                                    const linkLabel = link.includes('youtube.com') || link.includes('youtu.be') ? 'رابط يوتيوب' : 
                                                     link.includes('drive.google.com') ? 'رابط Google Drive' : 'رابط خارجي';
                                    return `
                                        <div style="padding: 12px; background: rgba(59, 130, 246, 0.05); border: 2px solid #3b82f6; border-radius: 8px; display: flex; align-items: center; gap: 12px;">
                                            <span style="font-size: 24px;">${fileIcon}</span>
                                            <div style="flex: 1; min-width: 0;">
                                                <div style="font-weight: 600; color: var(--text-color); margin-bottom: 4px;">${linkLabel}</div>
                                                <a href="${link}" target="_blank" style="color: #3b82f6; text-decoration: none; font-size: 13px; word-break: break-all; display: block; overflow: hidden; text-overflow: ellipsis;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">${link}</a>
                                            </div>
                                            <button onclick="window.open('${link}', '_blank')" style="padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; white-space: nowrap;" onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">
                                                فتح ↗
                                            </button>
                                        </div>
                                    `;
                                } else {
                                    // للملفات العادية
                                    return `
                                        <div style="padding: 10px 16px; background: rgba(14, 165, 233, 0.1); border: 1px solid #0ea5e9; border-radius: 6px; font-size: 14px; color: var(--text-color); display: flex; align-items: center; gap: 8px;">
                                            <span style="font-size: 20px;">${fileIcon}</span>
                                            <span>${fileName}</span>
                                            ${file.file_size ? `<span style="color: var(--text-muted); font-size: 12px; margin-right: auto;">(${formatFileSize(file.file_size)})</span>` : ''}
                                        </div>
                                    `;
                                }
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
            
            <!-- Footer -->
            <div style="padding: 20px 24px; border-top: 2px solid var(--border-color); background: var(--bg-color); border-radius: 0 0 16px 16px; display: flex; gap: 12px; justify-content: flex-end;">
                <button onclick="closeTelegramPreviewModal()" style="padding: 12px 24px; background: var(--bg-secondary); color: var(--text-color); border: 2px solid var(--border-color); border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.background='var(--border-color)'" onmouseout="this.style.background='var(--bg-secondary)'">
                    ✗ إلغاء
                </button>
                <button onclick="confirmSendTelegram(${project.id}, '${project.title.replace(/'/g, "\\'")}')" style="padding: 12px 32px; background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 700; font-size: 16px; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4); transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(14, 165, 233, 0.5)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(14, 165, 233, 0.4)'">
                    📤 إرسال الآن
                </button>
            </div>
        </div>
    `;
    
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeTelegramPreviewModal();
        }
    });
}

// Format bullet list
function formatBulletList(text) {
    if (!text) return '';
    return text.split('\n').filter(line => line.trim()).map(line => {
        return `<div style="padding: 4px 0;">${line}</div>`;
    }).join('');
}

// Select/Deselect all sections
function selectAllSections(checked) {
    document.querySelectorAll('.section-checkbox').forEach(cb => {
        cb.checked = checked;
    });
}

// Close preview modal
function closeTelegramPreviewModal() {
    const modal = document.getElementById('telegramPreviewModal');
    if (modal) {
        modal.remove();
    }
}

// Confirm and send to Telegram
async function confirmSendTelegram(projectId, projectTitle) {
    // Get selected sections
    const selectedSections = Array.from(document.querySelectorAll('.section-checkbox:checked')).map(cb => parseInt(cb.value));
    
    if (selectedSections.length === 0) {
        UI.showToast('يرجى اختيار شعبة واحدة على الأقل', 'warning');
        return;
    }
    
    closeTelegramPreviewModal();
    UI.showToast('جاري إرسال الإشعار...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}/send-telegram/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                section_ids: selectedSections,
                send_files: true,
                pin_message: true
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            showTelegramResultsModal(data.telegram, projectTitle);
            
            setTimeout(() => {
                if (typeof loadDashboard === 'function') {
                    loadDashboard();
                }
            }, 2000);
        } else {
            const error = await response.json();
            UI.showToast(error.error || 'فشل إرسال الإشعار', 'error');
        }
    } catch (error) {
        console.error('Error sending Telegram:', error);
        UI.showToast('حدث خطأ أثناء إرسال الإشعار', 'error');
    }
}

// Show Telegram Results Modal (النتائج بعد الإرسال)
function showTelegramResultsModal(telegram, projectTitle) {
    const successCount = telegram.success ? telegram.success.length : 0;
    const failedCount = telegram.failed ? telegram.failed.length : 0;
    
    let content = `
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 48px; color: #10b981; margin-bottom: 12px;">✓</div>
            <h3 style="margin: 0; color: var(--text-color);">تم إرسال الإشعار!</h3>
            <p style="color: var(--text-muted); margin-top: 8px;">${projectTitle}</p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; text-align: center;">
                <div style="font-size: 36px; font-weight: bold;">${successCount}</div>
                <div style="font-size: 14px; opacity: 0.9;">تم الإرسال</div>
            </div>
            <div style="background: ${failedCount > 0 ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)'}; color: white; padding: 20px; border-radius: 12px; text-align: center;">
                <div style="font-size: 36px; font-weight: bold;">${failedCount}</div>
                <div style="font-size: 14px; opacity: 0.9;">فشل الإرسال</div>
            </div>
        </div>
    `;
    
    if (successCount > 0) {
        content += `
            <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                <div style="color: #15803d; font-weight: 600; margin-bottom: 8px;">✅ الشُعب التي تم الإرسال لها:</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
        `;
        
        telegram.success.forEach(item => {
            content += `
                <span style="background: white; color: #15803d; padding: 6px 12px; border-radius: 6px; font-size: 13px; border: 1px solid #bbf7d0;">
                    ${item.section_name || item.section_id}
                </span>
            `;
        });
        
        content += `</div></div>`;
    }
    
    if (failedCount > 0) {
        content += `
            <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px;">
                <div style="color: #991b1b; font-weight: 600; margin-bottom: 8px;">⚠️ لم يتم الإرسال:</div>
                <div style="font-size: 13px; color: #7f1d1d;">
        `;
        
        telegram.failed.forEach((item, index) => {
            content += `${item.section_name || item.section_id}${index < failedCount - 1 ? '، ' : ''}`;
        });
        
        content += `</div></div>`;
    }
    
    UI.showModal('نتائج الإرسال للتيليجرام', content, [
        { text: 'حسناً', class: 'btn-primary', onclick: 'UI.closeModal()' }
    ]);
}

// Helper: Format file size
function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
