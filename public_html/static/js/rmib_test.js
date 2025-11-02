// ==================== RMIB RANKING SYSTEM - DRAG & DROP ====================
// File: static/js/rmib_test_ranking.js
// Version: 3.0 - Production Ready with Amazing UX
// Desc: Drag & drop ranking system untuk RMIB test

'use strict';

// ==================== GLOBAL STATE ====================
const RMIB_DATA = {
    categories: window.RMIB_CATEGORIES || {},
    studentId: window.STUDENT_ID,
    studentName: window.STUDENT_NAME,
    hasProgress: window.HAS_PROGRESS
};

let rankings = []; // Array of category keys in rank order [rank1, rank2, ..., rank12]
let draggedElement = null;
let draggedIndex = null;
let autoSaveInterval = null;
let autoSaveCountdown = null;
let confirmCallback = null;

console.log('🎯 RMIB Ranking System Initialized', {
    studentId: RMIB_DATA.studentId,
    studentName: RMIB_DATA.studentName,
    hasProgress: RMIB_DATA.hasProgress,
    categoriesCount: Object.keys(RMIB_DATA.categories).length
});

// ==================== SCORING SYSTEM ====================
const RANK_SCORES = {
    1: 60, 2: 55, 3: 50, 4: 45, 5: 40, 6: 35,
    7: 30, 8: 25, 9: 20, 10: 15, 11: 10, 12: 5
};

// ==================== UTILITY FUNCTIONS ====================

function getCsrfToken() {
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenInput?.value) return tokenInput.value;
    
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith('csrftoken=')) {
            return decodeURIComponent(cookie.substring(10));
        }
    }
    return null;
}

function showToast(type, title, message) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const icons = {
        success: { icon: 'fa-check-circle', gradient: 'from-green-500 to-emerald-600' },
        error: { icon: 'fa-exclamation-circle', gradient: 'from-red-500 to-rose-600' },
        warning: { icon: 'fa-exclamation-triangle', gradient: 'from-yellow-500 to-orange-600' },
        info: { icon: 'fa-info-circle', gradient: 'from-blue-500 to-indigo-600' }
    };
    
    const config = icons[type] || icons.info;
    
    const toast = document.createElement('div');
    toast.className = 'glass rounded-2xl shadow-2xl p-5 mb-3 transform transition-all duration-300';
    toast.innerHTML = `
        <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br ${config.gradient} flex items-center justify-center flex-shrink-0 shadow-lg">
                <i class="fas ${config.icon} text-white"></i>
            </div>
            <div class="flex-1">
                <p class="font-black text-gray-900 mb-1">${title}</p>
                <p class="text-sm text-gray-700">${message}</p>
            </div>
            <button onclick="this.closest('.glass').remove()" class="text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function showLoading() {
    document.getElementById('loadingModal')?.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingModal')?.classList.add('hidden');
}

function showConfirmationModal(title, message, callback) {
    const modal = document.getElementById('confirmationModal');
    if (!modal) return;
    
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    
    confirmCallback = callback;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function hideConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
    confirmCallback = null;
}

// ==================== DOM INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM Ready');
    initializeEventListeners();
});

// ==================== EVENT LISTENERS ====================

function initializeEventListeners() {
    document.getElementById('startTestBtn')?.addEventListener('click', startTest);
    document.getElementById('submitBtn')?.addEventListener('click', submitRanking);
    
    document.getElementById('confirmYesBtn')?.addEventListener('click', () => {
        confirmCallback?.();
        hideConfirmationModal();
    });
    
    document.getElementById('confirmNoBtn')?.addEventListener('click', hideConfirmationModal);
    
    console.log('✅ Event listeners initialized');
}

// ==================== TEST FLOW ====================

async function startTest() {
    try {
        console.log('🚀 Starting ranking test...');
        console.log('📦 Categories available:', Object.keys(RMIB_DATA.categories).length);
        
        showLoading();
        
        const csrfToken = getCsrfToken();
        if (!csrfToken) throw new Error('CSRF token not found');
        
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/start/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('instructionsPanel')?.classList.add('hidden');
            const testInterface = document.getElementById('testInterface');
            testInterface?.classList.remove('hidden');
            testInterface?.scrollIntoView({ behavior: 'smooth' });
            
            if (RMIB_DATA.hasProgress) {
                const loaded = await loadProgress();
                if (!loaded) {
                    console.log('⚠️ Progress load failed, initializing default');
                    initializeDefaultRanking();
                }
            } else {
                initializeDefaultRanking();
            }
            
            // Check if rankings is populated
            if (!rankings || rankings.length === 0) {
                throw new Error('Rankings initialization failed');
            }
            
            renderRanking();
            startAutoSave();
            hideLoading();
            
            showToast('success', 'Tes Dimulai!', 
                `${rankings.length} kategori siap diurutkan`);
        } else {
            hideLoading();
            showToast('error', 'Gagal', data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Start error:', error);
        console.error('Stack:', error.stack);
        showToast('error', 'Error', error.message);
    }
}


// ==================== RANKING LOGIC ====================

function initializeDefaultRanking() {
    const categoryKeys = Object.keys(RMIB_DATA.categories);
    
    if (categoryKeys.length === 0) {
        console.error('❌ No categories found!');
        console.log('RMIB_DATA:', RMIB_DATA);
        showToast('error', 'Error', 'Kategori tidak ditemukan');
        return;
    }
    
    rankings = categoryKeys;
    // Shuffle untuk urutan acak di awal
    rankings.sort(() => Math.random() - 0.5);
    
    console.log('📝 Initialized with', rankings.length, 'categories');
    console.log('📋 Categories:', rankings);
}


function renderRanking() {
    const container = document.getElementById('rankingContainer');
    if (!container) {
        console.error('❌ Ranking container not found');
        return;
    }
    
    if (!rankings || rankings.length === 0) {
        console.error('❌ Rankings array is empty');
        showToast('error', 'Error', 'Tidak ada kategori untuk ditampilkan');
        return;
    }
    
    console.log('🎨 Rendering', rankings.length, 'categories...');
    container.innerHTML = '';
    
    rankings.forEach((categoryKey, index) => {
        const rank = index + 1;
        const category = RMIB_DATA.categories[categoryKey];
        
        if (!category) {
            console.error('❌ Category not found:', categoryKey);
            return;
        }
        
        const score = RANK_SCORES[rank];
        
        const item = document.createElement('div');
        item.className = 'category-item';
        item.draggable = true;
        item.dataset.index = index;
        item.dataset.category = categoryKey;
        
        // Rank badge class
        let rankClass = 'rank-other';
        if (rank === 1) rankClass = 'rank-1';
        else if (rank === 2) rankClass = 'rank-2';
        else if (rank === 3) rankClass = 'rank-3';
        
        item.innerHTML = `
            <div class="flex items-center gap-4 mb-4">
                <div class="rank-badge ${rankClass}">
                    ${rank}
                </div>
                <div class="flex-1 min-w-0">
                    <h3 class="font-black text-gray-900 text-lg truncate">${category.name}</h3>
                    <p class="text-sm text-gray-600 truncate">${category.description}</p>
                </div>
                <div class="text-center">
                    <i class="fas fa-grip-vertical text-gray-400 text-2xl cursor-move"></i>
                </div>
            </div>
            
            <div class="flex items-center justify-between pt-4 border-t-2 border-gray-100">
                <div class="text-center flex-1">
                    <p class="text-xs font-semibold text-gray-600 uppercase mb-1">Rank</p>
                    <p class="text-3xl font-black text-blue-600">#${rank}</p>
                </div>
                <div class="text-center flex-1">
                    <p class="text-xs font-semibold text-gray-600 uppercase mb-1">Poin</p>
                    <p class="score-display">${score}</p>
                </div>
            </div>
        `;
        
        // Add drag events
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('drop', handleDrop);
        item.addEventListener('dragenter', handleDragEnter);
        item.addEventListener('dragleave', handleDragLeave);
        
        container.appendChild(item);
    });
    
    console.log('✅ Rendered', rankings.length, 'items');
}

// ==================== DRAG & DROP HANDLERS ====================

function handleDragStart(e) {
    draggedElement = this;
    draggedIndex = parseInt(this.dataset.index);
    
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
    
    // Visual feedback
    this.style.opacity = '0.5';
    
    console.log(`🎯 Drag started: Rank ${draggedIndex + 1}`);
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    this.style.opacity = '1';
    
    // Remove all drag-over classes
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.remove('drag-over');
    });
    
    draggedElement = null;
    draggedIndex = null;
}

function handleDragOver(e) {
    if (e.preventDefault) e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    if (this !== draggedElement) {
        this.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    if (e.stopPropagation) e.stopPropagation();
    e.preventDefault();
    
    this.classList.remove('drag-over');
    
    if (draggedElement !== this) {
        const targetIndex = parseInt(this.dataset.index);
        
        // Swap rankings
        const draggedCategory = rankings[draggedIndex];
        rankings.splice(draggedIndex, 1);
        rankings.splice(targetIndex, 0, draggedCategory);
        
        console.log(`🔄 Swapped Rank ${draggedIndex + 1} ↔ Rank ${targetIndex + 1}`);
        
        // Re-render with smooth animation
        renderRanking();
        
        // Show feedback
        showToast('info', 'Urutan Diubah', 
            `Kategori dipindahkan ke Rank ${targetIndex + 1}`);
    }
    
    return false;
}

// ==================== AUTO-SAVE ====================

function startAutoSave() {
    let countdown = 30;
    
    // Update timer display
    autoSaveCountdown = setInterval(() => {
        countdown--;
        const timerEl = document.getElementById('autoSaveTimer');
        if (timerEl) timerEl.textContent = countdown;
        
        if (countdown <= 0) {
            countdown = 30;
        }
    }, 1000);
    
    // Auto-save every 30 seconds
    autoSaveInterval = setInterval(() => {
        saveProgress();
        countdown = 30;
    }, 30000);
    
    console.log('⏱️ Auto-save enabled (30s)');
}

function stopAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
        autoSaveInterval = null;
    }
    if (autoSaveCountdown) {
        clearInterval(autoSaveCountdown);
        autoSaveCountdown = null;
    }
    console.log('⏹️ Auto-save stopped');
}

async function saveProgress() {
    try {
        // Convert rankings to levels format
        const levels = {};
        rankings.forEach((categoryKey, index) => {
            const rank = index + 1;
            levels[categoryKey] = rank;
        });
        
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ levels })
        });
        
        const data = await response.json();
        if (data.success) {
            console.log('✅ Progress auto-saved at', new Date().toLocaleTimeString('id-ID'));
        }
    } catch (error) {
        console.error('❌ Save error:', error);
    }
}

async function loadProgress() {
    try {
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/load/`);
        const data = await response.json();
        
        if (data.success && data.has_progress && data.levels) {
            // Convert levels to rankings array
            const levelEntries = Object.entries(data.levels);
            levelEntries.sort((a, b) => a[1] - b[1]); // Sort by level (rank)
            rankings = levelEntries.map(([categoryKey]) => categoryKey);
            
            console.log('✅ Progress loaded:', rankings);
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ Load error:', error);
        return false;
    }
}

// ==================== SUBMIT RANKING ====================

function submitRanking() {
    showConfirmationModal(
        'Simpan Ranking?',
        'Setelah disimpan, urutan ranking Anda akan menjadi hasil final. Pastikan urutan sudah benar.',
        submitFinalRanking
    );
}

async function submitFinalRanking() {
    try {
        console.log('🚀 Submitting final ranking...');
        showLoading();
        
        // Convert rankings to levels
        const levels = {};
        rankings.forEach((categoryKey, index) => {
            const rank = index + 1;
            levels[categoryKey] = rank;
        });
        
        // Calculate total score
        let totalScore = 0;
        Object.values(RANK_SCORES).forEach(score => totalScore += score);
        
        console.log('📊 Final levels:', levels);
        console.log('💰 Total score:', totalScore);
        
        const response = await fetch(`/students/${RMIB_DATA.studentId}/rmib/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ levels })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            stopAutoSave();
            
            showToast('success', 'Berhasil!', 
                `Ranking disimpan! Total Skor: ${data.total_score} poin`);
            
            setTimeout(() => {
                window.location.href = data.redirect_url || `/students/${RMIB_DATA.studentId}/rmib/result/`;
            }, 2000);
        } else {
            showToast('error', 'Gagal', data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Submit error:', error);
        showToast('error', 'Error', error.message);
    }
}

// ==================== PAGE UNLOAD PROTECTION ====================

window.addEventListener('beforeunload', (e) => {
    if (rankings.length > 0) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// ==================== KEYBOARD SHORTCUTS (BONUS UX) ====================

document.addEventListener('keydown', (e) => {
    // Ctrl + S = Save progress
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveProgress();
        showToast('info', 'Progress Disimpan', 'Ranking tersimpan manual');
    }
    
    // Ctrl + Enter = Submit
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        submitRanking();
    }
});

// ==================== INIT ====================

console.log('🔍 DEBUG - RMIB_DATA:', RMIB_DATA);
console.log('📊 Categories count:', Object.keys(RMIB_DATA.categories || {}).length);
console.log('📋 Category keys:', Object.keys(RMIB_DATA.categories || {}));

