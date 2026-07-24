// LifeTrack Main UI Script

document.addEventListener('DOMContentLoaded', function() {
    // 1. Toast Notification Helper
    window.LifeTrackToast = {
        show: function(message, type = 'success') {
            const toastContainer = document.getElementById('toast-container');
            if (!toastContainer) return;

            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'warning'} border-0 show`;
            toast.role = 'alert';
            toast.ariaLive = 'assertive';
            toast.ariaAtomic = 'true';
            toast.style.marginBottom = '10px';
            toast.style.backdropFilter = 'blur(10px)';
            toast.style.background = type === 'success' ? 'rgba(16, 185, 129, 0.9)' : type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(245, 158, 11, 0.9)';

            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body fw-medium">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;

            toastContainer.appendChild(toast);

            // Auto remove after 4s
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            }, 4000);
        }
    };
});
