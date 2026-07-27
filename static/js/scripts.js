/*!
* Start Bootstrap - Personal v1.0.1 (https://startbootstrap.com/template-overviews/personal)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-personal/blob/master/LICENSE)
*/
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;

    // Check for saved dark mode preference
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'enabled') {
        body.classList.add('dark-mode');
    }

    // Update toggle icon based on current state
    function updateToggleIcon() {
        if (!darkModeToggle) return;
        if (body.classList.contains('dark-mode')) {
            darkModeToggle.innerHTML = '<i class="bi bi-sun"></i>';
        } else {
            darkModeToggle.innerHTML = '<i class="bi bi-moon-stars"></i>';
        }
    }

    // Initialize icon
    updateToggleIcon();

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');

            // Save preference
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
            } else {
                localStorage.setItem('darkMode', 'disabled');
            }
            updateToggleIcon();
        });
    }

    // Navbar collapse handling - ensure Bootstrap's collapse works
    // The data-bs-toggle="collapse" should work with Bootstrap JS loaded
    // But we can add a fallback if needed
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', () => {
            navbarCollapse.classList.toggle('show');
        });
    }
});