const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const mainHtml = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const cardHtml = fs.readFileSync(path.join(root, 'card', 'index.html'), 'utf8');

const guidance = require(path.join(root, 'assets', 'mobile-guidance.js'));
const cardDeck = require(path.join(root, 'card', 'card-deck.js'));

assert.equal(guidance.autoGuided(390, 844), true, 'portrait phone should start in chapter mode');
assert.equal(guidance.autoGuided(844, 390), false, 'short landscape phone should use continuous scrolling');
assert.equal(guidance.autoGuided(1180, 757), true, 'desktop should retain chapter mode');
assert.equal(guidance.autoGuided(800, 700), false, 'mid-size non-phone viewport should retain continuous scrolling');
assert.equal(guidance.swipeThreshold(390), 42, 'phone swipe should use the responsive threshold');
assert.equal(guidance.swipeThreshold(1180), 65, 'desktop swipe should retain its threshold');
assert.match(mainHtml, /PortfolioMobileGuidance\.autoGuided/, 'chapter controller should use tested geometry behavior');
assert.match(mainHtml, /PortfolioMobileGuidance\.swipeThreshold/, 'chapter controller should use tested swipe behavior');

const panelIds = [...cardHtml.matchAll(/<section\b[^>]*class="[^"]*\bpanel\b[^"]*"[^>]*\bid="([^"]+)"/g)].map(match => match[1]);
assert.deepEqual(panelIds, ['hello', 'work', 'about', 'development', 'more-work', 'world-forge', 'contact']);
assert.doesNotMatch(cardHtml, /THE SHORT VERSION|class="edition"|class="bottom-bar"|class="section-nav"|id="scroll-mode"/);
assert.match(cardHtml, /noindex,nofollow/);
assert.match(cardHtml, /spencer-colety-software-engineer-headshot-blue\.png/);
assert.match(cardHtml, /\.portrait-row img\{[^}]*width:112px;[^}]*height:112px/, 'portrait should stay square before circular cropping');
assert.match(cardHtml, /Frame[\s\S]*Direct[\s\S]*Review[\s\S]*Verify/);
assert.match(cardHtml, /24 project records/i);
assert.match(cardHtml, /World Forge[\s\S]*In development[\s\S]*true freedom/i);
assert.match(cardHtml, /spencer@coletylabs\.com/);
assert.match(cardHtml, /linkedin\.com\/in\/spencer-colety-a64b66280/);
assert.match(cardHtml, /github\.com\/scolety1/);
assert.match(cardHtml, /card-deck\.js/);
assert.doesNotMatch(cardHtml, /CardDeck\.init\(\)/, 'card deck should initialize exactly once through the external controller');

assert.equal(cardDeck.gestureDirection(0, 28), 0);
assert.equal(cardDeck.gestureDirection(27, 28), 0);
assert.equal(cardDeck.gestureDirection(28, 28), 1);
assert.equal(cardDeck.gestureDirection(-28, 28), -1);
assert.equal(cardDeck.clampPanel(-1, 7), 0);
assert.equal(cardDeck.clampPanel(3, 7), 3);
assert.equal(cardDeck.clampPanel(8, 7), 6);
assert.equal(cardDeck.nextPanel(2, 40, 7, 28), 3, 'small down intent should advance one panel');
assert.equal(cardDeck.nextPanel(2, -40, 7, 28), 1, 'small up intent should reverse one panel');
assert.equal(cardDeck.nextPanel(2, 8, 7, 28), 2, 'sub-threshold movement should not advance');

console.log('mobile/card refresh: 32 assertions passed');
