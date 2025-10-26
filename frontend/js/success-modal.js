/**
 * Success Modal - عرض نتائج إنشاء المشروع
 */

function showSuccessModal(data) {
    const modal = document.createElement('div');
    modal.className = 'success-modal-overlay';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s;
    `;
    
    const project = data.project || {};
    const telegram = data.telegram || {};
    
    let html = `
        <div style="
            background: var(--card-bg, #ffffff);
            border-radius: 20px;
            padding: 40px;
            max-width: 700px;
            width: 90%;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 25px 80px rgba(0,0,0,0.4);
            animation: slideDown 0.4s ease-out;
        ">
            <!-- Success Header -->
            <div style="text-align: center; margin-bottom: 32px;">
                <div style="
                    display: inline-block;
                    width: 80px;
                    height: 80px;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 48px;
                    margin-bottom: 16px;
                    animation: bounceIn 0.6s;
                ">
                    ✓
                </div>
                <h2 style="
                    margin: 0;
                    font-size: 28px;
                    color: var(--text-color, #1f2937);
                    font-weight: 700;
                ">
                    تم إنشاء المشروع بنجاح!
                </h2>
            </div>
            
            <!-- Project Info Card -->
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 24px;
                border-radius: 16px;
                margin-bottom: 24px;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            ">
                <h3 style="margin: 0 0 16px 0; font-size: 20px; font-weight: 600;">
                    📚 ${project.title || 'المشروع الجديد'}
                </h3>
                <div style="display: grid; gap: 12px; font-size: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="opacity: 0.9;">المادة:</span>
                        <strong>${project.subject || '-'}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="opacity: 0.9;">الصف:</span>
                        <strong>${project.grade_display || 'غير محدد'}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="opacity: 0.9;">عدد الشُعب:</span>
                        <strong>${project.sections_count || 0} شُعبة</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="opacity: 0.9;">الدرجة:</span>
                        <strong>${project.max_grade || 0} درجة</strong>
                    </div>
                </div>
            </div>
    `;
    
    // Telegram Results
    if (telegram.sent && telegram.total > 0) {
        const successCount = telegram.success ? telegram.success.length : 0;
        const failedCount = telegram.failed ? telegram.failed.length : 0;
        
        html += `
            <div style="
                background: var(--bg-light, #f9fafb);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 24px;
            ">
                <h4 style="
                    margin: 0 0 16px 0;
                    font-size: 18px;
                    color: var(--text-color, #1f2937);
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span style="font-size: 24px;">📱</span>
                    نتائج الإرسال للتليجرام
                </h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
                    <div style="
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white;
                        padding: 16px;
                        border-radius: 10px;
                        text-align: center;
                    ">
                        <div style="font-size: 32px; font-weight: bold;">${successCount}</div>
                        <div style="font-size: 14px; opacity: 0.9;">تم الإرسال</div>
                    </div>
                    <div style="
                        background: ${failedCount > 0 ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)'};
                        color: white;
                        padding: 16px;
                        border-radius: 10px;
                        text-align: center;
                    ">
                        <div style="font-size: 32px; font-weight: bold;">${failedCount}</div>
                        <div style="font-size: 14px; opacity: 0.9;">فشل الإرسال</div>
                    </div>
                </div>
        `;
        
        // Success details
        if (successCount > 0) {
            html += `
                <div style="
                    background: #f0fdf4;
                    border: 1px solid #86efac;
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 12px;
                ">
                    <div style="color: #15803d; font-weight: 600; margin-bottom: 8px;">
                        ✅ الشُعب التي تم الإرسال لها:
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            `;
            
            telegram.success.forEach(item => {
                html += `
                    <span style="
                        background: white;
                        color: #15803d;
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 13px;
                        border: 1px solid #bbf7d0;
                    ">
                        ${item.section_name || item.section_id}
                    </span>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        // Failed details
        if (failedCount > 0) {
            // Check if all failed because of "No Telegram group found"
            const allNoGroup = telegram.failed.every(item => 
                item.error && item.error.includes('No Telegram group')
            );
            
            html += `
                <div style="
                    background: #fef2f2;
                    border: 1px solid #fca5a5;
                    border-radius: 8px;
                    padding: 12px;
                ">
                    <div style="color: #991b1b; font-weight: 600; margin-bottom: 8px;">
                        ⚠️ لم يتم الإرسال ${allNoGroup ? '(لم يتم إنشاء القروبات بعد)' : ''}:
                    </div>
                    <div style="font-size: 13px; color: #7f1d1d; line-height: 1.8;">
            `;
            
            if (allNoGroup) {
                html += `
                    <strong style="display: block; margin-bottom: 8px;">💡 الحل:</strong>
                    1. اذهب إلى <a href="sections-manage.html" style="color: #dc2626; text-decoration: underline;">إدارة الصفوف</a><br>
                    2. اختر الصف واضغط زر "📱 تيليجرام"<br>
                    3. أنشئ القروبات<br>
                    4. بعدها يمكنك إرسال المشروع من لوحة التحكم<br><br>
                    <strong>الشُعب:</strong> 
                `;
            }
            
            telegram.failed.forEach((item, index) => {
                const sectionName = item.section_name || item.section_id || `شعبة ${index + 1}`;
                const error = item.error ? ` (${item.error})` : '';
                html += `${sectionName}${!allNoGroup ? error : ''}${index < failedCount - 1 ? '، ' : ''}`;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
    } else if (!telegram.sent) {
        html += `
            <div style="
                background: #dbeafe;
                border: 2px solid #3b82f6;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 24px;
                text-align: center;
            ">
                <div style="font-size: 32px; margin-bottom: 12px;">📤</div>
                <p style="margin: 0; color: #1e40af; font-size: 15px; line-height: 1.6;">
                    <strong>لم يتم إرسال إشعار للتليجرام</strong><br>
                    يمكنك إرسال المشروع للقروبات لاحقاً من لوحة التحكم
                </p>
            </div>
        `;
    }
    
    // Action Buttons
    html += `
            <div style="
                display: flex;
                gap: 12px;
                margin-top: 32px;
            ">
                <button onclick="window.location.href='dashboard.html'" style="
                    flex: 1;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 16px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s, box-shadow 0.2s;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                "
                onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.4)'"
                onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.3)'">
                    📊 عودة للوحة التحكم
                </button>
                <button onclick="window.location.href='create-project.html'" style="
                    flex: 1;
                    background: white;
                    color: #667eea;
                    border: 2px solid #667eea;
                    padding: 16px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                "
                onmouseover="this.style.background='#f0f4ff'"
                onmouseout="this.style.background='white'">
                    ➕ إنشاء مشروع آخر
                </button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    // Auto-redirect after 10 seconds
    setTimeout(() => {
        if (modal.parentElement) {
            window.location.href = 'dashboard.html';
        }
    }, 10000);
}

// Animations CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            transform: scale(1);
        }
    }
`;
document.head.appendChild(style);

// Export
window.showSuccessModal = showSuccessModal;
