// staff_dashboard.js - Elite School 2025

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
}

// Auto highlight current page in sidebar
document.addEventListener("DOMContentLoaded", function () {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath || 
            (currentPath === '/staff/' && link.getAttribute('href') === '/staff/')) {
            link.classList.add('active');
        }
    });
});