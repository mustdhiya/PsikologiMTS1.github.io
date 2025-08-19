// ✨ BASIC JAVASCRIPT FUNCTIONALITY FOR HEADER
function initializeApp() {
    initializeNavigation();
    initializeMobileMenu();
    updateCurrentDate();
}

// ✨ Navigation Functions - Navigate to actual HTML files
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetPage = this.getAttribute('data-page');

            // Map pages to actual HTML files
            const pageMapping = {
                'dashboard': '1dashboard.html',
                'students': '2daftar.html',
                'add-student': '3tambah.html',
                'rmib-input': '4input.html',
                'reports': '5laporan.html'
            };

            const htmlFile = pageMapping[targetPage];
            if (htmlFile) {
                window.location.href = htmlFile;
            }
        });
    });
}

// ✨ Mobile Menu Functions
function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');

    sidebar.classList.toggle('open');
    overlay.classList.toggle('hidden');
}

function initializeMobileMenu() {
    // Close mobile menu when clicking outside
    document.getElementById('mobileOverlay')?.addEventListener('click', toggleMobileMenu);
}

// ✨ Modal Functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
}

// ✨ Quick Actions
function showQuickActions() {
    showModal('quickActionsModal');
}

function hideQuickActions() {
    hideModal('quickActionsModal');
}

// ✨ Quick Action Triggers - Navigate to HTML files
function triggerAddStudent() {
    hideQuickActions();
    window.location.href = '3tambah.html';
}

function triggerRMIBInput() {
    hideQuickActions();
    window.location.href = '4input.html';
}

function triggerReports() {
    hideQuickActions();
    window.location.href = '5laporan.html';
}

function triggerExport() {
    hideQuickActions();
    // Basic export simulation
    alert('Fitur export akan segera tersedia');
}

// ✨ Enhanced Toast Notifications
function showToast(title, message, type = 'success', duration = 3000) {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Update toast styling based on type
    const iconClasses = {
        success: 'fas fa-check-circle text-green-500',
        error: 'fas fa-exclamation-circle text-red-500',
        warning: 'fas fa-exclamation-triangle text-yellow-500',
        info: 'fas fa-info-circle text-blue-500'
    };

    const borderClasses = {
        success: 'border-green-500',
        error: 'border-red-500',
        warning: 'border-yellow-500',
        info: 'border-blue-500'
    };

    toastIcon.className = iconClasses[type] || iconClasses.success;
    toast.className = `toast bg-white rounded-xl shadow-2xl border-l-4 p-4 max-w-sm ${borderClasses[type] || borderClasses.success}`;

    toast.classList.remove('hidden');
    toast.classList.add('show');

    setTimeout(() => {
        hideToast();
    }, duration);
}

function hideToast() {
    const toast = document.getElementById('toast');
    toast.classList.remove('show');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 300);
}

// ✨ Utility Functions
function updateCurrentDate() {
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: 'Asia/Jakarta'
        };
        dateElement.textContent = now.toLocaleDateString('id-ID', options);
    }
}

// ✨ Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}