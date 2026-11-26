/* Artech Digital — home page behaviour. Plain JavaScript, no libraries.
   1. Menu drop-down (tablet and phone)
   2. Sliders (projects, reviews, latest posts)
   3. Calendly booking widget, loaded only when the visitor gets near it
   4. Subscribe form */
(function () {
  'use strict';

  /* 1. Menu ------------------------------------------------------------- */
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('site-nav');

  function setMenu(open) {
    header.classList.toggle('is-menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  }
  if (header && toggle && nav) {
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) setMenu(false);
    });
    document.addEventListener('click', function (event) {
      if (!header.contains(event.target)) setMenu(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') setMenu(false);
    });
    window.matchMedia('(min-width: 992px)').addEventListener('change', function () { setMenu(false); });
  }

  /* 2. Sliders ----------------------------------------------------------
     Markup: [data-slider="cards|reviews"] wraps a [data-slider-viewport], its
     [data-slider-track] and the [data-slider-prev] / [data-slider-next] buttons.
       cards   — slides keep their own width, the arrows move one slide
       reviews — three per view (two on tablets, one on phones), the arrows move a full view,
                 and the track takes the height of the tallest visible review */
  function createSlider(root) {
    var kind = root.getAttribute('data-slider');
    var viewport = root.querySelector('[data-slider-viewport]');
    var track = root.querySelector('[data-slider-track]');
    var prev = root.querySelector('[data-slider-prev]');
    var next = root.querySelector('[data-slider-next]');
    var slides = Array.prototype.slice.call(track.children);
    var snaps = [0];
    var index = 0;
    var offset = 0;

    function perView() {
      /* reviews: the number per view is set in the stylesheet (--per-view) */
      return kind === 'reviews' ? (parseInt(getComputedStyle(viewport).getPropertyValue('--per-view'), 10) || 1) : 1;
    }

    function measure() {
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      var step = perView();
      if (kind === 'reviews') {
        /* equal columns, worked out from the whole-pixel width of the viewport */
        var width = (viewport.clientWidth - gap * (step - 1)) / step;
        slides.forEach(function (slide) { slide.style.width = width + 'px'; });
      }
      var first = slides[0].getBoundingClientRect().left;
      var end = slides[slides.length - 1].getBoundingClientRect().right;
      var max = Math.max(0, end - first - viewport.clientWidth);
      snaps = [];
      for (var i = 0; i < slides.length; i += step) {
        var x = slides[i].getBoundingClientRect().left - first;
        if (x >= max - 0.5) break;
        snaps.push(x);
      }
      snaps.push(max);
      index = Math.min(index, snaps.length - 1);
    }

    function fitHeight() {
      if (kind !== 'reviews') return;
      var start = index * perView();
      var tallest = 0;
      slides.slice(start, start + perView()).forEach(function (slide) {
        tallest = Math.max(tallest, slide.offsetHeight);
      });
      if (tallest) track.style.height = tallest + 'px';
    }

    function move(x) {
      offset = x;
      track.style.transform = 'translate3d(' + (-x) + 'px, 0, 0)';
    }

    function go(to) {
      index = Math.max(0, Math.min(to, snaps.length - 1));
      move(snaps[index]);
      fitHeight();
      prev.setAttribute('aria-disabled', String(index === 0));
      next.setAttribute('aria-disabled', String(index === snaps.length - 1));
    }

    function refresh() {
      measure();
      go(index);
    }

    prev.addEventListener('click', function () { go(index - 1); });
    next.addEventListener('click', function () { go(index + 1); });

    /* Drag with mouse, pen or finger */
    var drag = null;
    var justDragged = false;
    track.addEventListener('pointerdown', function (event) {
      if (event.pointerType === 'mouse' && event.button !== 0) return;
      drag = { x: event.clientX, y: event.clientY, from: offset, moved: false, time: Date.now() };
    });
    window.addEventListener('pointermove', function (event) {
      if (!drag) return;
      var dx = event.clientX - drag.x;
      if (!drag.moved) {
        if (Math.abs(dx) < 6 || Math.abs(dx) < Math.abs(event.clientY - drag.y)) return;
        drag.moved = true;
        track.classList.add('is-dragging');
      }
      var x = drag.from - dx;
      var max = snaps[snaps.length - 1];
      if (x < 0) x = x / 3;                       /* soft resistance past either end */
      if (x > max) x = max + (x - max) / 3;
      move(x);
    });
    function release(event) {
      if (!drag) return;
      var finished = drag;
      drag = null;
      if (!finished.moved) return;
      track.classList.remove('is-dragging');
      justDragged = true;
      setTimeout(function () { justDragged = false; }, 0);
      var dx = event.clientX - finished.x;
      var quick = Date.now() - finished.time < 300 && Math.abs(dx) > 20;
      var target = index;
      if (quick) {
        target = index + (dx < 0 ? 1 : -1);
      } else {
        var best = Infinity;
        snaps.forEach(function (snap, i) {
          var distance = Math.abs(snap - offset);
          if (distance < best) { best = distance; target = i; }
        });
      }
      go(target);
    }
    window.addEventListener('pointerup', release);
    window.addEventListener('pointercancel', release);
    /* A drag must not open the card underneath it */
    track.addEventListener('click', function (event) {
      if (justDragged) event.preventDefault();
    }, true);
    track.addEventListener('dragstart', function (event) { event.preventDefault(); });

    if ('ResizeObserver' in window) new ResizeObserver(refresh).observe(viewport);
    window.addEventListener('resize', refresh);
    window.addEventListener('load', refresh);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);

    /* First layout without the height animation */
    track.style.transitionDuration = '0s';
    refresh();
    requestAnimationFrame(function () { track.style.transitionDuration = ''; });
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-slider]'), createSlider);

  /* 3. Calendly ---------------------------------------------------------- */
  var calendar = document.querySelector('[data-calendly]');
  if (calendar) {
    var loadCalendar = function () {
      var frame = document.createElement('iframe');
      var url = calendar.getAttribute('data-calendly');
      frame.src = url + (url.indexOf('?') > -1 ? '&' : '?') + 'embed_domain=' + encodeURIComponent(location.hostname || 'localhost') + '&embed_type=Inline';
      frame.title = 'Select a date and time';
      frame.loading = 'lazy';
      calendar.appendChild(frame);
    };
    if ('IntersectionObserver' in window) {
      var watcher = new IntersectionObserver(function (entries) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) {
          watcher.disconnect();
          loadCalendar();
        }
      }, { rootMargin: '600px 0px' });
      watcher.observe(calendar);
    } else {
      loadCalendar();
    }
  }

  /* 4. Subscribe form -----------------------------------------------------
     Nothing is sent anywhere yet: connect this to your mailing-list service.
     Until then the form only shows the confirmation message. */
  var form = document.querySelector('[data-subscribe]');
  if (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      form.querySelector('.subscribe__row').hidden = true;
      form.querySelector('.subscribe__message').hidden = false;
    });
  }
})();
