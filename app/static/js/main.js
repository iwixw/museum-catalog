/**
 * Museum Catalog — Main JavaScript
 */

'use strict';

// ============================================================
// Toggle password visibility
// ============================================================
function togglePasswordVisibility(fieldId, btn) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    if (field.type === 'password') {
        field.type = 'text';
        btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
        btn.title = 'Скрыть пароль';
    } else {
        field.type = 'password';
        btn.innerHTML = '<i class="bi bi-eye"></i>';
        btn.title = 'Показать пароль';
    }
}

// ============================================================
// Auto-dismiss alerts after 5 seconds
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});

// ============================================================
// Confirm delete actions (fallback for browsers without confirm dialog)
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    const deleteForms = document.querySelectorAll('form[data-confirm]');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const msg = form.dataset.confirm || 'Вы уверены?';
            if (!window.confirm(msg)) {
                e.preventDefault();
            }
        });
    });
});

// ============================================================
// Active nav link highlight based on current URL
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// ============================================================
// Smooth scroll to top button (if added later)
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    // Add scroll-to-top button dynamically if page is long
    const scrollBtn = document.createElement('button');
    scrollBtn.id = 'scrollTopBtn';
    scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollBtn.className = 'btn btn-primary rounded-circle shadow';
    scrollBtn.style.cssText = [
        'position: fixed',
        'bottom: 1.5rem',
        'right: 1.5rem',
        'width: 44px',
        'height: 44px',
        'display: none',
        'z-index: 1000',
        'padding: 0',
        'line-height: 1',
        'font-size: 1.1rem'
    ].join(';');
    document.body.appendChild(scrollBtn);

    window.addEventListener('scroll', function () {
        scrollBtn.style.display = window.scrollY > 300 ? 'flex' : 'none';
        scrollBtn.style.alignItems = 'center';
        scrollBtn.style.justifyContent = 'center';
    });

    scrollBtn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
