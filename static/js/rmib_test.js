// ==================== RMIB TEST + ACHIEVEMENT SYSTEM ====================
// File: static/js/rmib_test.js

// ==================== GLOBAL DATA ====================
const RMIB_DATA = {
    studentId: window.STUDENT_ID || 0,
    categories: window.RMIB_CATEGORIES || {},
    hasProgress: window.HAS_PROGRESS || false
};

const RANK_SCORES = {
    1: 60, 2: 55, 3: 50, 4: 45, 5: 40, 6: 35,
    7: 30, 8: 25, 9: 20, 10: 15, 11: 10, 12: 5
};

const POINTS_MATRIX = {
    internasional: { juara_1: 100, juara_2: 90, juara_3: 80, harapan: 70 },
    nasional: { juara_1: 80, juara_2: 70, juara_3: 60, harapan: 50 },
    provinsi: { juara_1: 60, juara_2: 50, juara_3: 40, harapan: 30 },
    kabupaten: { juara_1: 40, juara_2: 35, juara_3: 30, harapan: 20 },
    kecamatan: { juara_1: 20, juara_2: 15, juara_3: 10, harapan: 5 },
    sekolah: { juara_1: 10, juara_2: 8, juara_3: 6, harapan: 4 },
};

// ==================== GLOBAL STATE ====================
let rankings = {};
let achievements = [];

// ==================== UTILITY FUNCTIONS ====================
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function showToast(type, title, msg) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const icons = { 
        success: 'fa-check-circle', 
        error: 'fa-exclamation-circle', 
        info: 'fa-info-circle' 
    };
    const colors = { 
        success: 'from-green-500 to-emerald-600', 
        error: 'from-red-500 to-rose-600', 
        info: 'from-blue-500 to-indigo-600' 
    };
    
    const toast = document.createElement('div');
    toast.className = 'glass rounded-2xl shadow-2xl p-4 mb-3';
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br ${colors[type]} flex items-center justify-center text-white shadow-lg">
                <i class="fas ${icons[type]}"></i>
            </div>
            <div class="flex-1">
                <p class="font-bold text-gray-900 text-sm">${title}</p>
                <p class="text-xs text-gray-600">${msg}</p>
            </div>
        </div>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function showLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) modal.classList.remove('hidden');
}

function hideLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) modal.classList.add('hidden');
}

// ==================== RMIB RANKING FUNCTIONS ====================

async function startTest() {
    try {
        showLoading();
        const res = await fetch(`/students/${RMIB_DATA.studentId}/rmib/start/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() }
        });
        
        const data = await res.json();
        if (data.success) {
            document.getElementById('instructionsPanel')?.classList.add('hidden');
            document.getElementById('testInterface')?.classList.remove('hidden');
            
            Object.keys(RMIB_DATA.categories).forEach(key => { rankings[key] = 0; });
            renderRanking();
            startAutoSave();
            loadAchievementTypes();
            
            hideLoading();
            showToast('success', 'Tes Dimulai', 'Mulai masukkan ranking untuk setiap kategori');
        } else {
            hideLoading();
            showToast('error', 'Gagal', data.message);
        }
    } catch (err) {
        hideLoading();
        showToast('error', 'Error', err.message);
    }
}

function renderRanking() {
    const container = document.getElementById('rankingContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.entries(RMIB_DATA.categories).forEach(([catKey, cat]) => {
        const currentRank = rankings[catKey] || 0;
        const score = currentRank > 0 ? RANK_SCORES[currentRank] : 0;
        const isFilled = currentRank > 0;
        
        const card = document.createElement('div');
        card.className = `category-card ${isFilled ? 'filled' : ''}`;
        
        card.innerHTML = `
            <div class="category-header">
                <div class="category-icon" style="background: linear-gradient(135deg, ${getGradient(catKey)});">
                    <i class="fas ${cat.icon}"></i>
                </div>
                <div class="category-info">
                    <h3>${cat.name}</h3>
                    <p>${cat.description}</p>
                </div>
            </div>
            
            <div class="input-section">
                <div class="input-group">
                    <label class="input-label">Ranking</label>
                    <input 
                        type="number" 
                        min="1" 
                        max="12" 
                        placeholder="1-12"
                        value="${currentRank || ''}"
                        data-category="${catKey}"
                        class="rank-input ${isFilled ? 'filled' : ''}"
                    />
                    <div class="error-message" data-error="${catKey}"></div>
                </div>
                
                <div class="score-box">
                    <span class="score-label">Poin</span>
                    <div class="score-value ${!isFilled ? 'empty' : ''}" data-score="${catKey}">${score || '-'}</div>
                </div>
            </div>
        `;
        
        const input = card.querySelector('.rank-input');
        input.addEventListener('input', (e) => handleRankInput(catKey, e.target.value, card));
        
        container.appendChild(card);
    });
}

function handleRankInput(catKey, value, card) {
    const errorEl = card.querySelector(`[data-error="${catKey}"]`);
    const input = card.querySelector('.rank-input');
    const scoreEl = document.querySelector(`[data-score="${catKey}"]`);
    
    errorEl?.classList.remove('show');
    input.classList.remove('error', 'filled');
    
    if (value === '') {
        rankings[catKey] = 0;
        scoreEl.textContent = '-';
        scoreEl.classList.add('empty');
        card.classList.remove('filled');
        updateProgress();
        return;
    }
    
    const rank = parseInt(value);
    
    if (isNaN(rank) || rank < 1 || rank > 12) {
        errorEl.textContent = 'Masukkan angka 1-12';
        errorEl.classList.add('show');
        input.classList.add('error');
        return;
    }
    
    const duplicate = Object.entries(rankings).find(([k, r]) => k !== catKey && r === rank);
    
    if (duplicate) {
        errorEl.textContent = `Ranking ${rank} sudah digunakan`;
        errorEl.classList.add('show');
        input.classList.add('error');
        return;
    }
    
    rankings[catKey] = rank;
    const score = RANK_SCORES[rank];
    scoreEl.textContent = score;
    scoreEl.classList.remove('empty');
    input.classList.add('filled');
    card.classList.add('filled');
    updateProgress();
}

function updateProgress() {
    const filled = Object.values(rankings).filter(r => r > 0).length;
    const totalScore = Object.values(rankings).reduce((s, r) => s + (r > 0 ? RANK_SCORES[r] : 0), 0);
    
    const totalScoreEl = document.getElementById('totalScoreDisplay');
    if (totalScoreEl) totalScoreEl.textContent = totalScore;
}

function startAutoSave() {
    let countdown = 30;
    
    setInterval(() => {
        countdown--;
        const timerEl = document.getElementById('autoSaveTimer');
        if (timerEl) timerEl.textContent = countdown;
        if (countdown <= 0) countdown = 30;
    }, 1000);
    
    setInterval(() => {
        saveProgress();
    }, 30000);
}

async function saveProgress() {
    try {
        await fetch(`/students/${RMIB_DATA.studentId}/rmib/save/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ levels: rankings })
        });
    } catch (error) {
        console.error('Save error:', error);
    }
}

function getGradient(catKey) {
    const gradients = {
        outdoor: '#10b981, #059669', 
        mechanical: '#3b82f6, #1d4ed8', 
        computational: '#8b5cf6, #6d28d9',
        scientific: '#6366f1, #4338ca', 
        personal_contact: '#ec4899, #be185d', 
        aesthetic: '#f97316, #c2410c',
        literary: '#14b8a6, #0d9488', 
        musical: '#ef4444, #b91c1c', 
        social_service: '#f59e0b, #d97706',
        clerical: '#6b7280, #374151', 
        practical: '#eab308, #a16207', 
        medical: '#dc2626, #991b1b'
    };
    return gradients[catKey] || '#667eea, #764ba2';
}

// ==================== ACHIEVEMENT FUNCTIONS ====================

async function loadAchievementTypes() {
    try {
        console.log('🔄 Loading achievement types...');
        
        const url = `/students/api/achievement-types/`;
        console.log('📍 Fetching from:', url);
        
        const res = await fetch(url);
        
        console.log('📊 Response status:', res.status);
        console.log('📊 Response headers:', res.headers.get('content-type'));
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error(`Expected JSON but got: ${contentType}`);
        }
        
        const data = await res.json();
        console.log('✅ Data received:', data.length, 'items');
        
        const select = document.getElementById('achievement_type');
        if (!select) {
            console.error('❌ Select element not found');
            return;
        }
        
        select.innerHTML = '<option value="">-- Pilih Jenis Prestasi --</option>';
        
        const academic = data.filter(t => t.category === 'academic');
        const nonAcademic = data.filter(t => t.category === 'non_academic');
        
        if (academic.length > 0) {
            const optgroup1 = document.createElement('optgroup');
            optgroup1.label = '🎓 Akademik (' + academic.length + ')';
            academic.forEach(type => {
                const opt = document.createElement('option');
                opt.value = type.id;
                opt.textContent = `${type.name} (${type.rmib_primary || 'N/A'})`;
                optgroup1.appendChild(opt);
            });
            select.appendChild(optgroup1);
        }
        
        if (nonAcademic.length > 0) {
            const optgroup2 = document.createElement('optgroup');
            optgroup2.label = '🎨 Non-Akademik (' + nonAcademic.length + ')';
            nonAcademic.forEach(type => {
                const opt = document.createElement('option');
                opt.value = type.id;
                opt.textContent = `${type.name} (${type.rmib_primary || 'N/A'})`;
                optgroup2.appendChild(opt);
            });
            select.appendChild(optgroup2);
        }
        
        console.log('✅ Dropdown populated!');
        showToast('success', 'Success', `Loaded ${data.length} achievement types`);
        
    } catch (err) {
        console.error('❌ Error:', err);
        showToast('error', 'Error Loading Data', err.message);
    }
}

function calculateAchievementPoints() {
    const level = document.getElementById('level')?.value;
    const rank = document.getElementById('rank')?.value;
    
    if (!level || !rank) return;
    
    const points = POINTS_MATRIX[level][rank];
    const previewEl = document.getElementById('previewPoints');
    const previewContainer = document.getElementById('pointsPreview');
    
    if (previewEl) previewEl.textContent = points;
    if (previewContainer) previewContainer.classList.remove('hidden');
}

function loadAchievementsList() {
    const container = document.getElementById('achievementsContainer');
    if (!container) {
        console.warn('Container achievementsContainer not found');
        return;
    }
    
    console.log('📋 Loading achievements list...');
    console.log('Current achievements array:', achievements);
    console.log('Total achievements:', achievements.length);
    
    container.innerHTML = '';
    
    if (achievements.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">Belum ada prestasi</p>';
        return;
    }
    
    achievements.forEach((ach, idx) => {
        try {
            const points = POINTS_MATRIX[ach.level][ach.rank];
            const typeName = ach.achievement_type_name || 'Unknown';
            
            const div = document.createElement('div');
            div.className = 'achievement-item bg-white rounded-lg p-4 mb-3 border-l-4 border-yellow-500 shadow-sm';
            div.innerHTML = `
                <div class="flex justify-between items-center">
                    <div>
                        <p class="font-bold text-gray-900">${typeName}</p>
                        <p class="text-sm text-gray-600">${ach.level} - ${ach.rank} (${ach.year})</p>
                        ${ach.notes ? `<p class="text-xs text-gray-500 mt-1">${ach.notes}</p>` : ''}
                    </div>
                    <div class="text-right">
                        <p class="text-2xl font-bold text-yellow-600">+${points}</p>
                        <p class="text-xs text-gray-500">poin</p>
                    </div>
                </div>
            `;
            container.appendChild(div);
            console.log(`✅ Achievement ${idx + 1}: ${typeName} (+${points})`);
        } catch (err) {
            console.error(`Error rendering achievement ${idx}:`, err);
        }
    });
    
    console.log(`✅ Total ${achievements.length} achievements displayed`);
}

// ==================== EVENT LISTENERS ====================

// Achievement form submission
const achievementForm = document.getElementById('achievementForm');
if (achievementForm) {
    achievementForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        console.log('=== Achievement Form Submitted ===');
        
        try {
            const formData = new FormData(e.target);
            const achievementTypeId = formData.get('achievement_type');
            const level = formData.get('level');
            const rank = formData.get('rank');
            const year = formData.get('year');
            const notes = formData.get('notes') || '';
            
            console.log('Form data:', { achievementTypeId, level, rank, year, notes });
            
            const res = await fetch(`/students/api/achievement-types/`);
            if (!res.ok) throw new Error('Failed to fetch achievement types');
            
            const types = await res.json();
            const selectedType = types.find(t => t.id == achievementTypeId);
            
            if (!selectedType) {
                throw new Error('Selected achievement type not found');
            }
            
            const achievementData = {
                achievement_type_id: achievementTypeId,
                achievement_type_name: selectedType.name,
                level: level,
                rank: rank,
                year: parseInt(year),
                notes: notes
            };
            
            achievements.push(achievementData);
            
            console.log('✅ Achievement added:', achievementData);
            console.log('📊 Total achievements:', achievements.length);
            
            const points = POINTS_MATRIX[level][rank];
            showToast('success', 'Prestasi Ditambahkan', `${selectedType.name} (+${points} poin)`);
            
            e.target.reset();
            document.getElementById('pointsPreview')?.classList.add('hidden');
            
            loadAchievementsList();
            
        } catch (err) {
            console.error('❌ Error adding achievement:', err);
            showToast('error', 'Error', err.message);
        }
    });
}

// Achievement form change listeners
document.querySelectorAll('#level, #rank').forEach(el => {
    el.addEventListener('change', calculateAchievementPoints);
});

// Submit button
document.getElementById('submitBtn')?.addEventListener('click', async () => {
    const filled = Object.values(rankings).filter(r => r > 0).length;
    
    console.log(`=== submitBtn clicked ===`);
    console.log(`Filled rankings: ${filled}/12`);
    console.log(`Achievements: ${achievements.length}`);
    
    if (filled < 12) {
        showToast('error', 'Belum Lengkap', `Baru ${filled}/12 ranking terisi`);
        return;
    }
    
    try {
        showLoading();
        
        console.log('📤 Submitting data...');
        console.log('Rankings:', rankings);
        console.log('Achievements:', achievements);
        
        const res = await fetch(`/students/${RMIB_DATA.studentId}/rmib/submit/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ 
                levels: rankings, 
                achievements: achievements 
            })
        });
        
        const data = await res.json();
        hideLoading();
        
        console.log('Response:', data);
        
        if (data.success) {
            showToast('success', 'Berhasil!', `Skor: ${data.combined_score} poin`);
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 2000);
        } else {
            showToast('error', 'Gagal', data.message);
        }
    } catch (error) {
        hideLoading();
        console.error('❌ Submit error:', error);
        showToast('error', 'Error', error.message);
    }
});

// Tab switching
function switchTab(tabName) {
    if (tabName === 'ranking') {
        document.getElementById('tab-ranking').style.color = '#667eea';
        document.getElementById('tab-ranking').style.borderBottomColor = '#667eea';
        document.getElementById('tab-achievement').style.color = '#6b7280';
        document.getElementById('tab-achievement').style.borderBottomColor = 'transparent';
        
        document.getElementById('content-ranking').classList.remove('hidden');
        document.getElementById('content-achievement').classList.add('hidden');
    } else if (tabName === 'achievement') {
        document.getElementById('tab-achievement').style.color = '#667eea';
        document.getElementById('tab-achievement').style.borderBottomColor = '#667eea';
        document.getElementById('tab-ranking').style.color = '#6b7280';
        document.getElementById('tab-ranking').style.borderBottomColor = 'transparent';
        
        document.getElementById('content-ranking').classList.add('hidden');
        document.getElementById('content-achievement').classList.remove('hidden');
    }
}

document.getElementById('tab-ranking')?.addEventListener('click', () => switchTab('ranking'));
document.getElementById('tab-achievement')?.addEventListener('click', () => switchTab('achievement'));

// Start test button
document.getElementById('startTestBtn')?.addEventListener('click', startTest);

// Confirmation modal
document.getElementById('confirmYesBtn')?.addEventListener('click', () => {
    document.getElementById('confirmationModal')?.classList.add('hidden');
});

document.getElementById('confirmNoBtn')?.addEventListener('click', () => {
    document.getElementById('confirmationModal')?.classList.add('hidden');
});

// ==================== INIT ====================
console.log('✅ RMIB + Achievement System Ready');
console.log('📊 Student ID:', RMIB_DATA.studentId);
console.log('📋 Categories:', Object.keys(RMIB_DATA.categories).length);
