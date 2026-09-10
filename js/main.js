/* Panwar Knitwear — nav, category filter, and the GSAP motion layer.
   Motion is progressive enhancement: if GSAP fails to load, or the visitor
   prefers reduced motion, everything is shown in its final state. */
(function () {
  'use strict';

  var root = document.documentElement;
  var released = false;
  var motionOK = matchMedia('(prefers-reduced-motion: no-preference)').matches;
  var introRunning = false;   // true once the intro has taken control

  /* Drop the CSS staging class so nothing can be left invisible. */
  function release() {
    if (released) return;
    released = true;
    root.classList.remove('anim');
  }

  /* Kept separate from release(): initMotion() calls release() early, before
     the intro has had a chance to play. Only failure paths dismiss the intro. */
  function dismissIntro() { root.classList.remove('intro-armed'); }

  /* --- Mobile navigation ------------------------------------------------ */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* --- Header scroll state ----------------------------------------------
     A plain passive listener rather than a ScrollTrigger, so the header still
     behaves correctly when GSAP is unavailable. The transition is CSS. */
  var header = document.querySelector('.site-header');
  if (header && !header.classList.contains('site-header--solid')) {
    var onScroll = function () {
      // Compare against the DOM rather than a cached flag so the state can
      // never desync if anything else touches the class.
      var should = window.scrollY > 40;
      if (should !== header.classList.contains('is-condensed')) {
        header.classList.toggle('is-condensed', should);
      }
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* --- Product category filter ------------------------------------------ */
  var chips = document.querySelectorAll('.chip[data-filter]');
  var plates = document.querySelectorAll('.plates [data-categories]');
  var countEl = document.getElementById('filter-count');

  function applyFilter(key, animate) {
    var shown = [];
    plates.forEach(function (plate) {
      var ok = key === 'all' || plate.dataset.categories.split(' ').indexOf(key) !== -1;
      plate.classList.toggle('is-hidden', !ok);
      if (ok) shown.push(plate);
    });
    if (countEl) {
      countEl.textContent = shown.length + (shown.length === 1 ? ' Product' : ' Products');
    }
    if (animate && motionOK && window.gsap && shown.length) {
      gsap.killTweensOf(shown);
      gsap.fromTo(shown,
        { opacity: 0, y: 14 },
        {
          opacity: 1, y: 0, duration: .45, ease: 'power2.out',
          stagger: .025, overwrite: true,
          // clearProps so a filtered plate never keeps an inline opacity
          onComplete: function () { gsap.set(shown, { clearProps: 'opacity,transform' }); }
        });
    }
    if (window.ScrollTrigger) ScrollTrigger.refresh();
  }

  if (chips.length && plates.length) {
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
        chip.setAttribute('aria-pressed', 'true');
        applyFilter(chip.dataset.filter, true);
        history.replaceState(null, '', chip.dataset.filter === 'all'
          ? location.pathname
          : location.pathname + '#' + chip.dataset.filter);
      });
    });

    // Honour a category passed in the URL hash (category rows link this way).
    var initial = location.hash.replace('#', '');
    var preset = initial &&
      document.querySelector('.chip[data-filter="' + CSS.escape(initial) + '"]');
    if (preset) {
      chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
      preset.setAttribute('aria-pressed', 'true');
      applyFilter(preset.dataset.filter, false);
    } else {
      applyFilter('all', false);
    }
  }

  /* --- Motion layer ------------------------------------------------------ */
  function initMotion() {
    if (!motionOK || !window.gsap || !window.ScrollTrigger) { release(); dismissIntro(); return; }

    gsap.registerPlugin(ScrollTrigger);

    var q = function (sel) { return gsap.utils.toArray(sel); };
    var ups = q('[data-anim="up"]');
    var plateEls = q('[data-anim="plate"]');
    var heroLines = q('.hero-title .line > span');

    /* Take ownership of the staged elements, then release the CSS class.
       This runs in one synchronous task, so no paint happens in between and
       there is no flash of unstyled/unpositioned content. */
    gsap.set(ups, { opacity: 0, y: 26 });
    gsap.set(plateEls, { opacity: 0, y: 30 });
    gsap.set(heroLines, { yPercent: 108 });
    release();

    /* Hero entrance. Built paused: the brand intro (when it runs) starts it at
       the hand-off point so the two read as one continuous move. */
    var heroTl = null;
    if (heroLines.length) {
      var tl = heroTl = gsap.timeline({ paused: true, defaults: { ease: 'power3.out' } });
      tl.set('.hero-title', { opacity: 1 })
        .to(heroLines, { yPercent: 0, duration: 1, stagger: .09 }, 0)
        .to('.hero-media figure', { opacity: 1, duration: 1.1 }, .15)
        .from('.hero-media figure', { scale: 1.07, duration: 1.4, ease: 'power2.out' }, .15)
        .to('.hero-copy .lede', { opacity: 1, y: 0, duration: .7 }, .5)
        .to('.hero-copy [data-anim="cta"]', { opacity: 1, y: 0, duration: .55, stagger: .07 }, .62)
        .to('.hero-foot span', { opacity: 1, y: 0, duration: .5, stagger: .06 }, .75)
        .to('.hero-rail', { opacity: 1, duration: .7 }, .85);

      gsap.set('.hero-copy .lede', { y: 18 });
      gsap.set('.hero-copy [data-anim="cta"]', { y: 14 });
      gsap.set('.hero-foot span', { y: 10 });
    }

    /* --- Brand intro: spec sheet -> product -> business ---------------------
       ~1.9s, homepage only, once per tab session. Plays only if the head
       script armed it (motion welcome + not seen yet); otherwise the hero
       simply starts immediately. */
    function startHero() { if (heroTl) heroTl.play(); }

    var introEl = document.getElementById('intro');
    if (introEl && root.classList.contains('intro-armed')) {
      var brandWord = introEl.querySelector('.intro-brand .l > span');
      var lineWords = introEl.querySelectorAll('.intro-line .l > span');
      var media = introEl.querySelector('.intro-media');
      var mediaImg = introEl.querySelector('.intro-media img');

      /* The CSS start state uses translateY(%), which GSAP reads back as a
         pixel matrix. Re-declare it in GSAP's own yPercent so the tweens below
         actually land on zero instead of leaving a stale pixel offset. */
      gsap.set(brandWord, { yPercent: 106, y: 0 });
      gsap.set(lineWords, { yPercent: 110, y: 0 });

      /* The intro is in charge now. Cancel the "scripts never arrived"
         failsafe, otherwise it would tear the overlay down at 6s while it is
         legitimately waiting for the visitor to scroll. */
      introRunning = true;
      clearTimeout(window.__pkFailsafe);

      var left = false;

      function offTriggers() {
        removeEventListener('wheel', onWheel);
        removeEventListener('touchmove', onWheel);
        removeEventListener('keydown', onLeave);
        removeEventListener('scroll', onLeave);
        introEl.removeEventListener('click', onLeave);
      }
      /* Scrolling is blocked by cancelling the gesture, not by overflow:hidden
         — hiding the scrollbar would shift the layout underneath. */
      function onWheel(e) { e.preventDefault(); onLeave(); }
      function onLeave() {
        if (left) return;
        left = true;
        offTriggers();
        window.scrollTo(0, 0);   // discard anything that leaked through

        /* The head-script failsafe is cancelled by now, so if the outro were to
           throw the overlay would be stranded. Guarantee the exit either way. */
        function finish() {
          dismissIntro();
          startHero();
          try { sessionStorage.setItem('pk-intro', '1'); } catch (e) {}
        }
        try {
        gsap.timeline({ onComplete: finish })
          .to('.intro-cue', { opacity: 0, duration: .25, ease: 'power2.in' }, 0)
          .to('.intro-inner', { y: -22, scale: .985, duration: .55, ease: 'power2.in' }, 0)
          /* hero starts while the overlay is still fading, so it reads as one move */
          .add(startHero, .12)
          .to('.site-header', { opacity: 1, duration: .5, ease: 'power2.out' }, .12)
          .to(introEl, { opacity: 0, duration: .5, ease: 'power2.inOut' }, .08);
        } catch (e) { finish(); }
      }

      addEventListener('wheel', onWheel, { passive: false });
      addEventListener('touchmove', onWheel, { passive: false });
      addEventListener('keydown', onLeave);
      addEventListener('scroll', onLeave, { passive: true });
      introEl.addEventListener('click', onLeave);

      /* Plays once, then holds on the final composition until onLeave() fires. */
      gsap.timeline()
        /* 1. brand + location */
        .to(brandWord, { yPercent: 0, duration: .7, ease: 'power3.out' }, .05)
        .to('.intro-loc', { opacity: 1, duration: .5, ease: 'power2.out' }, .3)
        .from('.intro-loc', { y: 10, duration: .5, ease: 'power2.out' }, .3)
        /* 2. technical labels */
        .to('.intro-specs li', { opacity: 1, duration: .45, stagger: .06, ease: 'power2.out' }, .45)
        .from('.intro-specs li', { y: 8, duration: .45, stagger: .06, ease: 'power2.out' }, .45)
        /* 3. the crop opens into the product image (clip + scale only) */
        .fromTo(media,
          { clipPath: 'inset(46% 44% 46% 44%)' },
          { clipPath: 'inset(0% 0% 0% 0%)', duration: .85, ease: 'power2.inOut' }, .6)
        .from(mediaImg, { scale: 1.35, duration: 1, ease: 'power2.out' }, .6)
        /* 4. the line */
        .to(lineWords, { yPercent: 0, duration: .6, stagger: .08, ease: 'power3.out' }, 1.05)
        /* 5. invitation to continue — then it waits */
        .to('.intro-cue', { opacity: 1, duration: .5, ease: 'power2.out' }, 1.5);
    } else {
      startHero();
    }

    /* Section reveals — batched, fire once, then the observer detaches. */
    if (ups.length) {
      ScrollTrigger.batch(ups, {
        start: 'top 88%',
        once: true,
        onEnter: function (batch) {
          gsap.to(batch, {
            opacity: 1, y: 0, duration: .8, ease: 'power3.out',
            stagger: .08, clearProps: 'transform'
          });
        }
      });
    }

    /* Product plates — tighter stagger; they arrive in rows. */
    if (plateEls.length) {
      ScrollTrigger.batch(plateEls, {
        start: 'top 92%',
        once: true,
        onEnter: function (batch) {
          gsap.to(batch, {
            opacity: 1, y: 0, duration: .7, ease: 'power2.out',
            stagger: .055, clearProps: 'transform'
          });
        }
      });
    }

    /* --- Manufacturing process sequence: 01 -> 02 -> 03 -> 04 ------------
       Desktop pins the block and scrubs through the four stages. Small
       screens get the same order as plain reveals, no pinning. Either way
       `.is-enhanced` is what dims the inactive stages, so if this never runs
       the four stages stay fully legible. */
    var proc = document.querySelector('[data-proc]');
    if (proc) {
      var procItems = gsap.utils.toArray('.proc-item', proc);
      var fill = proc.querySelector('.proc-fill');
      var odoTrack = proc.querySelector('.proc-odo-track');
      var current = proc.querySelector('#proc-current');
      var n = procItems.length;
      var active = -1;

      var setStage = function (i) {
        i = Math.max(0, Math.min(n - 1, i));
        if (i === active) return;
        active = i;
        procItems.forEach(function (el, j) {
          el.classList.toggle('is-active', j === i);
          el.classList.toggle('is-past', j < i);
        });
        if (current) current.textContent = ('0' + (i + 1)).slice(-2);
        if (odoTrack) {
          // yPercent is a share of the whole track (n numerals tall), so one
          // step is 100/n — not 100.
          gsap.to(odoTrack, {
            yPercent: -(100 / n) * i,
            duration: .5, ease: 'power3.out', overwrite: true
          });
        }
      };

      proc.classList.add('is-enhanced');
      setStage(0);

      var mmProc = gsap.matchMedia();

      /* Desktop — pinned, scrubbed sequence */
      mmProc.add('(min-width: 861px)', function () {
        var stItem = ScrollTrigger.create({
          trigger: proc,
          start: 'center center',
          end: function () { return '+=' + (n * 260); },
          pin: true,
          pinSpacing: true,
          anticipatePin: 1,
          scrub: .6,
          invalidateOnRefresh: true,
          onUpdate: function (self) {
            // progress -> stage index, and the rail fills with it
            setStage(Math.floor(self.progress * n * 0.999));
            if (fill) gsap.set(fill, { scaleX: self.progress });
          },
          onLeaveBack: function () { setStage(0); if (fill) gsap.set(fill, { scaleX: 0 }); }
        });
        return function () {
          stItem.kill();
          if (fill) gsap.set(fill, { clearProps: 'transform' });
        };
      });

      /* Small screens — same order, no pinning: each stage activates as it
         reaches the middle of the viewport, and the rail fills vertically. */
      mmProc.add('(max-width: 860px)', function () {
        var triggers = procItems.map(function (el, i) {
          return ScrollTrigger.create({
            trigger: el,
            start: 'top 62%',
            end: 'bottom 38%',
            onEnter: function () { setStage(i); },
            onEnterBack: function () { setStage(i); }
          });
        });
        var railST = ScrollTrigger.create({
          trigger: proc.querySelector('.proc-stages'),
          start: 'top 70%',
          end: 'bottom 60%',
          scrub: .5,
          onUpdate: function (self) { if (fill) gsap.set(fill, { scaleY: self.progress }); }
        });
        return function () {
          triggers.forEach(function (t) { t.kill(); });
          railST.kill();
          if (fill) gsap.set(fill, { clearProps: 'transform' });
        };
      });
    }

    /* Subtle parallax — transform only, never layout. */
    q('[data-parallax]').forEach(function (el) {
      gsap.fromTo(el, { yPercent: -4.5 }, {
        yPercent: 4.5, ease: 'none',
        scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true }
      });
    });

    addEventListener('load', function () { ScrollTrigger.refresh(); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMotion);
  } else {
    initMotion();
  }

  /* Last-resort safety net: if anything above threw, content is still shown. */
  setTimeout(function () {
    release();
    // Never dismiss an intro that is intentionally waiting for the visitor.
    if (!introRunning) dismissIntro();
  }, 4000);
})();
