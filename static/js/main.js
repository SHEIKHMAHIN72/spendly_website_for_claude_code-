// main.js — students will add JavaScript here as features are built

// Demo modal
(function () {
    var trigger = document.getElementById('demoTrigger');
    var modal = document.getElementById('demoModal');
    var closeBtn = document.getElementById('modalClose');
    var iframe = document.getElementById('demoVideo');

    function openModal() {
        iframe.src = 'https://www.youtube.com/embed/placeholder';
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        iframe.src = '';
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (trigger) {
        trigger.addEventListener('click', openModal);
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });
})();
