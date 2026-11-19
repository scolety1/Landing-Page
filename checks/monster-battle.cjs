const assert = require('node:assert/strict');
const path = require('node:path');

const battle = require(path.resolve(__dirname, '..', 'assets', 'monster-battle.js'));

function play(actions) {
  return actions.reduce((state, action) => battle.applyMove(state, action), battle.initialState());
}

const direct = play(['leaf', 'leaf', 'tackle', 'tackle', 'tackle']);
assert.equal(direct.outcome, 'won', 'a straightforward attack sequence should win');
assert.ok(direct.hp >= 30, 'the straightforward win should leave a forgiving health margin');

const cautious = play(['guard', 'leaf', 'heal', 'leaf', 'guard', 'leaf', 'leaf', 'tackle']);
assert.equal(cautious.outcome, 'won', 'a cautious guard-and-recover strategy should also win');
assert.ok(cautious.hp > 0, 'the cautious strategy should keep Mossbit standing');

const charged = battle.applyMove(battle.applyMove(battle.initialState(), 'leaf'), 'guard');
assert.ok(charged.lastDamage <= 6, 'guarding an announced charge should make its reduced damage obvious');

console.log('monster battle: 5 assertions passed');
