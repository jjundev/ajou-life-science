// Loads the x-dc script from Main.dc.html into a vm sandbox with a DCLogic stub.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const PROJECT = path.join(__dirname, '..', 'canvas');
const MAIN_PATH = path.join(PROJECT, 'Main.dc.html');
const CANVAS_JSON_PATH = path.join(PROJECT, 'canvas.json');

function readMain() {
  return fs.readFileSync(MAIN_PATH, 'utf8');
}

function markupPart() {
  const html = readMain();
  return html.slice(0, html.indexOf('data-dc-script'));
}

function makeStorage(store, mode) {
  if (mode === 'throw') {
    const boom = () => { throw new Error('storage blocked'); };
    return { getItem: boom, setItem: boom, removeItem: boom };
  }
  return {
    getItem: (k) => (Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
  };
}

function loadComponent(opts = {}) {
  const src = readMain().match(/<script type="text\/x-dc"[^>]*>([\s\S]*?)<\/script>/)[1];
  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(u) { this.state = Object.assign({}, this.state, typeof u === 'function' ? u(this.state) : u); }
  }
  const store = opts.storage && opts.storage !== 'throw' ? opts.storage : {};
  const win = {
    matchMedia: (q) => ({
      matches: q.includes('prefers-color-scheme: dark') ? !!opts.systemDark
        : q.includes('max-width: 1023.98px') ? !!opts.narrow
        : q.includes('prefers-reduced-motion') ? !!opts.reduceMotion : false,
    }),
    localStorage: makeStorage(store, opts.storage),
    devicePixelRatio: 1,
    innerWidth: opts.innerWidth || 1440,
    addEventListener() {}, removeEventListener() {},
  };
  const ctx = vm.createContext({ DCLogic, window: win, requestAnimationFrame: () => 0, cancelAnimationFrame() {}, console });
  vm.runInContext(src + '\n;globalThis.__C = Component;', ctx);
  const c = new ctx.__C({});
  return { c, store, win };
}

// Canvas 2D stub that records every method call with the styles current at call time.
function makeCtx() {
  const calls = [];
  const target = { fillStyle: '', strokeStyle: '', globalAlpha: 1, lineWidth: 1, font: '', textAlign: '', textBaseline: '', lineCap: '' };
  const ctx = new Proxy(target, {
    get(t, prop) {
      if (prop in t) return t[prop];
      if (typeof prop !== 'string') return undefined;
      return (...args) => {
        calls.push({ op: prop, args, fillStyle: t.fillStyle, strokeStyle: t.strokeStyle });
        if (prop === 'createRadialGradient' || prop === 'createLinearGradient') return { addColorStop() {} };
        if (prop === 'measureText') return { width: 10 };
        return undefined;
      };
    },
    set(t, prop, v) { t[prop] = v; return true; },
  });
  return { ctx, calls };
}

module.exports = { loadComponent, readMain, markupPart, makeCtx, MAIN_PATH, CANVAS_JSON_PATH };
