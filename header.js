// ✨ ENHANCED JAVASCRIPT FUNCTIONALITY
function initializeApp() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('hidden');
    }

    // Initialize all components with delay for smooth loading
    setTimeout(() => {
        initializeNavigation();
        initializeCharts();
        initializeKeyboardShortcuts();
        startCounterAnimations();
        updateCurrentDate();
        initializeRealTimeUpdates();
        initializeInteractiveElements();
        initializeLiveUpdates();

        hideLoadingOverlay();
        showToast('Sistem Siap', 'Dashboard berhasil dimuat dan siap digunakan', 'success');
        playWelcomeAnimation();
    }, 1000);
}

// ✨ Interactive Elements
function initializeInteractiveElements() {
    // Add ripple effect to cards
    document.querySelectorAll('.metric-card').forEach(card => {
        card.addEventListener('click', function (e) {
            createRipple(e, this);
        });
    });

    // Initialize tooltips
    initializeTooltips();

    // Initialize auto-refresh toggle
    initializeAutoRefresh();
}

function createRipple(event, element) {
    const ripple = document.createElement('div');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
                z-index: 1;
            `;

    // Add ripple animation CSS if not exists
    if (!document.querySelector('#ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
                    @keyframes ripple {
                        to {
                            transform: scale(2);
                            opacity: 0;
                        }
                    }
                `;
        document.head.appendChild(style);
    }

    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// ✨ Live Data Updates
function initializeLiveUpdates() {
    setInterval(() => {
        updateMetrics();
        updateCharts();
        animateProgressBars();
    }, 5000); // Update every 5 seconds
}

function updateMetrics() {
    // Simulate dynamic data updates
    const completionRate = document.getElementById('completionRate');
    const targetRate = document.getElementById('targetRate');
    const scoreCategory = document.getElementById('scoreCategory');
    const scorePercentage = document.getElementById('scorePercentage');

    if (completionRate) {
        const newRate = Math.min(95, parseInt(completionRate.textContent) + Math.floor(Math.random() * 2));
        completionRate.textContent = newRate;
        targetRate.textContent = newRate + '%';

        // Update progress bar
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = newRate + '%';
        }
    }

    // Update score category
    if (scoreCategory && scorePercentage) {
        const score = parseInt(scorePercentage.textContent);
        if (score >= 85) scoreCategory.textContent = 'Sangat Baik';
        else if (score >= 75) scoreCategory.textContent = 'Baik';
        else if (score >= 65) scoreCategory.textContent = 'Cukup';
        else scoreCategory.textContent = 'Perlu Perbaikan';
    }
}

function updateCharts() {
    // Add visual indicator for chart updates
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        container.classList.add('chart-updating');
        setTimeout(() => {
            container.classList.remove('chart-updating');
        }, 1000);
    });
}

function animateProgressBars() {
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });
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

// ✨ Card Click Handlers
function showStudentDetails() {
    showModal('studentModal');
    playCountUpAnimation();
}

function showCompletedTests() {
    showToast('Info', 'Menampilkan detail tes yang telah selesai...', 'info');
    // Navigate to daftar siswa page
    setTimeout(() => {
        navigateToPage('2daftar.html');
    }, 1000);
}

function showPendingTests() {
    showToast('Peringatan', 'Ada 14 siswa yang belum menyelesaikan tes!', 'warning');
    // Navigate to input page for pending tests
    setTimeout(() => {
        navigateToPage('4input.html');
        createConfetti();
    }, 500);
}

function showScoreAnalysis() {
    showToast('Analisis', 'Menampilkan detail analisis skor...', 'info');
    // Navigate to laporan page
    setTimeout(() => {
        navigateToPage('5laporan.html');
    }, 1000);
    // Animate score visualization
    animateScoreProgress();
}

// ✨ Navigation Functions - Navigate to actual HTML files
function navigateToPage(htmlFile) {
    showLoadingOverlay();
    showToast('Navigasi', 'Memuat halaman...', 'info', 1000);

    setTimeout(() => {
        window.location.href = htmlFile;
    }, 1200);
}

// ✨ Update Navigation System for HTML files
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
                'reports': '5laporan.html',
                'certificates': '6certif.html'
            };

            const htmlFile = pageMapping[targetPage];
            if (htmlFile) {
                if (htmlFile === '1dashboard.html') {
                    // Stay on current page but update active nav
                    updateActiveNav(this);
                } else {
                    navigateToPage(htmlFile);
                }
            }
        });
    });
}

// ✨ Update sidebar navigation links to match HTML files
function updateSidebarNavigation() {
    const sidebarNav = document.querySelector('nav.space-y-2');
    if (sidebarNav) {
        sidebarNav.innerHTML = `
                    <a href="1dashboard.html" class="nav-link group flex items-center space-x-3 text-blue-600 bg-blue-50 p-3 rounded-xl font-medium border-l-4 border-blue-600 transition-all" data-page="dashboard">
                        <div class="w-6 h-6 bg-blue-600 rounded-lg flex items-center justify-center">
                            <i class="fas fa-tachometer-alt text-white text-sm"></i>
                        </div>
                        <span>Dashboard</span>
                        <div class="ml-auto flex items-center space-x-2">
                            <span class="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">156</span>
                            <i class="fas fa-chevron-right text-xs group-hover:translate-x-1 transition-transform"></i>
                        </div>
                    </a>
                    
                    <a href="2daftar.html" class="nav-link group flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 p-3 rounded-xl transition-all" data-page="students">
                        <div class="w-6 h-6 bg-gray-400 group-hover:bg-blue-600 rounded-lg flex items-center justify-center transition-colors">
                            <i class="fas fa-users text-white text-sm"></i>
                        </div>
                        <span>Daftar Siswa</span>
                        <i class="fas fa-chevron-right text-xs ml-auto opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all"></i>
                    </a>
                    
                    <a href="3tambah.html" class="nav-link group flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 p-3 rounded-xl transition-all" data-page="add-student">
                        <div class="w-6 h-6 bg-gray-400 group-hover:bg-green-600 rounded-lg flex items-center justify-center transition-colors">
                            <i class="fas fa-user-plus text-white text-sm"></i>
                        </div>
                        <span>Tambah Siswa</span>
                        <i class="fas fa-chevron-right text-xs ml-auto opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all"></i>
                    </a>
                    
                    <a href="4input.html" class="nav-link group flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 p-3 rounded-xl transition-all" data-page="rmib-input">
                        <div class="w-6 h-6 bg-gray-400 group-hover:bg-purple-600 rounded-lg flex items-center justify-center transition-colors">
                            <i class="fas fa-edit text-white text-sm"></i>
                        </div>
                        <span>Input Skor RMIB</span>
                        <i class="fas fa-chevron-right text-xs ml-auto opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all"></i>
                    </a>
                    
                    <a href="5laporan.html" class="nav-link group flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 p-3 rounded-xl transition-all" data-page="reports">
                        <div class="w-6 h-6 bg-gray-400 group-hover:bg-indigo-600 rounded-lg flex items-center justify-center transition-colors">
                            <i class="fas fa-chart-bar text-white text-sm"></i>
                        </div>
                        <span>Laporan & Analisis</span>
                        <i class="fas fa-chevron-right text-xs ml-auto opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all"></i>
                    </a>
                    
                    <a href="6certif.html" class="nav-link group flex items-center space-x-3 text-gray-700 hover:text-blue-600 hover:bg-blue-50 p-3 rounded-xl transition-all" data-page="certificates">
                        <div class="w-6 h-6 bg-gray-400 group-hover:bg-yellow-600 rounded-lg flex items-center justify-center transition-colors">
                            <i class="fas fa-certificate text-white text-sm"></i>
                        </div>
                        <span>Sertifikat</span>
                        <i class="fas fa-chevron-right text-xs ml-auto opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all"></i>
                    </a>
                `;
    }
}

// ✨ Animation Functions
function playWelcomeAnimation() {
    // Create welcome confetti
    for (let i = 0; i < 20; i++) {
        setTimeout(() => createConfetti(), i * 100);
    }
}

function createConfetti() {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';
    confetti.style.left = Math.random() * window.innerWidth + 'px';
    confetti.style.backgroundColor = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444'][Math.floor(Math.random() * 5)];
    document.body.appendChild(confetti);

    setTimeout(() => confetti.remove(), 3000);
}

function animateScoreProgress() {
    const progressCircle = document.getElementById('scoreProgress');
    if (progressCircle) {
        progressCircle.style.strokeDashoffset = '125.6';
        setTimeout(() => {
            progressCircle.style.strokeDashoffset = '31.4';
        }, 100);
    }
}

function playCountUpAnimation() {
    // Animate numbers in modal
    const numberElements = document.querySelectorAll('#studentModal .text-2xl');
    numberElements.forEach((element, index) => {
        const target = parseInt(element.textContent);
        let current = 0;
        const increment = target / 50;

        const animation = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target;
                clearInterval(animation);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 20);
    });
}

// ✨ Quick Action Triggers - Updated to navigate to HTML files
function triggerAddStudent() {
    hideQuickActions();
    showToast('Navigasi', 'Membuka halaman tambah siswa...', 'info');
    setTimeout(() => navigateToPage('3tambah.html'), 1000);
}

function triggerRMIBInput() {
    hideQuickActions();
    showToast('Navigasi', 'Membuka halaman input RMIB...', 'info');
    setTimeout(() => navigateToPage('4input.html'), 1000);
}

function triggerExport() {
    hideQuickActions();
    exportAllData();
}

function triggerReports() {
    hideQuickActions();
    showToast('Navigasi', 'Membuka halaman laporan...', 'info');
    setTimeout(() => navigateToPage('5laporan.html'), 1000);
}

function triggerCertificates() {
    hideQuickActions();
    showToast('Navigasi', 'Membuka halaman sertifikat...', 'info');
    setTimeout(() => navigateToPage('6certif.html'), 1000);
}

// ✨ Update Quick Actions buttons in dashboard
function updateQuickActionButtons() {
    const quickActionsGrid = document.querySelector('.grid.grid-cols-1.sm\\:grid-cols-2.lg\\:grid-cols-4.gap-4');
    if (quickActionsGrid) {
        quickActionsGrid.innerHTML = `
                    <button onclick="navigateToPage('3tambah.html')" class="group flex flex-col items-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 rounded-2xl transition-all transform hover:scale-105 border-2 border-blue-200 hover:border-blue-300">
                        <div class="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <i class="fas fa-user-plus text-white text-xl"></i>
                        </div>
                        <span class="font-semibold text-blue-700 text-sm">Tambah Siswa</span>
                        <span class="text-xs text-blue-600 mt-1">Daftar siswa baru</span>
                    </button>

                    <button onclick="navigateToPage('4input.html')" class="group flex flex-col items-center p-6 bg-gradient-to-br from-green-50 to-green-100 hover:from-green-100 hover:to-green-200 rounded-2xl transition-all transform hover:scale-105 border-2 border-green-200 hover:border-green-300">
                        <div class="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <i class="fas fa-edit text-white text-xl"></i>
                        </div>
                        <span class="font-semibold text-green-700 text-sm">Input Skor RMIB</span>
                        <span class="text-xs text-green-600 mt-1">Entry hasil tes</span>
                    </button>

                    <button onclick="navigateToPage('5laporan.html')" class="group flex flex-col items-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-200 rounded-2xl transition-all transform hover:scale-105 border-2 border-purple-200 hover:border-purple-300">
                        <div class="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <i class="fas fa-chart-line text-white text-xl"></i>
                        </div>
                        <span class="font-semibold text-purple-700 text-sm">Lihat Laporan</span>
                        <span class="text-xs text-purple-600 mt-1">Analisis & statistik</span>
                    </button>

                    <button onclick="navigateToPage('6certif.html')" class="group flex flex-col items-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 hover:from-orange-100 hover:to-orange-200 rounded-2xl transition-all transform hover:scale-105 border-2 border-orange-200 hover:border-orange-300">
                        <div class="w-12 h-12 bg-orange-600 rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <i class="fas fa-certificate text-white text-xl"></i>
                        </div>
                        <span class="font-semibold text-orange-700 text-sm">Sertifikat</span>
                        <span class="text-xs text-orange-600 mt-1">Generate sertifikat</span>
                    </button>
                `;
    }
}

// ✨ Auto-refresh Toggle
function initializeAutoRefresh() {
    let autoRefreshEnabled = true;
    const toggleButton = document.createElement('button');
    toggleButton.innerHTML = '<i class="fas fa-sync-alt mr-1"></i> Auto-refresh: ON';
    toggleButton.className = 'text-xs bg-green-100 text-green-600 px-2 py-1 rounded-lg hover:bg-green-200 transition-colors';

    toggleButton.addEventListener('click', () => {
        autoRefreshEnabled = !autoRefreshEnabled;
        toggleButton.innerHTML = `<i class="fas fa-sync-alt mr-1"></i> Auto-refresh: ${autoRefreshEnabled ? 'ON' : 'OFF'}`;
        toggleButton.className = autoRefreshEnabled
            ? 'text-xs bg-green-100 text-green-600 px-2 py-1 rounded-lg hover:bg-green-200 transition-colors'
            : 'text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-lg hover:bg-gray-200 transition-colors';

        showToast('Setting', `Auto-refresh ${autoRefreshEnabled ? 'diaktifkan' : 'dinonaktifkan'}`, 'info');
    });

    // Add to navigation if exists
    const statusElement = document.querySelector('.flex.items-center.space-x-4.text-sm');
    if (statusElement) {
        statusElement.appendChild(toggleButton);
    }
}

// ✨ Tooltips
function initializeTooltips() {
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const tooltip = document.createElement('div');
    tooltip.className = 'fixed bg-black text-white text-xs px-2 py-1 rounded z-50 pointer-events-none';
    tooltip.textContent = event.target.getAttribute('title');
    tooltip.style.left = event.pageX + 10 + 'px';
    tooltip.style.top = event.pageY - 30 + 'px';
    tooltip.id = 'tooltip';
    document.body.appendChild(tooltip);

    event.target.removeAttribute('title');
    event.target.setAttribute('data-original-title', tooltip.textContent);
}

function hideTooltip(event) {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.remove();
    }

    const originalTitle = event.target.getAttribute('data-original-title');
    if (originalTitle) {
        event.target.setAttribute('title', originalTitle);
        event.target.removeAttribute('data-original-title');
    }
}

function updateActiveNav(activeLink) {
    // Remove active state from all links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('text-blue-600', 'bg-blue-50', 'font-medium', 'border-l-4', 'border-blue-600');
        link.classList.add('text-gray-700');

        // Reset icon colors
        const iconDiv = link.querySelector('div');
        if (iconDiv) {
            iconDiv.classList.remove('bg-blue-600');
            iconDiv.classList.add('bg-gray-400');
        }
    });

    // Add active state to clicked link
    activeLink.classList.add('text-blue-600', 'bg-blue-50', 'font-medium', 'border-l-4', 'border-blue-600');
    activeLink.classList.remove('text-gray-700');

    // Update icon color
    const activeIconDiv = activeLink.querySelector('div');
    if (activeIconDiv) {
        activeIconDiv.classList.remove('bg-gray-400');
        activeIconDiv.classList.add('bg-blue-600');
    }
}

// ✨ Mobile Menu Functions
function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');

    sidebar.classList.toggle('open');
    overlay.classList.toggle('hidden');
}

function closeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');

    sidebar.classList.remove('open');
    overlay.classList.add('hidden');
}

// ✨ Enhanced Charts Initialization
function initializeCharts() {
    initializeInterestChart();
    initializeClassPerformanceChart();
}

function initializeInterestChart() {
    const ctx = document.getElementById('interestChart');
    if (!ctx) return;

    const gradient1 = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient1.addColorStop(0, '#667eea');
    gradient1.addColorStop(1, '#764ba2');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                'Scientific', 'Medical', 'Social Service',
                'Computational', 'Aesthetic', 'Literary',
                'Mechanical', 'Lainnya'
            ],
            datasets: [{
                data: [28, 22, 18, 15, 8, 5, 3, 1],
                backgroundColor: [
                    '#3B82F6', '#10B981', '#8B5CF6',
                    '#F59E0B', '#EF4444', '#6366F1',
                    '#EC4899', '#6B7280'
                ],
                borderWidth: 3,
                borderColor: '#fff',
                hoverBorderWidth: 5,
                hoverBorderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            family: 'Inter, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    cornerRadius: 12,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            return context.label + ': ' + context.parsed + '% (' +
                                Math.round(context.parsed * 156 / 100) + ' siswa)';
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1500
            }
        }
    });
}

function initializeClassPerformanceChart() {
    const ctx = document.getElementById('classPerformanceChart');
    if (!ctx) return;

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.1)');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Kelas 7A', 'Kelas 7B', 'Kelas 8A', 'Kelas 8B', 'Kelas 9A', 'Kelas 9B'],
            datasets: [{
                label: 'Rata-rata Skor',
                data: [75, 82, 78, 86, 81, 79],
                backgroundColor: gradient,
                borderColor: '#3B82F6',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    cornerRadius: 8,
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ✨ Counter Animations
function startCounterAnimations() {
    const counters = document.querySelectorAll('.counter');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });

    counters.forEach(counter => {
        observer.observe(counter);
    });
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;

    const updateCounter = () => {
        if (current < target) {
            current += step;
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };

    updateCounter();
}

// ✨ Real-time Updates Simulation
function initializeRealTimeUpdates() {
    setInterval(() => {
        // Simulate real-time data updates
        updateActivityFeed();
        updateSystemStatus();
    }, 30000); // Update every 30 seconds
}

function updateActivityFeed() {
    // Simulate new activity
    const activities = [
        'Siswa baru bergabung',
        'Tes RMIB selesai',
        'Laporan diunduh',
        'Data tersinkron'
    ];

    // Randomly show toast for new activity
    if (Math.random() < 0.3) {
        const randomActivity = activities[Math.floor(Math.random() * activities.length)];
        showToast('Aktivitas Baru', randomActivity, 'info', 3000);
    }
}

function updateSystemStatus() {
    // Update timestamp displays
    const statusElements = document.querySelectorAll('[data-timestamp]');
    statusElements.forEach(element => {
        element.textContent = 'Baru saja';
    });
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

// ✨ Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {
        if (e.altKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    navigateToPage('1dashboard.html');
                    break;
                case '2':
                    e.preventDefault();
                    navigateToPage('2daftar.html');
                    break;
                case '3':
                    e.preventDefault();
                    navigateToPage('3tambah.html');
                    break;
                case '4':
                    e.preventDefault();
                    navigateToPage('4input.html');
                    break;
                case '5':
                    e.preventDefault();
                    navigateToPage('5laporan.html');
                    break;
                case '6':
                    e.preventDefault();
                    navigateToPage('6certif.html');
                    break;
            }
        }
    });
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

function showLoadingOverlay() {
    document.getElementById('loadingOverlay')?.classList.remove('hidden');
}

function hideLoadingOverlay() {
    document.getElementById('loadingOverlay')?.classList.add('hidden');
}

// ✨ Export Functions
function exportAllData() {
    showLoadingOverlay();
    showToast('Export Dimulai', 'Sedang memproses data untuk export...', 'info');

    setTimeout(() => {
        hideLoadingOverlay();
        showToast('Export Berhasil', 'File Excel berhasil diunduh ke perangkat Anda', 'success');
    }, 2000);
}

// ✨ Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
        initializeApp();
        updateSidebarNavigation();
        updateQuickActionButtons();
    });
} else {
    initializeApp();
    updateSidebarNavigation();
    updateQuickActionButtons();
}