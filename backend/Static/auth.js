document.addEventListener('DOMContentLoaded', () => {
    // Password Toggle
    const toggleButtons = document.querySelectorAll('.password-toggle');

    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const input = button.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
            } else {
                input.type = 'password';
                button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
            }
        });
    });

    // Password Strength
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');

    if (passwordInput && strengthBar) {
        passwordInput.addEventListener('input', () => {
            const val = passwordInput.value;
            let robustness = 0;

            if (val.length >= 8) robustness += 1;
            if (val.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) robustness += 1;
            if (val.match(/([0-9])/)) robustness += 1;
            if (val.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) robustness += 1;

            let color = '';
            let text = '';
            let width = '0%';

            switch (robustness) {
                case 1:
                    width = '25%';
                    color = '#ef4444'; // Red
                    text = 'Weak';
                    break;
                case 2:
                    width = '50%';
                    color = '#f59e0b'; // Amber
                    text = 'Fair';
                    break;
                case 3:
                    width = '75%';
                    color = '#3b82f6'; // Blue
                    text = 'Good';
                    break;
                case 4:
                    width = '100%';
                    color = '#22c55e'; // Green
                    text = 'Strong';
                    break;
                default:
                    width = '0%';
                    text = '';
            }

            if (val.length > 0 && val.length < 8) {
                text = 'Too short';
                width = '10%';
                color = '#ef4444';
            }

            strengthBar.style.width = width;
            strengthBar.style.backgroundColor = color;
            if (strengthText) strengthText.textContent = text;
        });
    }

    // Loading State & Validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            // Validation: Confirm Password
            const password = form.querySelector('input[name="password"]');
            const confirm = form.querySelector('input[name="confirm_password"]');

            if (password && confirm) {
                if (password.value !== confirm.value) {
                    e.preventDefault();
                    alert("Passwords do not match!");
                    // Highlight error
                    confirm.style.borderColor = '#ef4444';
                    return;
                }
            }

            // Loading State
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                const originalText = btn.textContent;
                btn.disabled = true;
                btn.textContent = 'Please wait...';
                // Small delay to show state if response is super fast
                // or preventing double submission
            }
        });
    });

    // Sidebar Toggle Logic
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const closeBtn = document.querySelector('.close-sidebar');

    function toggleSidebar(show) {
        if (show) {
            sidebar.classList.add('active');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        } else {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    if (hamburger) {
        hamburger.addEventListener('click', () => toggleSidebar(true));
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => toggleSidebar(false));
    }

    if (overlay) {
        overlay.addEventListener('click', () => toggleSidebar(false));
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('active')) {
            toggleSidebar(false);
        }
    });
});
