// Voting method counters for the hoto.lol demo. Pure functions, no dependencies.
// A ballot profile: [{ count: number, ranking: [candidate,...] (best first, may be partial) }]
(function (root) {
  function candidatesOf(profile) {
    const s = new Set();
    profile.forEach(b => b.ranking.forEach(c => s.add(c)));
    return [...s];
  }
  function total(profile) { return profile.reduce((a, b) => a + b.count, 0); }

  function plurality(profile) {
    const tally = {};
    candidatesOf(profile).forEach(c => (tally[c] = 0));
    profile.forEach(b => { if (b.ranking.length) tally[b.ranking[0]] += b.count; });
    return { tally, winners: top(tally), rounds: null };
  }

  // Instant runoff. Ties for last are eliminated together only if all remaining tie; otherwise
  // the alphabetically-first of the lowest is eliminated (deterministic, documented in the UI).
  function irv(profile) {
    let alive = new Set(candidatesOf(profile));
    const rounds = [];
    while (alive.size) {
      const tally = {};
      alive.forEach(c => (tally[c] = 0));
      let active = 0;
      profile.forEach(b => {
        const first = b.ranking.find(c => alive.has(c));
        if (first !== undefined) { tally[first] += b.count; active += b.count; }
      });
      rounds.push({ tally: { ...tally }, active });
      const leaders = top(tally);
      if (tally[leaders[0]] * 2 > active || alive.size === 1) return { winners: [leaders[0]], rounds };
      const min = Math.min(...Object.values(tally));
      const lows = Object.keys(tally).filter(c => tally[c] === min).sort();
      if (lows.length === alive.size) return { winners: lows, rounds };
      alive.delete(lows[0]);
      rounds[rounds.length - 1].eliminated = lows[0];
    }
    return { winners: [], rounds };
  }

  // Approval: each ballot approves its top `k` ranked candidates unless it has an explicit `approved` list.
  function approval(profile, k = 2) {
    const tally = {};
    candidatesOf(profile).forEach(c => (tally[c] = 0));
    profile.forEach(b => {
      const set = b.approved || b.ranking.slice(0, k);
      set.forEach(c => (tally[c] += b.count));
    });
    return { tally, winners: top(tally) };
  }

  // Pairwise comparisons. Unranked candidates count as below all ranked ones.
  function pairwise(profile) {
    const cs = candidatesOf(profile), m = {};
    cs.forEach(a => { m[a] = {}; cs.forEach(b => { if (a !== b) m[a][b] = 0; }); });
    profile.forEach(bl => {
      const pos = c => { const i = bl.ranking.indexOf(c); return i === -1 ? Infinity : i; };
      cs.forEach(a => cs.forEach(b => { if (a !== b && pos(a) < pos(b)) m[a][b] += bl.count; }));
    });
    return m;
  }
  function condorcet(profile) {
    const m = pairwise(profile), cs = Object.keys(m);
    const wins = {};
    cs.forEach(a => (wins[a] = cs.filter(b => b !== a && m[a][b] > m[b][a]).length));
    const winner = cs.find(a => wins[a] === cs.length - 1) || null;
    // Copeland fallback if no Condorcet winner (wins + 0.5 per tie)
    const score = {};
    cs.forEach(a => (score[a] = wins[a] + 0.5 * cs.filter(b => b !== a && m[a][b] === m[b][a]).length));
    return { pairwise: m, condorcetWinner: winner, copeland: score, winners: winner ? [winner] : top(score) };
  }

  function top(tally) {
    const max = Math.max(...Object.values(tally));
    return Object.keys(tally).filter(c => tally[c] === max).sort();
  }

  const api = { plurality, irv, approval, condorcet, pairwise, total };
  if (typeof module !== 'undefined') module.exports = api; else root.Voting = api;
})(this);
