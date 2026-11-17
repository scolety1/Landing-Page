(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PortfolioMobileGuidance = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function autoGuided(width, height) {
    const desktop = width >= 900 && height >= 620;
    const portraitPhone = width <= 760 && height >= 560 && height > width;
    return desktop || portraitPhone;
  }

  function swipeThreshold(width) {
    return width <= 760 ? 42 : 65;
  }

  return { autoGuided, swipeThreshold };
});
