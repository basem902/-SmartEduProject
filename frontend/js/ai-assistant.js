/**
 * AI Assistant - Smart Content Generation System
 * Generates project content intelligently with single click
 */

// ✅ UPDATE FLOATING BUTTON VISIBILITY
function updateFloatingAIButton() {
    const button = document.getElementById('floatingAIButton');
    if (!button) return;
    
    const emptyFields = detectEmptyFields();
    const badge = document.getElementById('emptyFieldsCount');
    
    if (emptyFields.count > 0) {
        button.style.display = 'flex';
        if (badge) {
            badge.textContent = emptyFields.count;
        }
    } else {
        button.style.display = 'none';
    }
}

// ✅ DETECT EMPTY FIELDS
function detectEmptyFields() {
    const fields = {
        description: document.getElementById('projectDescription'),
        instructions: document.getElementById('projectInstructions'),
        requirements: document.getElementById('projectRequirements'),
        tips: document.getElementById('projectTips')
    };
    
    const empty = {
        fields: [],
        count: 0
    };
    
    for (const [name, element] of Object.entries(fields)) {
        if (element && (!element.value || element.value.trim().length === 0)) {
            empty.fields.push(name);
            empty.count++;
        }
    }
    
    return empty;
}

// ✅ UPDATE AI PREVIEW
function updateAIPreview() {
    // Update context preview
    const titleElement = document.getElementById('aiContextTitle');
    const subjectElement = document.getElementById('aiContextSubject');
    const gradeElement = document.getElementById('aiContextGrade');
    
    if (titleElement) {
        titleElement.textContent = projectData.title || 'لم يتم الإدخال بعد';
    }
    
    if (subjectElement) {
        subjectElement.textContent = projectData.subject || 'لم يتم الاختيار';
    }
    
    if (gradeElement) {
        // Get grade name from select
        const gradeSelect = document.getElementById('gradeSelect');
        if (gradeSelect && gradeSelect.selectedIndex > 0) {
            gradeElement.textContent = gradeSelect.options[gradeSelect.selectedIndex].text;
        } else {
            gradeElement.textContent = 'لم يتم الاختيار';
        }
    }
    
    // Update total count based on selected checkboxes
    const totalElement = document.getElementById('aiTotalItems');
    if (totalElement) {
        let total = 0;
        if (document.getElementById('aiGenDescription')?.checked) total += 1; // Description (1)
        if (document.getElementById('aiGenInstructions')?.checked) total += 5;
        if (document.getElementById('aiGenRequirements')?.checked) total += 5;
        if (document.getElementById('aiGenTips')?.checked) total += 5;
        
        totalElement.textContent = total;
    }
}

// ✅ OPEN AI ASSISTANT MODAL
function openAIAssistant() {
    const modal = document.getElementById('aiAssistantModal');
    if (!modal) return;
    
    // Update context preview
    updateAIPreview();
    
    // Update field statuses
    updateFieldStatuses();
    
    // Auto-check only empty fields
    const emptyFields = detectEmptyFields();
    document.getElementById('aiGenDescription').checked = emptyFields.fields.includes('description');
    document.getElementById('aiGenInstructions').checked = emptyFields.fields.includes('instructions');
    document.getElementById('aiGenRequirements').checked = emptyFields.fields.includes('requirements');
    document.getElementById('aiGenTips').checked = emptyFields.fields.includes('tips');
    
    // Update total after auto-checking
    updateAIPreview();
    
    modal.style.display = 'flex';
    
    // Add event listeners for checkbox changes
    ['aiGenDescription', 'aiGenInstructions', 'aiGenRequirements', 'aiGenTips'].forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', updateAIPreview);
        }
    });
    
    // Add event listeners for status updates
    ['projectDescription', 'projectInstructions', 'projectRequirements', 'projectTips'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', updateFieldStatuses);
        }
    });
}

// ✅ CLOSE AI ASSISTANT MODAL
function closeAIAssistant() {
    const modal = document.getElementById('aiAssistantModal');
    if (!modal) return;
    
    modal.style.display = 'none';
    
    // Reset progress
    const progress = document.getElementById('aiProgress');
    if (progress) {
        progress.style.display = 'none';
    }
}

// ✅ UPDATE FIELD STATUSES
function updateFieldStatuses() {
    const statusMap = {
        'projectDescription': 'statusDescription',
        'projectInstructions': 'statusInstructions',
        'projectRequirements': 'statusRequirements',
        'projectTips': 'statusTips'
    };
    
    for (const [fieldId, statusId] of Object.entries(statusMap)) {
        const field = document.getElementById(fieldId);
        const status = document.getElementById(statusId);
        
        if (field && status) {
            const isEmpty = !field.value || field.value.trim().length === 0;
            status.textContent = isEmpty ? 'فارغ' : '✓ ممتلئ';
            status.className = isEmpty ? 'ai-status' : 'ai-status filled';
        }
    }
}

// ✅ GENERATE ALL WITH AI
async function generateAllWithAI() {
    // Get selected fields
    const toGenerate = {
        description: document.getElementById('aiGenDescription').checked,
        instructions: document.getElementById('aiGenInstructions').checked,
        requirements: document.getElementById('aiGenRequirements').checked,
        tips: document.getElementById('aiGenTips').checked
    };
    
    // Check if at least one is selected
    if (!Object.values(toGenerate).some(v => v)) {
        showAlert('يرجى اختيار حقل واحد على الأقل للتوليد', 'warning');
        return;
    }
    
    // Get context from global projectData or DOM
    const title = projectData.title || document.getElementById('projectTitle')?.value?.trim() || '';
    const subject = projectData.subject || document.getElementById('projectSubject')?.value || '';
    
    console.log('📝 Project Data:', {
        title: title,
        subject: subject,
        gradeId: projectData.gradeId,
        hasProjectData: !!window.projectData
    });
    
    // Subject is more critical than title for AI generation
    if (!subject) {
        showAlert('يرجى اختيار المادة أولاً في Step 1', 'warning');
        return;
    }
    
    // Title is optional - AI can work with just subject
    if (!title) {
        console.warn('⚠️ No title provided, AI will use subject only');
    }
    
    // Show progress
    const progress = document.getElementById('aiProgress');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressDetails = document.getElementById('progressDetails');
    const generateBtn = document.querySelector('.btn-generate');
    
    if (progress) progress.style.display = 'block';
    if (generateBtn) generateBtn.disabled = true;
    
    try {
        const fieldsToGenerate = Object.entries(toGenerate)
            .filter(([_, shouldGenerate]) => shouldGenerate)
            .map(([field, _]) => field);
        
        const totalSteps = fieldsToGenerate.length;
        let completedSteps = 0;
        
        // Generate each field
        for (const field of fieldsToGenerate) {
            // Update progress
            const fieldNameAr = {
                description: 'الوصف',
                instructions: 'التعليمات',
                requirements: 'الشروط',
                tips: 'النصائح'
            }[field];
            
            if (progressDetails) {
                progressDetails.innerHTML = `<div>⏳ جاري توليد ${fieldNameAr}...</div>`;
            }
            
            // Update field status
            const statusId = {
                description: 'statusDescription',
                instructions: 'statusInstructions',
                requirements: 'statusRequirements',
                tips: 'statusTips'
            }[field];
            
            const statusElement = document.getElementById(statusId);
            if (statusElement) {
                statusElement.textContent = 'جاري التوليد...';
                statusElement.className = 'ai-status generating';
            }
            
            // Call AI API with enhanced context
            const token = localStorage.getItem('access_token');
            const API_BASE = window.API_BASE || 'http://localhost:8000/api';
            
            // Build context with all project data
            const context = {
                project_name: title,
                subject: subject,
                description: document.getElementById('projectDescription').value || '',
                grade_id: projectData.gradeId || null,  // من الـ global projectData
                max_grade: projectData.settings?.maxGrade || 100,
                max_items: 5  // بالضبط 5 نقاط لكل قسم
            };
            
            console.log('🤖 Calling AI with context:', context);
            
            const response = await fetch(`${API_BASE}/projects/ai/generate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    content_type: field,  // 'description', 'instructions', 'requirements', 'tips'
                    context: context
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                const content = data.content || data.generated_text || data[field] || '';
                const itemsCount = data.items_count || 0;
                
                console.log(`✅ AI Response for ${field}:`, {
                    content_length: content.length,
                    items_count: itemsCount,
                    content_preview: content.substring(0, 100)
                });
                
                // Validate items count for structured content
                if (field !== 'description') {
                    const lines = content.split('\n').filter(l => l.trim());
                    console.log(`📊 ${fieldNameAr}: ${lines.length} نقطة (المطلوب: 5)`);
                    
                    if (lines.length !== 5) {
                        console.warn(`⚠️ ${fieldNameAr}: عدد النقاط ${lines.length} بدلاً من 5`);
                    }
                }
                
                // Fill field
                const fieldElement = document.getElementById({
                    description: 'projectDescription',
                    instructions: 'projectInstructions',
                    requirements: 'projectRequirements',
                    tips: 'projectTips'
                }[field]);
                
                if (fieldElement) {
                    fieldElement.value = content;
                    
                    // Populate checklist if it's instructions, requirements, or tips
                    if (field === 'instructions' || field === 'requirements' || field === 'tips') {
                        if (typeof populateChecklistFromAI === 'function') {
                            populateChecklistFromAI(field, content);
                        }
                    }
                    
                    // Animate
                    fieldElement.style.backgroundColor = '#d1fae5';
                    setTimeout(() => {
                        fieldElement.style.backgroundColor = '';
                    }, 1000);
                }
                
                // Update status
                if (statusElement) {
                    statusElement.textContent = '✓ مكتمل';
                    statusElement.className = 'ai-status filled';
                }
                
                if (progressDetails) {
                    const itemsInfo = field !== 'description' ? ` (${itemsCount || '5'} نقاط)` : '';
                    progressDetails.innerHTML = `<div>✅ تم توليد ${fieldNameAr}${itemsInfo}</div>`;
                }
            } else {
                // Get error details
                let errorMsg = `Failed to generate ${field}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorData.message || errorMsg;
                    console.error(`❌ API Error for ${field}:`, errorData);
                } catch (e) {
                    console.error(`❌ Failed to parse error response for ${field}`);
                }
                throw new Error(errorMsg);
            }
            
            // Update progress bar
            completedSteps++;
            const percent = Math.round((completedSteps / totalSteps) * 100);
            if (progressFill) progressFill.style.width = `${percent}%`;
            if (progressPercent) progressPercent.textContent = `${percent}%`;
            
            // Small delay between requests
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        // Success
        if (progressDetails) {
            progressDetails.innerHTML = '<div>🎉 تم التوليد بنجاح!</div>';
        }
        
        showAlert('تم توليد المحتوى بنجاح!', 'success');
        
        // Update floating button
        updateFloatingAIButton();
        
        // Close modal after delay
        setTimeout(() => {
            closeAIAssistant();
        }, 2000);
        
    } catch (error) {
        console.error('AI Generation Error:', error);
        showAlert('فشل التوليد بالذكاء الاصطناعي. يرجى المحاولة مرة أخرى.', 'error');
        
        if (progressDetails) {
            progressDetails.innerHTML = '<div style="color: #dc2626;">❌ فشل التوليد</div>';
        }
    } finally {
        if (generateBtn) generateBtn.disabled = false;
    }
}

// ✅ INITIALIZE ON PAGE LOAD
document.addEventListener('DOMContentLoaded', () => {
    // Update button visibility on load
    setTimeout(() => {
        updateFloatingAIButton();
    }, 1000);
    
    // Update on field changes
    ['projectDescription', 'projectInstructions', 'projectRequirements', 'projectTips'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', () => {
                updateFloatingAIButton();
            });
        }
    });
    
    // Update on step changes
    const observer = new MutationObserver(() => {
        updateFloatingAIButton();
    });
    
    const wizardBody = document.querySelector('.wizard-body');
    if (wizardBody) {
        observer.observe(wizardBody, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class']
        });
    }
});

// Export functions
window.openAIAssistant = openAIAssistant;
window.closeAIAssistant = closeAIAssistant;
window.generateAllWithAI = generateAllWithAI;
window.updateFloatingAIButton = updateFloatingAIButton;
