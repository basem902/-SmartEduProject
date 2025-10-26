/**
 * Checklist Manager for Instructions, Requirements, and Tips
 * Converts AI-generated text into interactive checklists with checkboxes
 */

// Example templates
const CHECKLIST_EXAMPLES = {
    instructions: [
        "استخدم برنامج Shotcut لإنشاء الفيديو",
        "اختر مشروعاً حكومياً واحداً (ممنوع التكرار)",
        "اجمع صوراً وفيديوهات عالية الجودة عن المشروع",
        "أضف شاشة نهاية تحتوي على: اسمك الرباعي + الصف + الشعبة",
        "راجع الفيديو وتأكد من المدة (30 ثانية بالضبط)",
        "صدّر الفيديو بصيغة MP4 بجودة HD 1080p"
    ],
    requirements: [
        "عمل فردي (كل طالب فيديو خاص)",
        "المدة: 30 ثانية بالضبط",
        "ممنوع تكرار نفس المشروع الحكومي",
        "جودة الفيديو: HD 1080p",
        "الصيغة: MP4",
        "آخر 5 ثوانٍ: اسم رباعي + صف + شعبة",
        "الصور والمقاطع تناسب الموضوع"
    ],
    tips: [
        "ابدأ مبكراً ولا تؤجل العمل",
        "خطط للسيناريو قبل التصوير",
        "استخدم صوراً عالية الجودة",
        "راقب الوقت باستمرار (30 ثانية بالضبط)",
        "راجع الفيديو عدة مرات قبل التسليم",
        "اطلب رأي زميل أو أحد أفراد العائلة"
    ]
};

/**
 * Create a single checklist item
 */
function createChecklistItem(fieldName, text, checked = true) {
    const item = document.createElement('div');
    item.className = 'checklist-item new-item';
    if (!checked) item.classList.add('unchecked');
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = checked;
    checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
            item.classList.remove('unchecked');
        } else {
            item.classList.add('unchecked');
        }
        updateHiddenTextarea(fieldName);
    });
    
    const textSpan = document.createElement('span');
    textSpan.className = 'checklist-item-text';
    textSpan.contentEditable = 'true';
    textSpan.textContent = text;
    textSpan.setAttribute('data-placeholder', 'اكتب هنا...');
    textSpan.addEventListener('blur', () => {
        updateHiddenTextarea(fieldName);
    });
    textSpan.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            textSpan.blur();
        }
    });
    
    const actions = document.createElement('div');
    actions.className = 'checklist-item-actions';
    
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn-checklist-action btn-delete';
    deleteBtn.innerHTML = '🗑️';
    deleteBtn.title = 'حذف';
    deleteBtn.addEventListener('click', () => {
        item.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            item.remove();
            updateHiddenTextarea(fieldName);
        }, 300);
    });
    
    actions.appendChild(deleteBtn);
    
    item.appendChild(checkbox);
    item.appendChild(textSpan);
    item.appendChild(actions);
    
    // Remove animation class after animation completes
    setTimeout(() => {
        item.classList.remove('new-item');
    }, 300);
    
    return item;
}

/**
 * Add a new empty item to checklist
 */
function checklistAddItem(fieldName) {
    const container = document.getElementById(`${fieldName}Checklist`);
    const item = createChecklistItem(fieldName, '', true);
    container.appendChild(item);
    
    // Focus on the new item
    const textSpan = item.querySelector('.checklist-item-text');
    textSpan.focus();
}

/**
 * Select all items in checklist
 */
function checklistSelectAll(fieldName) {
    const container = document.getElementById(`${fieldName}Checklist`);
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = true;
        cb.closest('.checklist-item').classList.remove('unchecked');
    });
    updateHiddenTextarea(fieldName);
}

/**
 * Deselect all items in checklist
 */
function checklistDeselectAll(fieldName) {
    const container = document.getElementById(`${fieldName}Checklist`);
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = false;
        cb.closest('.checklist-item').classList.add('unchecked');
    });
    updateHiddenTextarea(fieldName);
}

/**
 * Load example checklist
 */
function checklistLoadExample(fieldName) {
    const container = document.getElementById(`${fieldName}Checklist`);
    container.innerHTML = ''; // Clear existing items
    
    const examples = CHECKLIST_EXAMPLES[fieldName] || [];
    examples.forEach(text => {
        const item = createChecklistItem(fieldName, text, true);
        container.appendChild(item);
    });
    
    updateHiddenTextarea(fieldName);
    showAlert('✅ تم تحميل المثال بنجاح', 'success');
}

/**
 * Update hidden textarea from checklist (for form submission)
 */
function updateHiddenTextarea(fieldName) {
    const container = document.getElementById(`${fieldName}Checklist`);
    const textarea = document.getElementById(`project${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}`);
    
    if (!textarea) return;
    
    const items = container.querySelectorAll('.checklist-item');
    const checkedTexts = [];
    
    items.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        const textSpan = item.querySelector('.checklist-item-text');
        
        if (checkbox.checked && textSpan.textContent.trim()) {
            checkedTexts.push(textSpan.textContent.trim());
        }
    });
    
    // Join with newlines and appropriate prefix (matching AI format)
    let prefix = '';
    if (fieldName === 'instructions') {
        prefix = '- [ ] ';  // Checkbox format for instructions
    } else if (fieldName === 'requirements') {
        prefix = '- [ ] ';  // Checkbox format for requirements
    } else if (fieldName === 'tips') {
        prefix = '💡 ';     // Emoji format for tips
    }
    
    textarea.value = checkedTexts.map(text => {
        // Add prefix if not already there
        if (prefix) {
            // Check if text already has the prefix
            if (fieldName === 'tips' && !text.startsWith('💡')) {
                return prefix + text;
            } else if ((fieldName === 'instructions' || fieldName === 'requirements') && !text.startsWith('- [ ]') && !text.match(/^\d+\./)) {
                return prefix + text;
            }
        }
        return text;
    }).join('\n');
}

/**
 * Populate checklist from AI-generated text
 */
function populateChecklistFromAI(fieldName, aiText) {
    const container = document.getElementById(`${fieldName}Checklist`);
    container.innerHTML = ''; // Clear existing
    
    if (!aiText || !aiText.trim()) {
        return;
    }
    
    // Split by newlines and filter empty lines
    const lines = aiText.split('\n').map(line => line.trim()).filter(line => line);
    
    lines.forEach(line => {
        // Remove ALL common prefixes (multiple checkboxes, numbers, bullets, emojis)
        let cleanText = line;
        
        // Step 1: Remove leading markdown checkbox format: - [ ]
        cleanText = cleanText.replace(/^[\-\*•]\s*\[\s*\]\s*/g, '');
        
        // Step 2: Remove ANY remaining standalone checkboxes (in case there are multiple)
        while (/^\[\s*\]\s*/.test(cleanText)) {
            cleanText = cleanText.replace(/^\[\s*\]\s*/, '');
        }
        
        // Step 3: Remove numbers (1. or 1️⃣ etc.)
        cleanText = cleanText.replace(/^(\d+\.|\d+️⃣)\s*/, '');
        
        // Step 4: Remove bullets (-, *, •)
        cleanText = cleanText.replace(/^[\-\*•]\s*/, '');
        
        // Step 5: Remove emojis (💡 etc.)
        cleanText = cleanText.replace(/^💡\s*/, '');
        
        cleanText = cleanText.trim();
        
        if (cleanText) {
            const item = createChecklistItem(fieldName, cleanText, true);
            container.appendChild(item);
        }
    });
    
    updateHiddenTextarea(fieldName);
    
    console.log(`✅ Populated ${fieldName} checklist with ${lines.length} items`);
}

/**
 * Initialize checklist from existing textarea value (on page load)
 */
function initializeChecklistFromTextarea(fieldName) {
    const textareaId = `project${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}`;
    const textarea = document.getElementById(textareaId);
    const container = document.getElementById(`${fieldName}Checklist`);
    
    if (!textarea || !container) return;
    
    const existingText = textarea.value.trim();
    
    if (existingText) {
        // Populate from existing text
        populateChecklistFromAI(fieldName, existingText);
    } else {
        // Start with empty checklist or load examples
        // Uncomment next line to auto-load examples:
        // checklistLoadExample(fieldName);
    }
}

/**
 * Get checklist data as array (for programmatic access)
 */
function getChecklistData(fieldName) {
    const container = document.getElementById(`${fieldName}Checklist`);
    const items = container.querySelectorAll('.checklist-item');
    const data = [];
    
    items.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        const textSpan = item.querySelector('.checklist-item-text');
        
        data.push({
            text: textSpan.textContent.trim(),
            checked: checkbox.checked
        });
    });
    
    return data;
}

/**
 * Set checklist data from array
 */
function setChecklistData(fieldName, dataArray) {
    const container = document.getElementById(`${fieldName}Checklist`);
    container.innerHTML = '';
    
    dataArray.forEach(({ text, checked }) => {
        const item = createChecklistItem(fieldName, text, checked);
        container.appendChild(item);
    });
    
    updateHiddenTextarea(fieldName);
}

// Initialize checklists on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 Checklist Manager initialized');
    
    // Initialize all three checklists
    ['instructions', 'requirements', 'tips'].forEach(fieldName => {
        initializeChecklistFromTextarea(fieldName);
    });
});

// Export functions for use in other scripts
window.checklistAddItem = checklistAddItem;
window.checklistSelectAll = checklistSelectAll;
window.checklistDeselectAll = checklistDeselectAll;
window.checklistLoadExample = checklistLoadExample;
window.populateChecklistFromAI = populateChecklistFromAI;
window.getChecklistData = getChecklistData;
window.setChecklistData = setChecklistData;
window.updateHiddenTextarea = updateHiddenTextarea;
