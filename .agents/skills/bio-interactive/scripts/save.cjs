// Saves one topic into a 복습노트 folder under the next free number, then builds its page.
// Usage: node save.cjs <RUN/n/Main.dc.html> <DEST>   → {"nn", "html", "dir"} JSON (exit 0), usage (exit 2) or the error (exit 1) on stderr
// Never overwrites: the number skips both 인터렉티브_NN.html and 자료_인터렉티브_NN. Nothing is written next to the source.
const fs = require('node:fs');
const path = require('node:path');
const { nextNumber } = require('./resolve.cjs');
const { build, canvasJson, titleOf } = require('./build.cjs');

function save({ src, dest }) {
  src = path.resolve(src);
  dest = path.resolve(dest);
  fs.mkdirSync(dest, { recursive: true });
  const nn = nextNumber(dest);
  const dir = path.join(dest, '자료_인터렉티브_' + nn);
  const html = path.join(dest, '인터렉티브_' + nn + '.html');
  fs.mkdirSync(dir); // not recursive: fails instead of writing into a folder that appeared meanwhile
  try {
    const copy = path.join(dir, 'Main.dc.html');
    fs.copyFileSync(src, copy);
    fs.writeFileSync(path.join(dir, 'canvas.json'), canvasJson(titleOf(fs.readFileSync(copy, 'utf8'))));
    fs.writeFileSync(html, build(copy, html));
  } catch (e) {
    // A half-made number would push every later save past a gap.
    fs.rmSync(dir, { recursive: true, force: true });
    throw e;
  }
  return { nn, html, dir };
}

if (require.main === module) {
  const [src, dest] = process.argv.slice(2);
  if (!src || !dest || !fs.existsSync(src) || !fs.statSync(src).isFile()) {
    console.error('usage: node save.cjs <RUN/n/Main.dc.html> <DEST>');
    process.exit(2);
  }
  try {
    console.log(JSON.stringify(save({ src, dest })));
  } catch (e) {
    console.error('save failed: ' + String(e.message || e).split('\n')[0]);
    process.exit(1);
  }
}

module.exports = { save };
