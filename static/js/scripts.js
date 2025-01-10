/*!
* Start Bootstrap - Personal v1.0.1 (https://startbootstrap.com/template-overviews/personal)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-personal/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project
    document.addEventListener('DOMContentLoaded', () => {
        const darkModeToggle = document.getElementById('darkModeToggle');
        const body = document.body;

        // Check for saved dark mode preference
        const darkMode = localStorage.getItem('darkMode');
        if (darkMode === 'enabled') {
            body.classList.add('dark-mode');
        }

        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');

            // Save preference
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
                darkModeToggle.innerHTML = '<i class="bi bi-sun"></i>';
            } else {
                localStorage.setItem('darkMode', null);
                darkModeToggle.innerHTML = '<i class="bi bi-moon-stars"></i>';
            }
        });
    });