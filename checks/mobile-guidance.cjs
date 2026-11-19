const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const guidance = require(path.join(root, 'assets', 'mobile-guidance.js'));
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');

assert.equal(guidance.autoGuided(390, 844, true), true);
assert.equal(guidance.autoGuided(638, 904, false), false, 'a narrow desktop window must keep continuous scrolling');
assert.equal(guidance.autoGuided(638, 904, true), true, 'a coarse-pointer phone-sized viewport should keep chapter navigation');
assert.equal(guidance.autoGuided(844, 390), false);
assert.equal(guidance.autoGuided(1180, 757), true);
assert.equal(guidance.autoGuided(800, 700), false);
assert.equal(guidance.swipeThreshold(390), 42);
assert.equal(guidance.swipeThreshold(1180), 65);
assert.match(html, /PortfolioMobileGuidance\.autoGuided/);
assert.match(html, /PortfolioMobileGuidance\.swipeThreshold/);
console.log('mobile guidance: 10 assertions passed');
