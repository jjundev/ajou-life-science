// Prints what the page shows at each step: playback label, canvas description and the topic's panel values.
// Usage: node steps.cjs <Main.dc.html>   → one block per step, or "단계 없음"
// Used by the content review (step 5) and the browser check (step 6) to compare step text with the screen.
const fs = require('node:fs');
const { loadComponent, makeCtx, makeCanvas } = require('./harness.cjs');

const PANEL_MAX = 400;

// Topic panel values (extraVals) without the handlers, as one JSON line.
function panelOf(c) {
  const vals = c.extraVals(c.state) || {};
  const plain = JSON.stringify(vals, (k, v) => (typeof v === 'function' ? undefined : v));
  return plain.length > PANEL_MAX ? plain.slice(0, PANEL_MAX) + '…' : plain;
}

function stepsReport(file) {
  const { c } = loadComponent(file, { narrow: false });
  c.attachCanvas(makeCanvas(makeCtx().ctx, 800, 600));
  return (c.T.STEPS || []).map((s, i) => {
    c.renderVals().steps[i].pick();
    c.draw(0.016, 0);
    const v = c.renderVals();
    return {
      n: i + 1, title: s.title, mode: s.mode, f: s.f == null ? null : s.f, phase: s.phase == null ? null : s.phase,
      fLabel: v.fLabel, canvasLabel: v.canvasLabel, panel: panelOf(c),
    };
  });
}

if (require.main === module) {
  const file = process.argv[2];
  if (!file || !fs.existsSync(file)) {
    console.error('usage: node steps.cjs <Main.dc.html>');
    process.exit(2);
  }
  const r = stepsReport(file);
  if (!r.length) console.log('단계 없음');
  for (const s of r) {
    console.log(s.n + '. ' + s.title + ' [' + s.mode + (s.f == null ? '' : ' f=' + s.f) + (s.phase == null ? '' : ' phase=' + s.phase) + ']');
    console.log('   재생 바: ' + (s.fLabel || '-'));
    console.log('   캔버스: ' + s.canvasLabel);
    console.log('   패널: ' + s.panel);
  }
}

module.exports = { stepsReport };
