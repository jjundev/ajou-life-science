// Fingerprints the replication scene with the twist off, so the flat (3D off) view stays exactly as it was.
// Regenerate only on purpose:  node tests/fixtures/replication-snapshot.cjs
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const FIELDS = ['k', 'p', 'q', 'r', 'w', 'c', 'a', 'rod', 'flat', 'focus', 't', 'text', 'dx', 'dy', 'size', 'lead'];
const FS = [0, 3, 5, 11.8, 17, 23.5, 26.9, 28.3, 40, 60];

function snapshot(c, f) {
  c.state.mode = 'replication';
  c.sim.f = f;
  c.sim.tw = 0;
  const I = [], O = [];
  c.buildReplication(I, O);
  const items = [...I, ...O].map((it) => {
    const o = {};
    for (const k of FIELDS) if (it[k] !== undefined) o[k] = Array.isArray(it[k]) ? [...it[k]] : it[k];
    return o;
  });
  return { n: items.length, sha: crypto.createHash('sha256').update(JSON.stringify(items)).digest('hex') };
}

if (require.main === module) {
  const { loadComponent } = require('../harness.cjs');
  const out = {};
  for (const f of FS) out[f] = snapshot(loadComponent({ systemDark: false }).c, f);
  fs.writeFileSync(path.join(__dirname, 'replication-flat.json'), JSON.stringify(out, null, 2) + '\n');
}

module.exports = { snapshot, FS };
