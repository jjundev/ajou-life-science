# 브라우저 검증 (메인 에이전트)

## 서버
file:// 미리보기에서는 스크립트가 돌지 않는다. 빈 포트로 서버를 띄운다. 셸 상태는 Bash 호출 사이에 이어지지 않으므로 포트 번호를 먼저 출력해 두고, 이후 명령과 URL에는 그 숫자를 직접 쓴다.
1. 빈 포트 찾기(출력된 숫자가 `<port>`):
   ```bash
   python3 -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[1])"
   ```
2. 서버 띄우기: Bash 도구의 `run_in_background: true`로 실행한다(명령 끝에 `&`를 붙이지 않는다).
   ```bash
   python3 -m http.server <port> --directory "<RUN>/repo"
   ```
3. URL: `http://localhost:<port>/복습노트/<range>/<파일명>` (한글 그대로).
4. 끝나면 서버를 종료한다: 그 백그라운드 작업을 멈추거나(TaskStop 등), `pkill -f "http.server <port>"`.

## 측정 전 준비
브라우저 창이 숨겨져 있으면 `document.documentElement.clientWidth`가 0이 되어 `hScroll`이 거짓 양성으로 나온다. 측정 전에 `resize_window`로 크기를 명시하고(`width: 1280`, `height: 900`) `document.documentElement.clientWidth > 0`을 확인한다. `.katex-mathml` 안 요소는 화면에 보이지 않으므로 넘침 원인으로 치지 않는다. 스크롤 직후 스크린샷은 늦게 반영될 수 있으니 1초쯤 기다린 뒤 찍는다.

## 가로 넘침 측정 (두 페이지 공통)
템플릿은 `body`를 고정하고 본문을 `.content` 안에서 스크롤하며, 한 번에 한 화면(토픽·카드)만 보여 준다. 그래서 `document.documentElement.scrollWidth`로는 넘침이 잡히지 않는다. 아래 `overflowScreens`로 화면을 하나씩 넘기며 `.content`를 잰다. 결과는 넘친 화면 id 목록이고, 비어 있어야 통과다. 목록이 나오면 그 화면에서 `.content`의 오른쪽 끝을 넘는 요소를 찾아 원인을 확인한다(`.katex-display`·`.table-wrap` 안의 자체 가로 스크롤은 넘침이 아니다).
```js
async function overflowScreens() {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const scroller = document.querySelector('.content') || document.documentElement;
  const screens = Array.from(document.querySelectorAll('main .screen'));
  const over = [];
  for (const s of screens.length ? screens : [document.querySelector('main')]) {
    if (screens.length) { location.hash = s.id ? '#' + s.id : ''; await wait(150); }
    // 넘어올 때의 translateX(24px) 애니메이션이 넘침으로 잡히지 않게 끝낸다(숨은 창에서는 애니메이션이 멈춰 있다)
    document.getAnimations().forEach((a) => a.finish());
    if (scroller.scrollWidth > scroller.clientWidth + 1 || document.documentElement.scrollWidth > window.innerWidth + 1) over.push(s.id || 'hero');
  }
  location.hash = '';
  await wait(150);
  return over;
}
```

## 정리노트 (`mcp__Claude_Browser__javascript_tool`)
위 `overflowScreens` 정의를 같은 실행에 붙여 넣는다.
```js
await new Promise((r) => setTimeout(r, 1500));
const textNodes = Array.from(document.querySelectorAll('main *, #panel-right *')).filter((e) => !['SCRIPT', 'STYLE'].includes(e.tagName) && !e.closest('[hidden]'));
({
  katex: document.querySelectorAll('.katex').length,
  katexErrors: document.querySelectorAll('.katex-error').length,
  rawDollar: textNodes.some((e) => Array.from(e.childNodes).some((n) => n.nodeType === 3 && n.textContent.includes('$'))),
  sumsInPanel: document.querySelectorAll('#panel-right .sum').length,
  sumsLeftInMain: document.querySelectorAll('main .sum').length,
  hScroll: await overflowScreens(),
  widgets: Array.from(document.querySelectorAll('.widget')).map((w) => ({ id: w.id, drawn: Array.from(w.querySelectorAll('svg')).some((s) => !s.closest('[hidden]') && s.childElementCount > 0) })),
})
```
통과: `katexErrors: 0`, `rawDollar: false`, `sumsInPanel`이 manifest에서 `layers`가 빈 목록이 아닌 토픽 수, `sumsLeftInMain: 0`, `hScroll: []`, 모든 위젯 `drawn: true`. `read_console_messages`에 오류 없음.

개념 토픽 하나로 넘겨(`location.hash = '#<토픽 id>'`) 오른쪽 "페이지 요약" 패널에 그 토픽의 요약이 보이는지 스크린샷으로 확인한다(1280px 이상에서는 패널이 기본으로 열린다).

위젯마다 그 토픽으로 넘긴 뒤 슬라이더 하나를 바꾸고(`input` 이벤트) readout 값이 `.widget-static` 표의 같은 설정 값과 같은지 확인한다.

## 모바일·다크
`resize_window`(`preset: "mobile"`, `colorScheme: "dark"`) → 새로고침 → `clientWidth > 0` 확인 → 위 스크립트 재실행(`hScroll: []`) → 스크린샷으로 그림·위젯 글자가 보이는지 확인 → 상단 바의 테마 버튼(`#theme-toggle`)을 눌러 `document.body` 배경색이 바뀌고 `aria-label`이 반대 모드로 바뀌는지 확인한 뒤 `localStorage.removeItem('od-theme')`로 지운다 → `preset: "desktop"`, `colorScheme: "light"`로 되돌린다.

## 복습문제
### 선택·채점 필수 확인

- 추가 해설이 있는 문항은 중앙에 짧은 판정만 표시되고, 긴 추가 설명은 오른쪽 패널에 한 번만 표시되는지 확인한다.

- 보기 선택 전 해설이 숨겨지고, 정답을 선택하면 한 개, 오답을 선택하면 내 선택과 정답 두 개의 해설만 펼쳐지는지 확인한다.
- 선택 전·후 어느 때도 “해설이 열려요” 같은 사용법 안내 문장(`.review-help`)이 카드에 없어야 한다.
- ‘틀린 것을 고르시오’는 문장의 참·거짓과 답 여부를 혼동하지 않는다. 모호한 기출은 ‘단일 정답 판정 주의’와 출제 의도상 답을 표시한다.
- 제출 뒤 각 보기를 클릭하면 그 해설만 접거나 펼치고 답은 바꾸지 않는다. Enter/Space로도 동작하며 aria-expanded와 실제 표시가 일치해야 한다. 다시 풀기는 해설·선택·완료 표시를 초기화하고 첫 보기로 포커스를 돌린다.
- 새로고침·화면 이동 뒤 선택이 유지된다(`sessionStorage`). 탭을 닫고 새 탭에서 다시 열면 푼 흔적이 없다(`localStorage`에 `od-review-*` 키가 없어야 한다).
- 마지막 문제 화면에서만 **JSON 내보내기** 버튼이 보인다. 클릭하면 `.assets/풀이기록` 폴더에 저장하고(처음 한 번만 폴더 선택창, 이후엔 기억한 폴더에 바로 저장, 관계없는 폴더면 저장 없이 안내, 취소하면 저장 없음, 폴더 API가 거부되면 다운로드), 파일에는 모든 문제가 문서 순서로 들어 있고 안 푼 문제는 `selected: null`이다. 저장소가 막혀도 내보내기가 된다. 정답을 고른 뒤에만 풀이 패널에 **애매함으로 표시** 버튼이 보이고(오답·출제 모호 문항에서는 숨김), 누르면 토스트와 함께 스냅샷·JSON의 `unsure`에 반영되며 뒤로가기엔 남고 다시 풀기로 지워진다(`result: "ambiguous"`와 별개). 저장 차단·잘못된 저장값은 풀이를 막지 않는다.
- Tab/Enter/Space, 390px/1280px, 밝은/어두운 테마, 비JavaScript 정적 풀이, 인쇄 해설을 확인한다.
- 그림·수식 노드 수와 id가 늘어나지 않는다. 인쇄가 끝나면 추가 해설이 오른쪽 패널로 돌아간다.
- 회귀 검사는 `python .agents/skills/bio-review-pack/tests/browser_check_review.py`로 실행한다(개발 환경의 Playwright/Chromium 필요, 생성 HTML에는 추가 의존성 없음).

측정 전에 다시 `resize_window`(`width: 1280`, `height: 900`) → `clientWidth > 0` 확인(앞 단계의 `preset: "desktop"`은 창 크기를 창 자체 크기로 되돌려 숨은 창에서는 0이 될 수 있다). 이번에도 `overflowScreens` 정의를 붙여 넣는다.
```js
await new Promise((r) => setTimeout(r, 1500));
document.querySelectorAll('details').forEach((d) => { d.open = true; });
await new Promise((r) => setTimeout(r, 300));
({
  cards: document.querySelectorAll('article.card').length,
  aidGroups: document.querySelectorAll('#panel-right .aid').length,
  katexErrors: document.querySelectorAll('.katex-error').length,
  brokenImgs: Array.from(document.querySelectorAll('article.card img')).filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.getAttribute('src')),
  hScroll: await overflowScreens(),
})
```
통과: `cards`와 `aidGroups`가 모두 manifest 문제 수, `katexErrors: 0`, `brokenImgs: []`, `hScroll: []`. 첫 카드로 넘겨 오른쪽 "풀이 도움" 패널에 그 카드의 원문·힌트·풀이가 보이는지, 상단 "정리노트" 링크가 노트로 이동하는지 확인한다.

## 마무리
모든 검사가 끝나면 `resize_window`(`preset: "desktop"`, `colorScheme: "light"`)로 되돌리고 서버를 종료한다(위 "서버" 4).
