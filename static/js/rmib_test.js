// ==================== RMIB LEVEL-BASED TEST ====================
// File: static/js/rmib_test_level.js
// Version: 1.0 - Production Ready
// Desc: Complete level-based RMIB test implementation

'use strict';

// ==================== GLOBAL STATE ====================
const RMIB_DATA = {
    categories: window.RMIB_CATEGORIES || {},
    studentId: window.STUDENT_ID,
    studentName: window.STUDENT_NAME,
    hasProgress: window.HAS_PROGRESS
};

let levels = {}; // Store current levels {category_key: level_value}
let autoSaveInterval = null;
let confirmCallback = null;
let listenersInitialized = false;

console.log('🎯 RMIB Level-Based Test Initialized', {
    studentId: RMIB_DATA.studentId,
    studentName: RMIB_DATA.studentName,
    hasProgress: RMIB_DATA.hasProgress,
    totalCategories: Object.keys(RMIB_DATA.categories).length
});

// ==================== UTILITY FUNCTIONS ====================

/**
 * Get CSRF token dari berbagai sumber
 */
function getCsrfToken() {
    console.log('🔍 Searching for CSRF token...');
    
    // Method 1: From hidden input (most reliable)
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenInput && tokenInput.value) {
        console.log('✅ CSRF token found in hidden input');
        return tokenInput.value;
    }
    
    // Method 2: From cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            const token = decodeURIComponent(cookie.substring(10));
            console.log('✅ CSRF token found in cookie');
            return token;
        }
    }
    
    // Method 3: From meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta && csrfMeta.content) {
        console.log('✅ CSRF token found in meta tag');
        return csrfMeta.content;
    }
    
    console.warn('⚠️ CSRF token not found');
    return null;
}

/**
 * Show toast notification
 */
function showToast(type, title, message) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        console.error('Toast container not found');
        return;
    }
    
    const colorMap = {
        'success': { bg: 'bg-green-500', icon: 'fa-check-circle' },
        'error': { bg: 'bg-red-500', icon: 'fa-exclamation-circle' },
        'warning': { bg: 'bg-yellow-500', icon: 'fa-exclamation-triangle' },
        'info': { bg: 'bg-blue-500', icon: 'fa-info-circle' }
    };
    
    const config = colorMap[type] || colorMap['info'];
    
    const toast = document.createElement('div');
    toast.className = `bg-white rounded-lg shadow-lg p-4 border-l-4 ${config.bg} border-opacity-20 animate-slideInRight`;
    toast.innerHTML = `
        <div class="flex items-start space-x-3">
            <i class="fas ${config.icon} text-lg" style="color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};"></i>
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
    
    console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
}

/**
 * Show loading modal
 */
function showLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

/**
 * Hide loading modal
 */
function hideLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

/**
 * Show confirmation modal
 */
function showConfirmationModal(title, message, callback) {
    console.log('📋 Showing confirmation:', title);
    
    const modal = document.getElementById('confirmationModal');
    if (!modal) {
        console.error('Confirmation modal not found');
        return;
    }
    
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    
    confirmCallback = callback;
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
}

/**
 * Hide confirmation modal
 */
function hideConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    }
    confirmCallback = null;
}

// ==================== DOM INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM Content Loaded');
    console.log('📊 Categories count:', Object.keys(RMIB_DATA.categories).length);
    
    // Initialize event listeners
    initializeEventListeners();
});

// ==================== EVENT LISTENERS ====================

function initializeEventListeners() {
    if (listenersInitialized) {
        console.log('⚠️ Listeners already initialized');
        return;
    }
    
    console.log('🔧 Initializing event listeners...');
    
    try {
        // Start test button
        const startTestBtn = document.getElementById('startTestBtn');
        if (startTestBtn) {
            startTestBtn.addEventListener('click', startTest);
            console.log('✅ Start test button listener attached');
        }
        
        // Submit button
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', submitTest);
            console.log('✅ Submit button listener attached');
        }
        
        // Confirmation modal buttons
        const confirmYesBtn = document.getElementById('confirmYesBtn');
        const confirmNoBtn = document.getElementById('confirmNoBtn');
        
        if (confirmYesBtn) {
            confirmYesBtn.addEventListener('click', () => {
                if (confirmCallback && typeof confirmCallback === 'function') {
                    confirmCallback();
                }
                hideConfirmationModal();
            });
            console.log('✅ Confirm yes button listener attached');
        }
        
        if (confirmNoBtn) {
            confirmNoBtn.addEventListener('click', hideConfirmationModal);
            console.log('✅ Confirm no button listener attached');
        }
        
        listenersInitialized = true;
        console.log('✅ All event listeners initialized');
    } catch (error) {
        console.error('❌ Error initializing listeners:', error);
    }
}

// ==================== TEST FLOW ====================

/**
 * Start atau resume test
 */
async function startTest() {
    try {
        console.log('🚀 === START TEST ===');
        showLoading();
        
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }
        
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/start/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Start response:', data);
        
        if (data.success) {
            // Hide instructions
            const instructionsPanel = document.getElementById('instructionsPanel');
            if (instructionsPanel) {
                instructionsPanel.classList.add('hidden');
            }
            
            // Show test interface
            const testInterface = document.getElementById('testInterface');
            if (testInterface) {
                testInterface.classList.remove('hidden');
                testInterface.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            
            // Load existing progress if available
            if (RMIB_DATA.hasProgress) {
                console.log('📥 Loading saved progress...');
                await loadProgress();
            } else {
                // Initialize with default level (middle value)
                console.log('📝 Initializing new levels...');
                Object.keys(RMIB_DATA.categories).forEach(key => {
                    levels[key] = 6; // Default middle value
                });
            }
            
            // Render categories
            renderCategories();
            
            // Start auto-save
            startAutoSave();
            
            hideLoading();
            
            const message = RMIB_DATA.hasProgress 
                ? 'Progress dimuat. Lanjutkan pengerjaan!' 
                : 'Mulai memilih level untuk setiap kategori';
            showToast('success', 'Tes Dimulai', message);
        } else {
            hideLoading();
            showToast('error', 'Gagal Memulai', data.message || 'Terjadi kesalahan');
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Start test error:', error);
        showToast('error', 'Error', `Gagal memulai tes: ${error.message}`);
    }
}

/**
 * Render semua kategori dengan slider
 */
function renderCategories() {
    console.log('🎨 Rendering categories...');
    
    const container = document.getElementById('categoriesContainer');
    if (!container) {
        console.error('Categories container not found');
        return;
    }
    
    container.innerHTML = '';
    
    const categories = Object.entries(RMIB_DATA.categories);
    console.log(`📊 Rendering ${categories.length} categories`);
    
    categories.forEach(([categoryKey, category]) => {
        const currentLevel = levels[categoryKey] || 6;
        const score = currentLevel * 5;
        
        const card = document.createElement('div');
        card.className = 'category-card bg-white rounded-xl shadow-lg p-6 border-2 border-gray-200 hover:border-blue-400';
        
        card.innerHTML = `
            <div class="flex items-center space-x-4 mb-5">
                <div class="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center text-xl flex-shrink-0 shadow-lg">
                    <i class="fas ${category.icon}"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <h3 class="font-bold text-gray-900 text-sm truncate">${category.name}</h3>
                    <p class="text-xs text-gray-600 truncate">${category.description}</p>
                </div>
            </div>
            
            <div class="space-y-4">
                <!-- Level Range Label -->
                <div class="flex justify-between text-xs text-gray-500 font-semibold">
                    <span>1</span>
                    <span class="font-bold text-gray-700">Level</span>
                    <span>12</span>
                </div>
                
                <!-- Slider -->
                <input type="range" 
                       min="1" 
                       max="12" 
                       value="${currentLevel}"
                       data-category="${categoryKey}"
                       class="level-slider w-full cursor-pointer"
                       oninput="updateLevel('${categoryKey}', this.value)">
                
                <!-- Level Scale Info -->
                <div class="flex justify-between text-xs text-gray-500">
                    <span>Tidak Sesuai</span>
                    <span>Sangat Sesuai</span>
                </div>
                
                <!-- Level Display & Score -->
                <div class="flex justify-between items-center pt-3 border-t border-gray-200">
                    <div>
                        <p class="level-label">Level Pilihan</p>
                        <p class="level-display">${currentLevel}</p>
                    </div>
                    <div class="text-center">
                        <p class="level-label">Poin</p>
                        <p class="score-display">${score}</p>
                    </div>
                    <div class="text-right">
                        <p class="level-label">Max</p>
                        <p class="text-2xl font-bold text-gray-400">60</p>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
    
    console.log('✅ Categories rendered');
    updateProgress();
}

/**
 * Update level saat slider berubah
 */
function updateLevel(categoryKey, value) {
    const newLevel = parseInt(value);
    
    if (isNaN(newLevel) || newLevel < 1 || newLevel > 12) {
        console.error('Invalid level value:', value);
        return;
    }
    
    levels[categoryKey] = newLevel;
    
    console.log(`📊 Level updated: ${categoryKey} = ${newLevel} (${newLevel * 5} poin)`);
    
    // Update display immediately
    updateProgress();
    
    // Auto-save (will be triggered by auto-save interval, not here to reduce server calls)
}

/**
 * Update progress display
 */
function updateProgress() {
    const filledCount = Object.keys(levels).filter(key => levels[key] > 0).length;
    const totalCategories = Object.keys(RMIB_DATA.categories).length;
    
    // Calculate total score
    let totalScore = 0;
    Object.values(levels).forEach(level => {
        if (level && typeof level === 'number') {
            totalScore += level * 5;
        }
    });
    
    const progressPercentage = (filledCount / totalCategories) * 100;
    
    // Update display
    document.getElementById('filledCount').textContent = filledCount;
    document.getElementById('totalScore').textContent = `${totalScore} poin`;
    document.getElementById('progressBar').style.width = progressPercentage + '%';
    
    console.log(`📈 Progress: ${filledCount}/${totalCategories} (${totalScore} poin)`);
    
    // Enable/disable submit button
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        if (filledCount === totalCategories) {
            submitBtn.classList.remove('btn-disabled');
        } else {
            submitBtn.classList.add('btn-disabled');
        }
    }
}

// ==================== SAVE & LOAD ====================

/**
 * Auto-save progress ke server
 */
async function saveProgress() {
    try {
        const csrfToken = getCsrfToken();
        
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ levels: levels })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('id-ID', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            console.log(`✅ Progress saved at ${timeStr}`);
        } else {
            console.warn('⚠️ Save response not successful:', data.message);
        }
    } catch (error) {
        console.error('❌ Save progress error:', error);
    }
}

/**
 * Load saved progress dari server
 */
async function loadProgress() {
    try {
        console.log('📥 Loading progress...');
        
        const csrfToken = getCsrfToken();
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/load/`, {
            method: 'GET',
            headers: { 'X-CSRFToken': csrfToken }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.has_progress) {
            levels = data.levels;
            console.log('✅ Progress loaded:', levels);
            return true;
        } else {
            console.log('ℹ️ No progress found');
            return false;
        }
    } catch (error) {
        console.error('❌ Load progress error:', error);
        return false;
    }
}

/**
 * Start auto-save interval (setiap 30 detik)
 */
function startAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
    }
    
    autoSaveInterval = setInterval(() => {
        if (Object.keys(levels).length > 0) {
            saveProgress();
        }
    }, 30000); // 30 seconds
    
    console.log('⏱️ Auto-save started (every 30 seconds)');
}

/**
 * Stop auto-save
 */
function stopAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
        autoSaveInterval = null;
        console.log('⏹️ Auto-save stopped');
    }
}

// ==================== SUBMIT TEST ====================

/**
 * Submit test - show confirmation first
 */
function submitTest() {
    const totalCategories = Object.keys(RMIB_DATA.categories).length;
    const filledCount = Object.keys(levels).filter(key => levels[key] > 0).length;
    
    if (filledCount < totalCategories) {
        showToast('warning', 'Belum Lengkap', 
            `Anda baru mengisi ${filledCount} dari ${totalCategories} kategori`);
        return;
    }
    
    console.log('🔍 All categories filled, showing confirmation');
    
    showConfirmationModal(
        'Kirim Tes?',
        'Setelah mengirim, Anda tidak dapat mengubah jawaban lagi. Data akan disimpan permanent.',
        submitFinalResults
    );
}

/**
 * Submit final results ke server
 */
async function submitFinalResults() {
    try {
        console.log('🚀 === FINAL SUBMIT ===');
        showLoading();
        
        const csrfToken = getCsrfToken();
        
        // Validate all categories filled
        const totalCategories = Object.keys(RMIB_DATA.categories).length;
        if (Object.keys(levels).length !== totalCategories) {
            throw new Error(`Data tidak lengkap: ${Object.keys(levels).length}/${totalCategories}`);
        }
        
        // Validate level ranges
        for (const [category, level] of Object.entries(levels)) {
            const levelInt = parseInt(level);
            if (isNaN(levelInt) || levelInt < 1 || levelInt > 12) {
                throw new Error(`Level invalid untuk ${category}: ${level}`);
            }
        }
        
        console.log('✅ All validations passed');
        console.log('📤 Submitting levels:', levels);
        
        // Submit to server
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ levels: levels })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Submit response:', data);
        
        hideLoading();
        
        if (data.success) {
            // Stop auto-save
            stopAutoSave();
            
            // Show success message
            const message = `Total Skor Anda: ${data.total_score} poin\nMinat Utama: ${data.primary_interest} (Level ${data.primary_level})`;
            showToast('success', 'Tes Berhasil Diselesaikan!', message);
            
            console.log('✅ Test submitted successfully');
            
            // Redirect after 2 seconds
            setTimeout(() => {
                window.location.href = data.redirect_url || `/students/${RMIB_DATA.studentId}/rmib/result/`;
            }, 2000);
        } else {
            showToast('error', 'Gagal Mengirim', data.message || 'Terjadi kesalahan server');
            console.error('❌ Submit failed:', data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Final submit error:', error);
        showToast('error', 'Error', `Gagal mengirim tes: ${error.message}`);
    }
}

// ==================== PAGE UNLOAD PROTECTION ====================

/**
 * Warn user jika ada unsaved progress
 */
window.addEventListener('beforeunload', function (e) {
    const totalCategories = Object.keys(RMIB_DATA.categories).length;
    const filledCount = Object.keys(levels).filter(key => levels[key] > 0).length;
    
    // Hanya warn jika ada progress tapi belum complete
    if (filledCount > 0 && filledCount < totalCategories) {
        e.preventDefault();
        e.returnValue = '';
        console.log('⚠️ Unsaved progress warning shown');
    }
});

/**
 * Submit test - bisa jadi new atau edited
 */
async function finalSubmit() {
    try {
        console.log('🚀 Submitting test...');
        showLoading();
        
        const csrfToken = getCsrfToken();
        const isEdit = window.location.href.includes('edit');
        const endpoint = isEdit 
            ? `/students/${RMIB_DATA.studentId}/rmib/submit-edited/`
            : `/students/${RMIB_DATA.studentId}/rmib/submit/`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ levels: levels })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            stopAutoSave();
            
            const message = isEdit 
                ? `Hasil tes berhasil diperbarui!\nTotal skor baru: ${data.total_score} poin`
                : `Total skor Anda: ${data.total_score} poin\nMinat utama: ${data.primary_interest} (Level ${data.primary_level})`;
            
            showToast('success', 'Berhasil!', message);
            
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 2000);
        } else {
            showToast('error', 'Gagal', data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('Submit error:', error);
        showToast('error', 'Error', error.message);
    }
}


// ==================== LOGGING ====================

console.log('✅ RMIB Level-Based Test Script Loaded Successfully');
console.log('📊 Total categories:', Object.keys(RMIB_DATA.categories).length);
console.log('👤 Student:', RMIB_DATA.studentName, `(ID: ${RMIB_DATA.studentId})`);
console.log('📝 Has progress:', RMIB_DATA.hasProgress);
