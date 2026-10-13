// Checks a topic's Main.dc.html against the template contract (references/scene-api.md).
// Usage: node check.cjs <Main.dc.html> [--allow-template]   → prints "ok" (exit 0) or one error per line (exit 1)
const fs = require('node:fs');
const { readDc, loadComponent, makeCtx, makeCanvas } = require('./harness.cjs');

const SHELL = ['class="app"', 'class="topbar"', 'class="layout', 'panel panel-left', 'panel panel-right', 'class="scrim',
  'class="stage"', 'ref="{{canvasRef}}"', 'class="view-btns"', '@media (max-width: 1023.98px)', 'aria-label="{{themeLabel}}"', 'class="source"'];
const EVENTS = ['onClick', 'onKeyDown', 'onMouseEnter', 'onMouseLeave', 'onChange'];
const FRAMES = 120;

// Markup between </helmet> and </x-dc>: the part the runtime compiles.
function bodyMarkup(src) {
  return src.slice(src.indexOf('</helmet>') + '</helmet>'.length, src.indexOf('</x-dc>'));
}

// Every {{hole}} must name a renderVals key or an enclosing <sc-for as> name.
function unknownHoles(markup, keys) {
  const bad = new Set(), scope = [];
  const seen = (name) => keys.has(name) || scope.includes(name);
  const re = /<sc-for\b[^>]*>|<\/sc-for>|\shint-[\w-]+="[^"]*"|\{\{\s*([\w$]+)[\w.$]*\s*\}\}/g;
  let m;
  while ((m = re.exec(markup))) {
    const tok = m[0];
    if (tok.startsWith('<sc-for')) {
      const list = tok.match(/list="\{\{\s*([\w$]+)/), as = tok.match(/\sas="([\w$]+)"/);
      if (list && !seen(list[1])) bad.add(list[1]);
      scope.push(as ? as[1] : '');
    } else if (tok === '</sc-for>') scope.pop();
    else if (m[1] && !seen(m[1])) bad.add(m[1]);
  }
  return [...bad];
}

function renderChecks(file, modes, errors) {
  const keys = new Set();
  for (const narrow of [true, false]) {
    for (const theme of ['light', 'dark']) {
      for (const mode of modes) {
        try {
          const { c } = loadComponent(file, { narrow });
          c.setTheme(theme);
          c.setMode(mode);
          Object.keys(c.renderVals()).forEach((k) => keys.add(k));
        } catch (e) {
          errors.push('RENDER_THROWS:' + (narrow ? 'narrow' : 'wide') + '-' + theme + '-' + mode);
        }
      }
    }
  }
  return keys;
}

// Draws each mode directly (tick() swallows exceptions): sweeps playback 0→fmax and the
// camera around, light then dark, then each view option flipped once.
function drawChecks(file, modes, errors) {
  for (const mode of modes) {
    let c, calls, last = 0;
    try {
      ({ c } = loadComponent(file, { narrow: false }));
      c.setMode(mode);
      const made = makeCtx();
      calls = made.calls;
      c.attachCanvas(makeCanvas(made.ctx, 800, 600));
    } catch (e) {
      errors.push('DRAW_THROWS:' + mode);
      continue;
    }
    const pb = c.modeDef(mode).playback;
    try {
      if (pb) c.setState({ playing: true });
      for (let k = 0; k < FRAMES; k++) {
        if (k === FRAMES / 2) c.setTheme('dark');
        if (pb) { c.sim.f = pb.fmax * k / (FRAMES - 1); c.setState({ f: c.sim.f }); }
        c.cam.yaw += 0.05;
        last = calls.length;
        c.draw(0.016, (k + 1) * 16);
      }
      const end = calls.slice(last);
      if (!end.some((x) => x.op === 'arc' || x.op === 'lineTo' || x.op === 'fillText')) errors.push('SCENE_EMPTY:' + mode);
      for (const t of c.renderVals().toggles) {
        t.toggle();
        c.draw(0.016, 0);
        c.renderVals().toggles.find((x) => x.label === t.label).toggle();
      }
    } catch (e) {
      errors.push('DRAW_THROWS:' + mode);
    }
  }
}

function check(file, opts = {}) {
  const errors = [];
  const src = readDc(file);
  const head = src.slice(0, src.indexOf('data-dc-script'));
  const markup = bodyMarkup(src);

  for (const s of SHELL) if (!head.includes(s)) errors.push('SHELL_MISSING:' + s);
  for (const m of markup.matchAll(/\s(on[A-Z]\w*)=/g)) if (!EVENTS.includes(m[1])) errors.push('EVENT_UNSUPPORTED:' + m[1]);
  for (const m of markup.matchAll(/(?<!&)#[0-9a-fA-F]{6}(?![0-9a-fA-F])/g)) errors.push('HEX_IN_MARKUP:' + m[0]);

  let topic;
  try {
    topic = loadComponent(file).c.topic();
  } catch (e) {
    errors.push('RENDER_THROWS:load');
    return { ok: false, errors: [...new Set(errors)] };
  }
  const modes = topic.MODES.map((m) => m.key);
  const keys = renderChecks(file, modes, errors);
  for (const h of unknownHoles(markup, keys)) errors.push('HOLE_UNKNOWN:' + h);
  drawChecks(file, modes, errors);

  if (!opts.allowTemplate) {
    for (const p of ['__TITLE__', '__SOURCE__']) if (src.includes(p)) errors.push('TEMPLATE_LEFT:' + p);
    if (topic.DEMO === true) errors.push('TEMPLATE_LEFT:DEMO');
  }
  const uniq = [...new Set(errors)];
  return { ok: uniq.length === 0, errors: uniq };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const file = args.find((a) => !a.startsWith('--'));
  if (!file || !fs.existsSync(file)) {
    console.error('usage: node check.cjs <Main.dc.html> [--allow-template]');
    process.exit(2);
  }
  const r = check(file, { allowTemplate: args.includes('--allow-template') });
  console.log(r.ok ? 'ok' : r.errors.join('\n'));
  process.exit(r.ok ? 0 : 1);
}

module.exports = { check };
