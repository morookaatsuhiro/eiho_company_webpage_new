/**
 * 株式会社 衛宝 | EIHO - 主脚本
 * 依赖: Bootstrap 5 (需在页面中先引入)
 */

(function () {
  'use strict';

  // ===== Navbar background on scroll =====
  const nav = document.querySelector('.navbar');
  const onScroll = () => {
    if (!nav) return;
    if (window.scrollY > 10) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  };
  window.addEventListener('scroll', onScroll);
  onScroll();

  // ===== Nav active/aria sync + close mobile menu =====
  const navLinks = document.querySelectorAll('.navbar .nav-link, .navbar .btn, .navbar-brand');
  const navAnchorLinks = Array.from(document.querySelectorAll('.navbar .nav-link[href^="#"]'));
  const navCollapse = document.getElementById('navMenu');

  const syncNavAriaCurrent = () => {
    navAnchorLinks.forEach((link) => {
      if (link.classList.contains('active')) {
        link.setAttribute('aria-current', 'page');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  };

  const activateNavLink = (linkEl) => {
    if (!linkEl) return;
    navAnchorLinks.forEach((link) => link.classList.remove('active'));
    linkEl.classList.add('active');
    syncNavAriaCurrent();
  };

  navLinks.forEach((a) => {
    a.addEventListener('click', () => {
      if (a.classList.contains('nav-link')) {
        const href = a.getAttribute('href') || '';
        if (href.startsWith('#')) activateNavLink(a);
      } else if (a.classList.contains('navbar-brand')) {
        const topLink = document.querySelector('.navbar .nav-link[href="#top"]');
        activateNavLink(topLink);
      }

      if (navCollapse && navCollapse.classList.contains('show')) {
        bootstrap.Collapse.getOrCreateInstance(navCollapse).hide();
      }
    });
  });

  const spyRoot = document.querySelector('[data-bs-spy="scroll"]');
  if (spyRoot) {
    spyRoot.addEventListener('activate.bs.scrollspy', syncNavAriaCurrent);
  }
  if (!document.querySelector('.navbar .nav-link.active')) {
    const topLink = document.querySelector('.navbar .nav-link[href="#top"]');
    activateNavLink(topLink);
  } else {
    syncNavAriaCurrent();
  }

  // ===== Footer year =====
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ===== Contact form submit =====
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const msg = document.getElementById('formMsg');
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';
      const setMsg = (text, isError = false) => {
        if (!msg) return;
        msg.textContent = text;
        msg.classList.toggle('text-danger', isError);
        msg.classList.toggle('text-success', !isError);
      };

      if (contactForm.dataset.submitting === '1') return;
      contactForm.dataset.submitting = '1';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '送信中...';
      }
      setMsg('送信中...');

      const formData = new FormData(contactForm);
      const payload = {
        name: String(formData.get('name') || '').trim(),
        company: String(formData.get('company') || '').trim(),
        email: String(formData.get('email') || '').trim(),
        message: String(formData.get('message') || '').trim()
      };

      try {
        const res = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        let data = null;
        try {
          data = await res.json();
        } catch (_) {
          data = null;
        }

        if (!res.ok) {
          const errMsg = (data && (data.detail || data.message)) || '送信に失敗しました。しばらくしてから再度お試しください。';
          setMsg(errMsg, true);
          return;
        }

        const okMsg = (data && data.message) || '送信しました。担当より折り返しご連絡します。';
        setMsg(okMsg, false);
        e.target.reset();
        setTimeout(() => { if (msg) msg.textContent = ''; }, 4500);
      } catch (_) {
        setMsg('送信に失敗しました。通信状況をご確認ください。', true);
      } finally {
        delete contactForm.dataset.submitting;
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnHtml;
        }
      }
    });
  }

  // ===== ScrollSpy: refresh when page loads with hash =====
  if (window.location.hash) {
    const scrollSpyEl = document.querySelector('[data-bs-spy="scroll"]');
    if (scrollSpyEl && typeof bootstrap !== 'undefined' && bootstrap.ScrollSpy) {
      requestAnimationFrame(() => {
        const instance = bootstrap.ScrollSpy.getInstance(scrollSpyEl);
        if (instance) instance.refresh();
      });
    }
  }

  // ===== CountUp (simple) =====
  const counters = document.querySelectorAll('.countup');
  const animateCount = (el) => {
    const to = parseInt(el.dataset.to, 10) || 0;
    const duration = 900;
    const start = performance.now();
    const from = 0;

    const step = (t) => {
      const p = Math.min((t - start) / duration, 1);
      const val = Math.floor(from + (to - from) * (0.2 + 0.8 * p) * p);
      el.textContent = val;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = to;
    };
    requestAnimationFrame(step);
  };

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCount(entry.target);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.6 });

  counters.forEach(c => io.observe(c));
})();
