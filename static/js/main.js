/* =========================================================================
   Portfolio interactions.
   Vanilla JS, no dependencies. Every feature degrades gracefully: with
   JavaScript disabled the page is still fully readable and the contact form
   still submits as a normal POST.
   ========================================================================= */

(function () {
  'use strict';

  var root = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(selector, scope) { return (scope || document).querySelector(selector); }
  function $$(selector, scope) {
    return Array.prototype.slice.call((scope || document).querySelectorAll(selector));
  }

  /* ---------------------------------------------------------------------
     Current year
     --------------------------------------------------------------------- */

  var yearEl = $('#year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ---------------------------------------------------------------------
     Theme toggle
     --------------------------------------------------------------------- */

  var themeToggle = $('#themeToggle');

  function syncThemeButton(theme) {
    if (!themeToggle) return;
    var next = theme === 'dark' ? 'light' : 'dark';
    themeToggle.setAttribute('aria-label', 'Switch to ' + next + ' theme');
    themeToggle.setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
  }

  syncThemeButton(root.getAttribute('data-theme') || 'dark');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var current = root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      var next = current === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      syncThemeButton(next);
      try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
      playVisibleVideo();
    });
  }

  /* ---------------------------------------------------------------------
     Background video — only load and play the one matching the theme
     --------------------------------------------------------------------- */

  var videos = $$('.bg-video');

  function playVisibleVideo() {
    if (reduceMotion) {
      videos.forEach(function (video) { video.pause(); });
      return;
    }
    var theme = root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    videos.forEach(function (video) {
      if (video.getAttribute('data-theme-video') !== theme) {
        video.pause();
        return;
      }
      // Attach the source the first time this theme is actually shown, so the
      // other clip is never downloaded.
      if (!video.getAttribute('src')) {
        video.setAttribute('src', video.getAttribute('data-src') || '');
        video.load();
      }
      var attempt = video.play();
      if (attempt && attempt.catch) attempt.catch(function () { /* autoplay blocked */ });
    });
  }

  // Defer video work until the page is otherwise idle so it never competes
  // with first paint.
  if (videos.length) {
    var start = function () { playVisibleVideo(); };
    if ('requestIdleCallback' in window) {
      requestIdleCallback(start, { timeout: 2500 });
    } else {
      window.addEventListener('load', function () { setTimeout(start, 400); });
    }
    // Stop decoding frames while the tab is hidden.
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        videos.forEach(function (video) { video.pause(); });
      } else {
        playVisibleVideo();
      }
    });
  }

  /* ---------------------------------------------------------------------
     Sticky header + mobile navigation
     --------------------------------------------------------------------- */

  var header = $('#siteHeader');
  var navToggle = $('#navToggle');
  var mobileNav = $('#mobileNav');

  function closeMobileNav() {
    if (!navToggle || !mobileNav) return;
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open menu');
    mobileNav.hidden = true;
  }

  if (navToggle && mobileNav) {
    navToggle.addEventListener('click', function () {
      var open = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', open ? 'false' : 'true');
      navToggle.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
      mobileNav.hidden = open;
    });

    $$('a', mobileNav).forEach(function (link) {
      link.addEventListener('click', closeMobileNav);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeMobileNav();
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 960) closeMobileNav();
    });
  }

  var toTop = $('#toTop');

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('is-stuck', y > 12);
    if (toTop) toTop.hidden = y < 600;
  }

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      onScroll();
      ticking = false;
    });
  }, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------------------------------------------------------------------
     Reveal on scroll
     --------------------------------------------------------------------- */

  var revealables = $$('.reveal');

  if (!('IntersectionObserver' in window) || reduceMotion) {
    revealables.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    revealables.forEach(function (el) { revealObserver.observe(el); });
  }

  /* ---------------------------------------------------------------------
     Scroll spy
     --------------------------------------------------------------------- */

  var navLinks = $$('[data-nav]');
  var sections = navLinks
    .map(function (link) { return document.getElementById(link.getAttribute('data-nav')); })
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (link) {
          link.classList.toggle('is-active', link.getAttribute('data-nav') === entry.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });

    sections.forEach(function (section) { spy.observe(section); });
  }

  /* ---------------------------------------------------------------------
     Hero role rotator
     --------------------------------------------------------------------- */

  var roleEl = $('#roleText');
  var roles = [];
  try {
    roles = JSON.parse(roleEl ? roleEl.getAttribute('data-roles') || '[]' : '[]');
  } catch (e) { roles = []; }

  if (roleEl && roles.length > 1 && !reduceMotion) {
    var roleIndex = 0;
    var charIndex = roles[0].length;
    var deleting = false;

    var tick = function () {
      var word = roles[roleIndex];
      charIndex += deleting ? -1 : 1;
      roleEl.textContent = word.slice(0, charIndex);

      var delay = deleting ? 45 : 85;
      if (!deleting && charIndex === word.length) {
        delay = 1900;
        deleting = true;
      } else if (deleting && charIndex === 0) {
        deleting = false;
        roleIndex = (roleIndex + 1) % roles.length;
        delay = 320;
      }
      window.setTimeout(tick, delay);
    };

    window.setTimeout(tick, 2200);
  }

  /* ---------------------------------------------------------------------
     Copy-to-clipboard
     --------------------------------------------------------------------- */

  $$('.copy-btn').forEach(function (button) {
    button.addEventListener('click', function () {
      var value = button.getAttribute('data-copy') || '';
      var done = function () {
        button.classList.add('is-copied');
        window.setTimeout(function () { button.classList.remove('is-copied'); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(done).catch(function () { /* denied */ });
      } else {
        var field = document.createElement('textarea');
        field.value = value;
        field.setAttribute('readonly', '');
        field.style.position = 'absolute';
        field.style.left = '-9999px';
        document.body.appendChild(field);
        field.select();
        try { document.execCommand('copy'); done(); } catch (e) { /* no-op */ }
        document.body.removeChild(field);
      }
    });
  });

  /* ---------------------------------------------------------------------
     Contact form
     --------------------------------------------------------------------- */

  var form = $('#contactForm');

  if (form) {
    var submitBtn = $('#contactSubmit');
    var status = $('#formStatus');

    var setStatus = function (message, kind) {
      if (!status) return;
      status.textContent = message;
      status.className = 'form-status' + (kind ? ' is-' + kind : '');
    };

    $$('input, textarea', form).forEach(function (field) {
      field.addEventListener('input', function () {
        var wrapper = field.closest('.field');
        if (wrapper) wrapper.classList.remove('has-error');
      });
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();

      var data = {
        name: (form.elements.name.value || '').trim(),
        email: (form.elements.email.value || '').trim(),
        message: (form.elements.message.value || '').trim(),
        website: (form.elements.website.value || '')
      };

      // Mirror the server's rules so people get feedback without a round trip.
      var problems = [];
      if (!/^[A-Za-z][A-Za-z .'\-]{2,}$/.test(data.name)) {
        problems.push(['name', 'Please enter your name using letters only (at least 3 characters).']);
      }
      if (!/^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/.test(data.email)) {
        problems.push(['email', 'Please enter a valid email address.']);
      }
      if (data.message.length < 10) {
        problems.push(['message', 'Your message needs to be at least 10 characters.']);
      }

      if (problems.length) {
        problems.forEach(function (problem) {
          var field = form.elements[problem[0]];
          var wrapper = field && field.closest('.field');
          if (wrapper) wrapper.classList.add('has-error');
        });
        setStatus(problems[0][1], 'error');
        var firstField = form.elements[problems[0][0]];
        if (firstField) firstField.focus();
        return;
      }

      var tokenField = form.elements.csrfmiddlewaretoken;
      if (submitBtn) {
        submitBtn.classList.add('is-loading');
        submitBtn.disabled = true;
      }
      setStatus('Sending…');

      fetch(form.action, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': tokenField ? tokenField.value : '',
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin',
        body: JSON.stringify(data)
      })
        .then(function (response) {
          return response.json().then(function (payload) {
            return { ok: response.ok, payload: payload };
          });
        })
        .then(function (result) {
          if (result.ok && result.payload.success) {
            form.reset();
            setStatus(result.payload.message || 'Message sent.', 'ok');
          } else {
            setStatus(result.payload.message || 'Something went wrong. Please try again.', 'error');
          }
        })
        .catch(function () {
          setStatus(
            'Network error — you can also email pratham.m.jaiswal@gmail.com directly.',
            'error'
          );
        })
        .then(function () {
          if (submitBtn) {
            submitBtn.classList.remove('is-loading');
            submitBtn.disabled = false;
          }
        });
    });
  }
})();
