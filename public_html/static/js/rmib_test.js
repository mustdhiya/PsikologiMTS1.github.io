// ==================== RMIB TEST INTERFACE - COMPLETE JAVASCRIPT ====================
// File: static/js/rmib_test.js
// Purpose: Handle RMIB test interface, progress tracking, and submission

// ==================== GLOBAL STATE ====================
const RMIB_DATA = {
    categories: window.RMIB_CATEGORIES || {},
    questions: window.RMIB_QUESTIONS || {},
    studentId: window.STUDENT_ID || null,
    studentName: window.STUDENT_NAME || '',
    hasProgress: window.HAS_PROGRESS || false
};

let currentCategory = null;
let currentRankings = {};
let completedCategories = new Set();
let autoSaveInterval = null;
let confirmCallback = null;
let listenersInitialized = false;

// ==================== UTILITIES ====================
function getCsrfToken() {
    console.log('🔍 Searching for CSRF token...');
    
    // Method 1: From hidden input
    let token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token) {
        console.log('✅ CSRF token found in hidden input');
        return token.value;
    }
    
    // Method 2: From cookie
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            const value = decodeURIComponent(cookie.substring(name.length + 1));
            console.log('✅ CSRF token found in cookie');
            return value;
        }
    }
    
    // Method 3: From meta tag
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
        console.log('✅ CSRF token found in meta tag');
        return meta.getAttribute('content');
    }
    
    console.error('❌ No CSRF token found!');
    return null;
}

function showToast(type, title, message) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const iconMap = {
        'success': { icon: 'fa-check-circle', color: 'green' },
        'error': { icon: 'fa-exclamation-circle', color: 'red' },
        'warning': { icon: 'fa-exclamation-triangle', color: 'yellow' },
        'info': { icon: 'fa-info-circle', color: 'blue' }
    };
    
    const config = iconMap[type] || iconMap['info'];
    
    const toast = document.createElement('div');
    toast.className = `toast bg-white rounded-lg shadow-lg p-4 border-l-4 border-${config.color}-500`;
    toast.innerHTML = `
        <div class="flex items-start space-x-3">
            <i class="fas ${config.icon} text-${config.color}-500 text-xl mt-0.5"></i>
            <div class="flex-1">
                <p class="font-bold text-gray-800">${title}</p>
                <p class="text-sm text-gray-600">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function showLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) modal.classList.remove('hidden');
}

function hideLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) modal.classList.add('hidden');
}

function showConfirmationModal(title, message, callback) {
    console.log('📢 Showing confirmation modal:', title);
    
    const modal = document.getElementById('confirmationModal');
    if (!modal) {
        console.error('❌ Confirmation modal not found');
        return;
    }
    
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    
    confirmCallback = callback;
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    
    console.log('✅ Modal shown');
}

function hideConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    }
    confirmCallback = null;
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM Content Loaded ===');
    console.log('Student ID:', RMIB_DATA.studentId);
    console.log('Student Name:', RMIB_DATA.studentName);
    console.log('Has Progress:', RMIB_DATA.hasProgress);
    
    initializeEventListeners();
});

// ==================== EVENT LISTENERS ====================
function initializeEventListeners() {
    if (listenersInitialized) {
        console.log('Event listeners already initialized');
        return;
    }
    
    console.log('🔧 Initializing event listeners...');
    
    // Start test button
    const startTestBtn = document.getElementById('startTestBtn');
    if (startTestBtn) {
        startTestBtn.addEventListener('click', startTest);
        console.log('✅ Start test button listener attached');
    }
    
    // Category buttons
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const category = e.currentTarget.dataset.category;
            openCategory(category);
        });
    });
    
    // Close category button
    const closeCategoryBtn = document.getElementById('closeCategoryBtn');
    if (closeCategoryBtn) {
        closeCategoryBtn.addEventListener('click', closeCategory);
    }
    
    // Validate button
    const validateBtn = document.getElementById('validateBtn');
    if (validateBtn) {
        validateBtn.addEventListener('click', validateCurrentCategory);
    }
    
    // Submit category button
    const submitCategoryBtn = document.getElementById('submitCategoryBtn');
    if (submitCategoryBtn) {
        submitCategoryBtn.addEventListener('click', submitCategory);
    }
    
    // Manual save button
    const manualSaveBtn = document.getElementById('manualSaveBtn');
    if (manualSaveBtn) {
        const newBtn = manualSaveBtn.cloneNode(true);
        manualSaveBtn.parentNode.replaceChild(newBtn, manualSaveBtn);
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            manualSave();
        });
    }
    
    // Final submit button
    const finalSubmitBtn = document.getElementById('finalSubmitBtn');
    if (finalSubmitBtn) {
        finalSubmitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            confirmFinalSubmit();
        });
    }
    
    // Review button
    const reviewBtn = document.getElementById('reviewAnswersBtn');
    if (reviewBtn) {
        reviewBtn.addEventListener('click', reviewAnswers);
    }
    
    // Confirmation modal buttons
    const confirmYesBtn = document.getElementById('confirmYesBtn');
    if (confirmYesBtn) {
        confirmYesBtn.addEventListener('click', () => {
            if (confirmCallback) confirmCallback();
            hideConfirmationModal();
        });
    }
    
    const confirmNoBtn = document.getElementById('confirmNoBtn');
    if (confirmNoBtn) {
        confirmNoBtn.addEventListener('click', hideConfirmationModal);
    }
    
    // Random fill button
    const randomBtn = document.getElementById('randomFillBtn');
    if (randomBtn) {
        randomBtn.addEventListener('click', fillRandomRankings);
    }
    
    // Clear all button
    const clearBtn = document.getElementById('clearAllBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAllRankings);
    }
    
    listenersInitialized = true;
    console.log('✅ All event listeners initialized');
}

// ==================== TEST FLOW ====================
async function startTest() {
    try {
        console.log('🚀 === startTest() START ===');
        showLoading();
        
        const csrfToken = getCsrfToken();
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/start/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        const data = await response.json();
        console.log('Response:', data);
        
        if (data.success) {
            // Hide instructions, show test interface
            const instructionsPanel = document.getElementById('instructionsPanel');
            const testInterface = document.getElementById('testInterface');
            
            if (instructionsPanel) instructionsPanel.classList.add('hidden');
            if (testInterface) {
                testInterface.classList.remove('hidden');
                testInterface.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            
            startAutoSave();
            
            // Load saved progress if exists
            if (RMIB_DATA.hasProgress) {
                console.log('📥 Loading saved progress...');
                await loadSavedProgress();
            }
            
            hideLoading();
            showToast('success', 'Tes Dimulai', 
                RMIB_DATA.hasProgress 
                    ? 'Progress Anda telah dimuat. Lanjutkan pengerjaan!' 
                    : 'Selamat mengerjakan tes RMIB. Progress akan otomatis tersimpan setiap 30 detik.');
        } else {
            hideLoading();
            showToast('error', 'Gagal Memulai Tes', data.message || 'Terjadi kesalahan');
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Start test error:', error);
        showToast('error', 'Error', 'Terjadi kesalahan: ' + error.message);
    }
}

function openCategory(categoryKey) {
    console.log(`📖 Opening category: ${categoryKey}`);
    
    currentCategory = categoryKey;
    const category = RMIB_DATA.categories[categoryKey];
    const questions = RMIB_DATA.questions[categoryKey];
    
    if (!category || !questions) {
        console.error('Category or questions not found');
        return;
    }
    
    // Update header
    document.getElementById('currentCategoryTitle').textContent = category.name;
    document.getElementById('currentCategoryDesc').textContent = category.description;
    
    const iconEl = document.getElementById('currentCategoryIcon');
    iconEl.className = `w-12 h-12 rounded-full flex items-center justify-center text-white bg-category-${categoryKey}`;
    iconEl.innerHTML = `<i class="fas ${category.icon}"></i>`;
    
    // Load questions
    loadQuestions(categoryKey, questions);
    
    // Show panel
    document.getElementById('questionsPanel').classList.remove('hidden');
    document.getElementById('questionsPanel').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function loadQuestions(categoryKey, questions) {
    console.log(`📝 Loading questions for ${categoryKey}`);
    
    const questionsList = document.getElementById('questionsList');
    questionsList.innerHTML = '';
    
    // Get saved rankings
    const savedRankings = currentRankings[categoryKey] || {};
    console.log('Saved rankings:', savedRankings);
    
    questions.forEach((question, index) => {
        const questionItem = document.createElement('div');
        questionItem.className = 'flex items-center space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition duration-200';
        
        const savedValue = savedRankings[index.toString()] || savedRankings[index] || '';
        
        questionItem.innerHTML = `
            <div class="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
                ${index + 1}
            </div>
            <div class="flex-1">
                <p class="text-gray-800">${question}</p>
            </div>
            <div class="flex-shrink-0">
                <input type="number" 
                       min="1" 
                       max="12" 
                       data-question-index="${index}"
                       value="${savedValue}"
                       placeholder="1-12"
                       class="ranking-input w-20 px-3 py-2 border-2 border-gray-300 rounded-lg text-center font-bold focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
        `;
        
        questionsList.appendChild(questionItem);
    });
    
    // Attach event listeners
    document.querySelectorAll('.ranking-input').forEach(input => {
        input.addEventListener('input', handleRankingInput);
        input.addEventListener('blur', validateRankingInput);
        
        if (input.value) {
            const event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
        }
    });
    
    // Auto-validate if already completed
    if (completedCategories.has(categoryKey)) {
        console.log(`✅ Category ${categoryKey} already completed, auto-validating...`);
        setTimeout(() => validateCurrentCategory(), 300);
    }
    
    console.log(`✅ Questions loaded for ${categoryKey}`);
}

function handleRankingInput(e) {
    const input = e.target;
    const value = parseInt(input.value);
    
    input.classList.remove('valid', 'invalid', 'duplicate');
    
    if (isNaN(value) || value < 1 || value > 12) {
        if (input.value !== '') input.classList.add('invalid');
        return;
    }
    
    // Check for duplicates
    const allInputs = document.querySelectorAll('.ranking-input');
    let isDuplicate = false;
    
    allInputs.forEach(otherInput => {
        if (otherInput !== input && parseInt(otherInput.value) === value) {
            isDuplicate = true;
        }
    });
    
    if (isDuplicate) {
        input.classList.add('duplicate');
    } else {
        input.classList.add('valid');
    }
    
    document.getElementById('validationWarning').classList.add('hidden');
}

function validateRankingInput(e) {
    const input = e.target;
    const value = parseInt(input.value);
    
    if (isNaN(value) || value < 1 || value > 12) {
        input.classList.remove('valid', 'duplicate');
        input.classList.add('invalid');
    }
}

function validateCurrentCategory() {
    console.log('🔍 Validating current category...');
    
    const inputs = document.querySelectorAll('.ranking-input');
    const rankings = {};
    let isValid = true;
    let errorMessage = '';
    
    // Collect rankings
    inputs.forEach(input => {
        const index = input.dataset.questionIndex;
        const value = parseInt(input.value);
        
        if (isNaN(value) || value < 1 || value > 12) {
            isValid = false;
            errorMessage = 'Semua pertanyaan harus diisi dengan angka 1-12!';
            input.classList.add('invalid');
        } else {
            rankings[index] = value;
            input.classList.remove('invalid');
        }
    });
    
    // Check count
    const values = Object.values(rankings);
    const uniqueValues = new Set(values);
    
    if (values.length !== 12) {
        isValid = false;
        errorMessage = 'Semua 12 pertanyaan harus diisi!';
    } else if (uniqueValues.size !== values.length) {
        isValid = false;
        errorMessage = 'Setiap angka 1-12 hanya boleh digunakan satu kali! Ada angka yang duplikat.';
        
        inputs.forEach(input => {
            const value = parseInt(input.value);
            const count = values.filter(v => v === value).length;
            if (count > 1) input.classList.add('duplicate');
        });
    } else {
        // Check if all numbers 1-12 present
        for (let i = 1; i <= 12; i++) {
            if (!values.includes(i)) {
                isValid = false;
                errorMessage = `Angka ${i} belum digunakan! Pastikan semua angka 1-12 terpakai.`;
                break;
            }
        }
    }
    
    // Show result
    if (isValid) {
        console.log('✅ Validation passed');
        document.getElementById('validationWarning').classList.add('hidden');
        document.getElementById('submitCategoryBtn').classList.remove('btn-disabled');
        showToast('success', 'Validasi Berhasil', 'Semua jawaban sudah benar. Anda bisa menyimpan kategori ini.');
        
        inputs.forEach(input => {
            input.classList.remove('invalid', 'duplicate');
            input.classList.add('valid');
        });
        
        return true;
    } else {
        console.log('❌ Validation failed:', errorMessage);
        document.getElementById('validationWarning').classList.remove('hidden');
        document.getElementById('validationMessage').textContent = errorMessage;
        document.getElementById('submitCategoryBtn').classList.add('btn-disabled');
        showToast('error', 'Validasi Gagal', errorMessage);
        return false;
    }
}

function submitCategory() {
    console.log(`💾 Submitting category: ${currentCategory}`);
    
    if (!validateCurrentCategory()) return;
    
    const inputs = document.querySelectorAll('.ranking-input');
    const rankings = {};
    
    inputs.forEach(input => {
        const index = parseInt(input.dataset.questionIndex);
        const value = parseInt(input.value);
        rankings[index] = value;
    });
    
    currentRankings[currentCategory] = rankings;
    completedCategories.add(currentCategory);
    
    updateProgress();
    markCategoryAsCompleted(currentCategory);
    closeCategory();
    saveProgress();
    
    showToast('success', 'Kategori Disimpan', 
        `Kategori "${RMIB_DATA.categories[currentCategory].name}" berhasil disimpan!`);
    
    // Check if all completed
    if (completedCategories.size === Object.keys(RMIB_DATA.categories).length) {
        console.log('🎉 All categories completed!');
        showSubmitTestSection();
    }
}

function closeCategory() {
    document.getElementById('questionsPanel').classList.add('hidden');
    currentCategory = null;
    document.getElementById('categoryNav').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function markCategoryAsCompleted(categoryKey) {
    const categoryBtn = document.querySelector(`[data-category="${categoryKey}"]`);
    if (categoryBtn && !categoryBtn.classList.contains('completed-indicator')) {
        categoryBtn.classList.add('completed-indicator', 'border-green-500');
        categoryBtn.classList.remove('border-gray-200');
    }
}

function updateProgress() {
    const total = Object.keys(RMIB_DATA.categories).length;
    const completed = completedCategories.size;
    const percentage = Math.round((completed / total) * 100);
    
    document.getElementById('completedCount').textContent = completed;
    document.getElementById('progressBar').style.width = percentage + '%';
    document.getElementById('progressPercentage').textContent = percentage;
}

function showSubmitTestSection() {
    document.getElementById('submitTestSection').classList.remove('hidden');
    document.getElementById('submitTestSection').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ==================== RANDOM & CLEAR ====================
function fillRandomRankings() {
    const inputs = document.querySelectorAll('.ranking-input');
    if (inputs.length === 0) {
        showToast('warning', 'Tidak Ada Input', 'Tidak ada pertanyaan yang dapat diisi.');
        return;
    }

    const rankings = Array.from({ length: 12 }, (_, i) => i + 1);
    shuffleArray(rankings);

    inputs.forEach((input, index) => {
        input.value = rankings[index];
        const event = new Event('input', { bubbles: true });
        input.dispatchEvent(event);
    });

    showToast('success', 'Random Fill Berhasil', 'Semua ranking telah diisi secara random dengan nilai unik 1-12.');
    setTimeout(() => validateCurrentCategory(), 500);
}

function clearAllRankings() {
    const inputs = document.querySelectorAll('.ranking-input');
    if (inputs.length === 0) {
        showToast('warning', 'Tidak Ada Input', 'Tidak ada pertanyaan yang dapat dihapus.');
        return;
    }

    inputs.forEach(input => {
        input.value = '';
        input.classList.remove('valid', 'invalid', 'duplicate');
    });

    document.getElementById('validationWarning').classList.add('hidden');
    document.getElementById('submitCategoryBtn').classList.add('btn-disabled');
    showToast('info', 'Semua Dihapus', 'Semua ranking telah dihapus.');
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// ==================== SAVE & LOAD ====================
async function saveProgress() {
    try {
        const csrfToken = getCsrfToken();
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ rankings: currentRankings })
        });
        
        const data = await response.json();
        if (data.success) {
            const now = new Date();
            const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
            document.getElementById('autoSaveStatus').textContent = `Tersimpan ${timeStr}`;
            console.log('✅ Progress saved');
        }
    } catch (error) {
        console.error('❌ Save error:', error);
    }
}

async function loadSavedProgress() {
    try {
        console.log('📥 === loadSavedProgress() START ===');
        showLoading();
        
        const csrfToken = getCsrfToken();
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/load/`, {
            method: 'GET',
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        const data = await response.json();
        console.log('Load response:', data);
        
        if (data.success && data.has_progress) {
            console.log('✅ Progress found');
            currentRankings = data.rankings;
            
            // Mark completed
            Object.keys(currentRankings).forEach(categoryKey => {
                const rankings = currentRankings[categoryKey];
                
                if (Object.keys(rankings).length === 12) {
                    const values = Object.values(rankings).map(v => parseInt(v));
                    const sortedValues = [...values].sort((a, b) => a - b);
                    const expectedValues = Array.from({ length: 12 }, (_, i) => i + 1);
                    
                    if (JSON.stringify(sortedValues) === JSON.stringify(expectedValues)) {
                        completedCategories.add(categoryKey);
                        markCategoryAsCompleted(categoryKey);
                        console.log(`✅ ${categoryKey} marked as completed`);
                    }
                }
            });
            
            updateProgress();
            
            if (completedCategories.size === Object.keys(RMIB_DATA.categories).length) {
                showSubmitTestSection();
            }
            
            showToast('success', 'Progress Dimuat', 
                `${completedCategories.size} dari ${Object.keys(RMIB_DATA.categories).length} kategori berhasil dimuat.`);
        } else {
            console.log('ℹ️ No progress found');
        }
        
        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('❌ Load error:', error);
        showToast('error', 'Gagal Memuat', error.message);
    }
}

function startAutoSave() {
    if (autoSaveInterval) clearInterval(autoSaveInterval);
    
    autoSaveInterval = setInterval(() => {
        if (Object.keys(currentRankings).length > 0) {
            saveProgress();
        }
    }, 30000); // Every 30 seconds
    
    console.log('⏱️ Auto-save started (every 30 seconds)');
}

// ==================== MANUAL SAVE & SUBMIT ====================
async function manualSave() {
    console.log('=== manualSave() START ===');
    
    const totalCategories = Object.keys(RMIB_DATA.categories).length;
    const completedCount = completedCategories.size;
    
    if (completedCount < totalCategories) {
        showToast('warning', 'Tes Belum Lengkap', 
            `Anda baru menyelesaikan ${completedCount} dari ${totalCategories} kategori.`);
        return;
    }
    
    showConfirmationModal(
        'Simpan Hasil Tes?',
        'Setelah disimpan, Anda tidak dapat mengubah jawaban lagi. Lanjutkan?',
        submitFinalResults
    );
}

async function submitFinalResults() {
    try {
        console.log('🚀 === submitFinalResults() START ===');
        showLoading();
        
        const totalCategories = Object.keys(RMIB_DATA.categories).length;
        if (completedCategories.size !== totalCategories) {
            hideLoading();
            showToast('error', 'Tes Belum Lengkap', 
                `Hanya ${completedCategories.size} kategori selesai.`);
            return;
        }
        
        // Validate rankings
        for (const [categoryKey, rankings] of Object.entries(currentRankings)) {
            const values = Object.values(rankings).map(v => parseInt(v));
            
            if (values.length !== 12) {
                hideLoading();
                showToast('error', 'Data Tidak Lengkap', `Kategori ${categoryKey} tidak lengkap.`);
                return;
            }
            
            const sortedValues = [...values].sort((a, b) => a - b);
            const expectedValues = Array.from({ length: 12 }, (_, i) => i + 1);
            if (JSON.stringify(sortedValues) !== JSON.stringify(expectedValues)) {
                hideLoading();
                showToast('error', 'Ranking Tidak Valid', `Kategori ${categoryKey} invalid.`);
                return;
            }
        }
        
        // Calculate total
        let totalScore = 0;
        Object.values(currentRankings).forEach(rankings => {
            Object.values(rankings).forEach(rank => {
                totalScore += parseInt(rank);
            });
        });
        
        const expectedTotal = 936; // 12 categories × 78
        if (totalScore !== expectedTotal) {
            hideLoading();
            showToast('error', 'Validasi Gagal', 
                `Total skor ${totalScore}, seharusnya ${expectedTotal}.`);
            return;
        }
        
        console.log('✅ All validations passed');
        
        // Submit
        const csrfToken = getCsrfToken();
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ rankings: currentRankings })
        });
        
        const data = await response.json();
        console.log('Submit response:', data);
        
        hideLoading();
        
        if (data.success) {
            if (autoSaveInterval) clearInterval(autoSaveInterval);
            
            showToast('success', 'Tes Berhasil Disimpan!', 
                'Anda akan diarahkan ke halaman hasil...');
            
            setTimeout(() => {
                window.location.href = data.redirect_url || `/students/${RMIB_DATA.studentId}/rmib/result/`;
            }, 2000);
        } else {
            showToast('error', 'Gagal Menyimpan', data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Submit error:', error);
        showToast('error', 'Error', error.message);
    }
}

function confirmFinalSubmit() {
    manualSave();
}

function reviewAnswers() {
    document.getElementById('categoryNav').scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('info', 'Review Jawaban', 'Klik kategori untuk melihat/mengubah jawaban.');
}

// ==================== PREVENT ACCIDENTAL LEAVE ====================
window.addEventListener('beforeunload', function (e) {
    if (completedCategories.size > 0 && completedCategories.size < Object.keys(RMIB_DATA.categories).length) {
        e.preventDefault();
        e.returnValue = '';
    }
});

console.log('✅ RMIB Test Script Loaded');
