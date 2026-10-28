const V = require('./voting.js'); const assert = require('assert');
// Wikipedia "Tennessee capital" example (42/26/15/17)
const T = [
 { count: 42, ranking: ['Memphis','Nashville','Chattanooga','Knoxville'] },
 { count: 26, ranking: ['Nashville','Chattanooga','Knoxville','Memphis'] },
 { count: 15, ranking: ['Chattanooga','Knoxville','Nashville','Memphis'] },
 { count: 17, ranking: ['Knoxville','Chattanooga','Nashville','Memphis'] },
];
assert.deepStrictEqual(V.plurality(T).winners, ['Memphis']);
assert.deepStrictEqual(V.irv(T).winners, ['Knoxville']);
assert.deepStrictEqual(V.condorcet(T).winners, ['Nashville']);
assert.strictEqual(V.condorcet(T).pairwise.Nashville.Memphis, 58);
// Approval with top-2: Nashville 26+42+15+17=100? check
assert.deepStrictEqual(V.approval(T, 2).tally, { Memphis:42, Nashville:68, Chattanooga:58, Knoxville:32 });
assert.deepStrictEqual(V.approval(T, 2).winners, ['Nashville']);
// Spoiler effect: 45 A>B>C, 40 B>A>C... plus 15 C>B>A: plurality A, IRV B
const S = [ {count:45,ranking:['A','B','C']}, {count:40,ranking:['B','A','C']}, {count:15,ranking:['C','B','A']} ];
assert.deepStrictEqual(V.plurality(S).winners, ['A']);
assert.deepStrictEqual(V.irv(S).winners, ['B']);
// Condorcet cycle: no winner, Copeland tie
const C = [ {count:1,ranking:['A','B','C']}, {count:1,ranking:['B','C','A']}, {count:1,ranking:['C','A','B']} ];
assert.strictEqual(V.condorcet(C).condorcetWinner, null);
// Partial ballots and single-candidate
assert.deepStrictEqual(V.irv([{count:3,ranking:['X']}]).winners, ['X']);
assert.deepStrictEqual(V.irv([{count:2,ranking:['A']},{count:2,ranking:['B']}]).winners, ['A','B']);
console.log('all tests passed');
