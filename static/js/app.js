/* ── app.js – FindIt frontend logic ── */

document.addEventListener('DOMContentLoaded', function () {

  /* ============================================================
     NAVBAR TOGGLE (mobile)
     ============================================================ */
  const navToggle = document.getElementById('navToggle');
  const navMenu   = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      navMenu.classList.toggle('open');
      const open = navMenu.classList.contains('open');
      navToggle.setAttribute('aria-expanded', open);
    });
    // Close when clicking outside
    document.addEventListener('click', function (e) {
      if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('open');
      }
    });
  }

  /* ============================================================
     USER DROPDOWN
     ============================================================ */
  const userMenuBtn  = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');

  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      userDropdown.classList.toggle('open');
    });
    document.addEventListener('click', function () {
      userDropdown.classList.remove('open');
    });
  }

  /* ============================================================
     DASHBOARD / ADMIN TABS
     ============================================================ */
  function initTabs(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const tabs = container.querySelectorAll('.dash-tab');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        const target = this.dataset.tab;

        // Deactivate all
        tabs.forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Activate selected
        this.classList.add('active');
        const content = document.getElementById('tab-' + target);
        if (content) content.classList.add('active');
      });
    });
  }

  initTabs('dashboardTabs');
  initTabs('adminTabs');

  /* ============================================================
     AUTO-DISMISS FLASH MESSAGES (after 5 s)
     ============================================================ */
  const flashContainer = document.getElementById('flashContainer');
  if (flashContainer) {
    setTimeout(function () {
      flashContainer.querySelectorAll('.flash').forEach(function (flash) {
        flash.style.transition = 'opacity .5s ease, transform .5s ease';
        flash.style.opacity = '0';
        flash.style.transform = 'translateX(2rem)';
        setTimeout(() => flash.remove(), 500);
      });
    }, 5000);
  }

  /* ============================================================
     NAVBAR SCROLL EFFECT
     ============================================================ */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 20) {
        navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,.10)';
      } else {
        navbar.style.boxShadow = '';
      }
    });
  }

  /* ============================================================
     STAT NUMBER COUNTER ANIMATION
     ============================================================ */
  function animateCounter(el) {
    const target = parseInt(el.dataset.target || el.textContent, 10);
    if (isNaN(target) || target === 0) return;
    const duration = 1200;
    const step     = target / (duration / 16);
    let current    = 0;
    const timer = setInterval(function () {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(current);
    }, 16);
  }

  // Observe stat numbers and animate when in view
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat-number').forEach(el => observer.observe(el));
  }

  /* ============================================================
     SEARCH INPUT – ENTER KEY SUPPORT
     ============================================================ */
  const searchInput = document.querySelector('.search-input');
  if (searchInput) {
    searchInput.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        this.closest('form').submit();
      }
    });
  }

  /* ============================================================
     CONFIRM DELETE BUTTONS (extra safety)
     ============================================================ */
  document.querySelectorAll('[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  /* ============================================================
     IMAGE PREVIEW (create/edit item)
     ============================================================ */
  const imageUrlInput = document.getElementById('image_url');
  if (imageUrlInput) {
    imageUrlInput.addEventListener('blur', function () {
      const url = this.value.trim();
      let preview = document.getElementById('imagePreview');
      if (!preview) {
        preview = document.createElement('div');
        preview.id = 'imagePreview';
        preview.style.cssText = 'margin-top:.75rem;border-radius:10px;overflow:hidden;border:2px dashed #e2e8f0;';
        this.parentElement.appendChild(preview);
      }
      if (url) {
        preview.innerHTML = `<img src="${url}" alt="Preview" style="width:100%;max-height:200px;object-fit:cover;"
                              onerror="this.parentElement.style.display='none'" />`;
        preview.style.display = '';
      } else {
        preview.style.display = 'none';
      }
    });
  }

  /* ============================================================
     TYPE TOGGLE on create/edit page
     ============================================================ */
  document.querySelectorAll('.type-option input[type="radio"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      const allOptions = this.closest('.type-toggle').querySelectorAll('.type-option');
      allOptions.forEach(o => o.classList.remove('active'));
      this.parentElement.classList.add('active');
    });
  });

  /* ============================================================
     BROWSE – FORM SUBMIT ON FILTER CHANGE (already done inline,
     but keep as fallback)
     ============================================================ */
  const filterForm = document.getElementById('filterForm');
  if (filterForm) {
    const selects = filterForm.querySelectorAll('select');
    selects.forEach(function (sel) {
      sel.addEventListener('change', function () {
        filterForm.submit();
      });
    });
  }

  /* ============================================================
     SMOOTH SCROLL for anchor links
     ============================================================ */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  console.log('[FindIt] App initialized ✓');
});
