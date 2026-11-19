(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MonsterBattle = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const patterns = ['Spark', 'Charge', 'Spark', 'Rest'];
  const actions = new Set(['leaf', 'tackle', 'guard', 'heal']);

  function initialState() {
    return {
      hp: 100,
      maxHp: 100,
      enemy: 90,
      maxEnemy: 90,
      turn: 0,
      heals: 3,
      energy: 3,
      maxEnergy: 3,
      lastDamage: 0,
      message: 'Mossbit faces Emberfin. Emberfin shows its next move before you act.',
      outcome: 'playing',
    };
  }

  function applyMove(current, move) {
    if (!actions.has(move)) throw new RangeError(`Unknown battle move: ${move}`);
    if (current.outcome !== 'playing') return current;
    if (move === 'leaf' && current.energy === 0) return current;
    if (move === 'heal' && current.heals === 0) return current;

    const state = { ...current, lastDamage: 0 };
    const guard = move === 'guard';
    let result = '';

    if (move === 'leaf') {
      state.energy -= 1;
      state.enemy = Math.max(0, state.enemy - 26);
      result = 'Leaf burst deals 26 and uses one charge.';
    } else if (move === 'tackle') {
      state.enemy = Math.max(0, state.enemy - 18);
      result = 'Tackle deals 18.';
    } else if (move === 'heal') {
      state.hp = Math.min(state.maxHp, state.hp + 28);
      state.heals -= 1;
      result = 'You recover up to 28 HP.';
    } else {
      state.energy = Math.min(state.maxEnergy, state.energy + 1);
      result = 'You brace for the next hit and restore one leaf charge.';
    }

    const enemyMove = patterns[state.turn % patterns.length];
    if (state.enemy > 0) {
      if (enemyMove === 'Rest') {
        state.enemy = Math.min(state.maxEnemy, state.enemy + 6);
        result += ' Emberfin rests and recovers 6.';
      } else {
        const baseDamage = enemyMove === 'Charge' ? 24 : 14;
        state.lastDamage = Math.round(baseDamage * (guard ? 0.25 : 1));
        state.hp = Math.max(0, state.hp - state.lastDamage);
        result += ` ${enemyMove} deals ${state.lastDamage}${guard ? ' after your guard.' : '.'}`;
      }
    }

    state.turn += 1;
    state.message = result;
    state.outcome = state.enemy <= 0 ? 'won' : state.hp <= 0 ? 'lost' : 'playing';
    return state;
  }

  return { patterns, initialState, applyMove };
});
