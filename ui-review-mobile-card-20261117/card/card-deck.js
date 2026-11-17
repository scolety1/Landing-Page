(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else {
    root.CardDeck = api;
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', api.init, { once: true });
    else api.init();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function gestureDirection(delta, threshold) {
    if (Math.abs(delta) < threshold) return 0;
    return delta > 0 ? 1 : -1;
  }

  function clampPanel(index, count) {
    return Math.max(0, Math.min(Math.max(0, count - 1), index));
  }

  function nextPanel(index, delta, count, threshold) {
    return clampPanel(index + gestureDirection(delta, threshold), count);
  }

  function nearestPanel(panels) {
    let best = 0;
    let distance = Infinity;
    panels.forEach((panel, index) => {
      const value = Math.abs(panel.getBoundingClientRect().top);
      if (value < distance) {
        best = index;
        distance = value;
      }
    });
    return best;
  }

  function interactiveTarget(target) {
    return target instanceof Element && Boolean(target.closest('a,button,input,select,textarea,summary,[contenteditable="true"]'));
  }

  function init() {
    const panels = [...document.querySelectorAll('main > .panel')];
    if (panels.length < 2) return;
    const motion = matchMedia('(prefers-reduced-motion: reduce)');
    const threshold = 28;
    let wheelTotal = 0;
    let lastWheel = 0;
    let transitioning = false;
    let unlock = 0;
    let touchStart = null;

    function move(index) {
      const target = panels[clampPanel(index, panels.length)];
      if (!target) return;
      transitioning = true;
      target.scrollIntoView({ block: 'start', behavior: motion.matches ? 'auto' : 'smooth' });
      clearTimeout(unlock);
      unlock = setTimeout(() => { transitioning = false; }, motion.matches ? 80 : 430);
    }

    document.addEventListener('wheel', event => {
      if (motion.matches || transitioning || event.ctrlKey || event.metaKey || interactiveTarget(event.target)) return;
      const scale = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? innerHeight : 1;
      const vertical = event.deltaY * scale;
      if (Math.abs(vertical) < 1 || Math.abs(event.deltaX * scale) > Math.abs(vertical)) return;
      event.preventDefault();
      const now = performance.now();
      if (now - lastWheel > 160) wheelTotal = 0;
      lastWheel = now;
      wheelTotal += vertical;
      const direction = gestureDirection(wheelTotal, threshold);
      if (!direction) return;
      const current = nearestPanel(panels);
      wheelTotal = 0;
      move(current + direction);
    }, { passive: false });

    document.addEventListener('touchstart', event => {
      touchStart = null;
      if (motion.matches || transitioning || event.touches.length !== 1 || interactiveTarget(event.target) || (visualViewport?.scale || 1) > 1.01) return;
      const point = event.touches[0];
      touchStart = { id: point.identifier, x: point.clientX, y: point.clientY, panel: nearestPanel(panels) };
    }, { passive: true });

    document.addEventListener('touchcancel', () => { touchStart = null; }, { passive: true });
    document.addEventListener('touchend', event => {
      const start = touchStart;
      touchStart = null;
      if (!start || motion.matches || transitioning || event.touches.length) return;
      const point = [...event.changedTouches].find(item => item.identifier === start.id);
      if (!point) return;
      const dy = start.y - point.clientY;
      const dx = start.x - point.clientX;
      if (Math.abs(dy) <= Math.abs(dx) * 1.15) return;
      const direction = gestureDirection(dy, threshold);
      if (!direction || nearestPanel(panels) !== start.panel) return;
      move(start.panel + direction);
    }, { passive: true });
  }

  return { gestureDirection, clampPanel, nextPanel, init };
});
