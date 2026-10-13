// Saves one topic into a 복습노트 folder under the next free number, then builds its page.
// Usage: node save.cjs <RUN/n/Main.dc.html> <DEST>   → {"nn", "html", "dir"} JSON (exit 0), usage on stderr (exit 2)
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
  const copy = path.join(dir, 'Main.dc.html');
  fs.copyFileSync(src, copy);
  fs.writeFileSync(html, build(copy, html));
  fs.writeFileSync(path.join(dir, 'canvas.json'), canvasJson(titleOf(fs.readFileSync(copy, 'utf8'))));
  return { nn, html, dir };
}

if (require.main === module) {
  const [src, dest] = process.argv.slice(2);
  if (!src || !dest || !fs.existsSync(src)) {
    console.error('usage: node save.cjs <RUN/n/Main.dc.html> <DEST>');
    process.exit(2);
  }
  console.log(JSON.stringify(save({ src, dest })));
}

module.exports = { save };
