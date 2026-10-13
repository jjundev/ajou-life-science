// Builds the standalone page (opens directly in a browser) from the canvas source.
// Run after editing canvas/Main.dc.html:  node standalone/build.cjs
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(__dirname, '..');
const MAIN_PATH = path.join(ROOT, 'canvas', 'Main.dc.html');
const RUNTIME_PATH = path.join(__dirname, 'dc-runtime.js');
const OUT_PATH = path.join(ROOT, '..', '인터렉티브_03_DNA_구조와_복제_3D.html');
const FONT_CSS = 'https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.css';

function build() {
  const src = fs.readFileSync(MAIN_PATH, 'utf8');
  // Uploaded /_blob fonts only resolve inside the canvas; the page loads Pretendard from the CDN like the notes.
  const helmet = src.match(/<helmet>([\s\S]*?)<\/helmet>/)[1].replace(/@font-face\s*{[^}]*}\n?/g, '').trim();
  const markup = src.slice(src.indexOf('</helmet>') + '</helmet>'.length, src.indexOf('</x-dc>')).trim();
  const script = src.match(/<script type="text\/x-dc"[^>]*>([\s\S]*?)<\/script>/)[1].trim();
  const runtime = fs.readFileSync(RUNTIME_PATH, 'utf8').trim();
  return [
    '<!doctype html>',
    '<html lang="ko">',
    '<head>',
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
    '<title>DNA 구조와 복제 3D</title>',
    '<!-- 생성 파일: 자료_인터렉티브_03_DNA_구조와_복제_3D/canvas/Main.dc.html을 고친 뒤 standalone/build.cjs로 다시 만드세요. -->',
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

if (require.main === module) {
  fs.writeFileSync(OUT_PATH, build());
  console.log('wrote ' + path.relative(process.cwd(), OUT_PATH));
}

module.exports = { build, OUT_PATH };
