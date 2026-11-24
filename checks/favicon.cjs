const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const assetName = 'spencer-colety-sc-favicon-paper.png';
const assetPath = path.join(root, 'assets', assetName);
const homepage = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const card = fs.readFileSync(path.join(root, 'card', 'index.html'), 'utf8');

assert.ok(fs.existsSync(assetPath), 'favicon PNG must exist in assets');
const png = fs.readFileSync(assetPath);
assert.equal(png.subarray(1, 4).toString('ascii'), 'PNG', 'favicon must be a PNG');
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
assert.equal(width, height, 'favicon must be square');
assert.ok(width >= 48, 'favicon must be at least 48px square');

const iconHref = `/assets/${assetName}`;
for (const [label, html] of [['homepage', homepage], ['card', card]]) {
  assert.match(html, new RegExp(`<link rel="icon" type="image/png" href="${iconHref.replaceAll('/', '\\/')}"`), `${label} must declare the SC PNG favicon`);
  assert.match(html, new RegExp(`<link rel="apple-touch-icon" href="${iconHref.replaceAll('/', '\\/')}"`), `${label} must declare the SC touch icon`);
}

console.log(`favicon contract: 8 assertions passed (${width}x${height})`);
