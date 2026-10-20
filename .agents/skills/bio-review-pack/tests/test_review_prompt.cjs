const test = require('node:test');
const assert = require('node:assert/strict');
const api = require('../assets/review-prompt.js');

const options = [{id:'1', text:'가'}, {id:'2', text:'나'}];
function mcq(id, status, selected, extra = {}) {
  return {id, title:`제목${id.slice(1)}`, stem:`문제${id.slice(1)}`, format:'mcq', options, selected,
    answer:'2', accepted:null, status, explanations:[], ...extra};
}
const items = [
  mcq('p1', 'incorrect', '1', {explanations:[
    {label:'내 선택 [1]', text:'이유1'}, {label:'정답 [2]', text:'이유2'}, {label:'', text:'수업과의 연결: 연결'}]}),
  mcq('p2', 'unsure', '2'),
  mcq('p3', 'unanswered', null),
  mcq('p4', 'correct', '2'),
];
const record = {kind:'review', documentId:'0929.html', range:'0929', items};

test('상태별 묶음 순서와 빈 묶음 생략', () => {
  const out = api.buildReviewPrompt(record);
  const a = out.indexOf('### 오답'), b = out.indexOf('### 애매함 표시(맞혔지만 확신 없음)'), c = out.indexOf('### 미응답');
  assert.ok(a > 0 && a < b && b < c);
  assert.ok(!out.includes('### 자기채점 대기'));
  assert.ok(!out.includes('### 출제 모호'));
  const tail = out.slice(out.indexOf('## 확신 있게 맞힌 문항'));
  assert.ok(tail.includes('- p4. 제목4'));
  assert.ok(!out.includes('#### p4.'));
  assert.ok(!out.includes('문제4'));
});

test('요약 줄', () => {
  const out = api.buildReviewPrompt(record);
  assert.ok(out.includes('- 자료: 0929.html'));
  assert.ok(out.includes('- 문항 4개 · 응답 3 · 정답 2(그중 애매함 1) · 오답 1 · 미응답 1\n'));
  assert.ok(!out.includes('자기채점 대기 0'));
  assert.ok(!out.includes('출제 모호 0'));
  const more = api.buildReviewPrompt({...record, items:[...items, mcq('p5', 'ambiguous', '1'),
    {...mcq('p6', 'pending', 'x'), format:'short', options:null, answer:'y'}]});
  assert.ok(more.includes('- 문항 6개 · 응답 5 · 정답 2(그중 애매함 1) · 오답 1 · 미응답 1 · 자기채점 대기 1 · 출제 모호 1\n'));
});

test('객관식 문항 본문', () => {
  const out = api.buildReviewPrompt(record);
  assert.ok(out.includes('#### p1. 제목1\n문제: 문제1\n보기:\n- [1] 가\n- [2] 나\n내 답: [1] / 정답: [2]\n해설:\n'));
  assert.ok(out.includes('- 내 선택 [1]: 이유1\n- 정답 [2]: 이유2\n- 수업과의 연결: 연결\n'));
  assert.ok(out.includes('#### p3. 제목3\n문제: 문제3\n보기:\n- [1] 가\n- [2] 나\n내 답: 없음 / 정답: [2]\n'));
});

test('단답형과 미응답', () => {
  const short = {id:'q1', title:'단답', stem:'단위는?', format:'short', options:null, selected:'Aa',
    answer:'뉴클레오타이드', accepted:['뉴클레오티드', 'nucleotide'], status:'pending', explanations:[]};
  const out = api.buildReviewPrompt({kind:'exam', documentId:'e.html', range:'1장-6장', items:[short]});
  assert.ok(out.includes('#### q1. 단답\n문제: 단위는?\n내 답: "Aa" / 정답: 뉴클레오타이드 (허용: 뉴클레오티드, nucleotide)\n'));
  assert.ok(!out.includes('보기:'));
  const none = api.buildReviewPrompt({kind:'exam', documentId:'e.html', range:'1장-6장',
    items:[{...short, selected:null, status:'unanswered', accepted:[]}]});
  assert.ok(none.includes('내 답: 없음 / 정답: 뉴클레오타이드\n'));
});

test('다시 볼 문항이 없으면 심화 모드', () => {
  const out = api.buildReviewPrompt({...record, items:[mcq('p4', 'correct', '2')]});
  assert.ok(!out.includes('## 다시 볼 문항'));
  assert.ok(out.includes('2. 오답·애매함·미응답 문항이 없어. 아래 맞힌 문항이 다룬 개념을 조건을 바꾼 변형 질문으로 하나씩 확인해서, 실제로 이해했는지 찍었는지 가려 줘.\n'));
  assert.ok(!out.includes('2. 다시 볼 문항을 개념별로 묶고'));
});

test('입력 원문 보존', () => {
  const raw = '  <script>x</script>  ';
  const out = api.buildReviewPrompt({...record, items:[{...mcq('p1', 'pending', raw), format:'short', options:null}]});
  assert.ok(out.includes(`내 답: "${raw}"`));
});

test('kind와 범위 표기', () => {
  assert.ok(api.buildReviewPrompt({...record, kind:'exam', range:'1장-6장'}).includes('방금 푼 시험 예상문제(1장-6장)의 풀이 기록'));
  const out = api.buildReviewPrompt(record);
  assert.ok(out.startsWith('# 생명과학 복기 요청\n\n너는 내 생명과학 튜터야. 아래는 내가 방금 푼 복습문제(0929)의 풀이 기록이야.'));
  assert.ok(out.includes('이 범위(0929) 수업 밖 내용으로 넓히지 마.'));
  assert.equal(out.trimEnd().split('\n').pop(), '준비됐으면 핵심 진단부터 공유하고 첫 질문을 내 줘.');
});

function fakeWin({clipboard, exec}) {
  const appended = [];
  const doc = {
    body:{append(node){appended.push(node); node.parentNode = doc.body;}},
    createElement(){return {style:{}, setAttribute(){}, select(){this.selected = true;}, remove(){this.removed = true;}};},
    execCommand(cmd){if (cmd !== 'copy') return false; if (exec instanceof Error) throw exec; return exec;},
  };
  return {win:{navigator:clipboard === undefined ? {} : {clipboard}, document:doc}, appended};
}

test('copyText: clipboard 성공, 실패 시 execCommand, 둘 다 실패면 false', async () => {
  let written = null;
  const ok = fakeWin({clipboard:{writeText:async t => {written = t;}}, exec:false});
  assert.equal(await api.copyText(ok.win, 'hi'), true);
  assert.equal(written, 'hi');
  assert.equal(ok.appended.length, 0);

  const fallback = fakeWin({clipboard:{writeText:async () => {throw Error('denied');}}, exec:true});
  assert.equal(await api.copyText(fallback.win, 'hi'), true);
  assert.equal(fallback.appended[0].value, 'hi');
  assert.ok(fallback.appended[0].removed);

  const noApi = fakeWin({exec:true});
  assert.equal(await api.copyText(noApi.win, 'hi'), true);

  const fail = fakeWin({clipboard:{writeText:async () => {throw Error('denied');}}, exec:Error('blocked')});
  assert.equal(await api.copyText(fail.win, 'hi'), false);
  const falseExec = fakeWin({exec:false});
  assert.equal(await api.copyText(falseExec.win, 'hi'), false);
});
