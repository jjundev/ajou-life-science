// Builds a standalone page (opens directly in a browser) from a .dc.html source.
// Usage: node build.cjs <자료_인터렉티브_NN/Main.dc.html> <인터렉티브_NN.html>
const fs = require('node:fs');
const path = require('node:path');

const RUNTIME_PATH = path.join(__dirname, '..', 'assets', 'dc-runtime.js');
const FONT_CSS = 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.css';

function titleOf(src) {
  const m = src.match(/<title>([\s\S]*?)<\/title>/);
  return m ? m[1].trim() : '';
}

function build(srcFile, outFile) {
  const src = fs.readFileSync(srcFile, 'utf8');
  // Uploaded /_blob fonts only resolve inside the canvas; the page loads Pretendard from the CDN like the notes.
  const helmet = src.match(/<helmet>([\s\S]*?)<\/helmet>/)[1].replace(/@font-face\s*{[^}]*}\n?/g, '').trim();
  const markup = src.slice(src.indexOf('</helmet>') + '</helmet>'.length, src.indexOf('</x-dc>')).trim();
  const script = src.match(/<script type="text\/x-dc"[^>]*>([\s\S]*?)<\/script>/)[1].trim();
  const runtime = fs.readFileSync(RUNTIME_PATH, 'utf8').trim();
  const rel = path.relative(path.dirname(outFile), srcFile).split(path.sep).join('/');
  return [
    '<!doctype html>',
    '<html lang="ko">',
    '<head>',
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
    `<title>${titleOf(src)}</title>`,
    `<!-- 생성 파일: ${rel}을 고친 뒤 bio-interactive/scripts/build.cjs로 다시 만드세요. -->`,
    `<link rel="stylesheet" href="${FONT_CSS}">`,
    helmet,
    '</head>',
    '<body>',
    '<div id="dc-root"></div>',
    '<template id="dc-template">',
    markup,
    '</template>',
    '<script>',
    runtime,
    script,
    'mountDC(Component);',
    '</script>',
    '</body>',
    '</html>',
    '',
  ].join('\n');
}

// Manifest for publishing the source folder as a Design canvas later.
function canvasJson(title) {
  return JSON.stringify({
    v: 3,
    createdOnFiles: { v: 1, at: new Date().toISOString() },
    title,
    launch: { view: 'focused', file: 'Main.dc.html' },
    pages: [],
    boards: { 'Main.dc.html': { x: 0, y: 0, w: 1440, h: 900, title, expand: 'fill', is_interactive: true } },
    order: ['Main.dc.html'],
    notes: {},
    designSystems: [],
  });
}

if (require.main === module) {
  const [srcFile, outFile] = process.argv.slice(2).map((p) => path.resolve(p));
  if (!srcFile || !outFile) {
    console.error('usage: node build.cjs <Main.dc.html> <out.html>');
    process.exit(2);
  }
  fs.writeFileSync(outFile, build(srcFile, outFile));
  const manifest = path.join(path.dirname(srcFile), 'canvas.json');
  if (!fs.existsSync(manifest)) fs.writeFileSync(manifest, canvasJson(titleOf(fs.readFileSync(srcFile, 'utf8'))));
  console.log('wrote ' + outFile);
}

module.exports = { build, canvasJson, titleOf, FONT_CSS };
