const test = require('node:test');
const assert = require('node:assert/strict');
const api = require('../assets/review-interaction.js');
const card = {version:'v1', mode:'single', answer:'2', options:[{id:'1'}, {id:'2'}]};
test('명시 정답과 모호성으로 채점', () => {
  assert.equal(api.grade(card,'1'),'incorrect');
  assert.equal(api.grade(card,'2'),'correct');
  assert.equal(api.grade(card,'X'),null);
  assert.equal(api.grade({...card,mode:'ambiguous'},'1'),'ambiguous');
});
test('손상·구버전·없는 보기 복원 금지', () => {
  for (const raw of ['{','null','[]','{"version":"old","selected":"2"}','{"version":"v1","selected":"X"}']) {
    assert.equal(api.readAttempt({getItem:()=>raw},'k',card),null);
  }
});
test('저장 차단', () => {
  const storage = {getItem(){throw Error('blocked')},setItem(){throw Error('blocked')},removeItem(){throw Error('blocked')}};
  assert.equal(api.readAttempt(storage,'k',card),null);
  assert.doesNotThrow(()=>api.writeAttempt(storage,'k',card,'2'));
  assert.doesNotThrow(()=>api.writeAttempt(storage,'k',card,null));
});
test('문서 분리', () => {
  assert.notEqual(api.storageKey('a.html','p1'),api.storageKey('b.html','p1'));
});
test('선택 저장과 초기화', () => {
  const data = new Map();
  const storage = {getItem:k=>data.get(k),setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)};
  api.writeAttempt(storage,'k',card,'2');
  assert.equal(api.readAttempt(storage,'k',card),'2');
  api.writeAttempt(storage,'k',card,null);
  assert.equal(api.readAttempt(storage,'k',card),null);
});

test('펼친 해설의 선두 식별자만 제거', () => {
  assert.equal(api.stripDiagnosticPrefix('(1) 틀려요. 보기 (2)는 맞아요.', '1'),
    '틀려요. 보기 (2)는 맞아요.');
  assert.equal(api.stripDiagnosticPrefix(' A. 맞아요.', 'A'), '맞아요.');
  assert.equal(api.stripDiagnosticPrefix('(2) 다른 보기', '1'), '(2) 다른 보기');
  assert.equal(api.stripDiagnosticPrefix('번호 없는 해설', '1'), '번호 없는 해설');
});

const model = {
  documentId: 'd.html', skipped: ['s1'],
  cards: {
    p10: {version:'v', mode:'single', answer:'2', options:[{id:'1'}, {id:'2'}]},
    p2: {version:'v', mode:'single', answer:'1', options:[{id:'1'}, {id:'2'}]},
    p3: {version:'v', mode:'ambiguous', answer:'1', options:[{id:'1'}, {id:'2'}]},
    p4: {version:'v', mode:'single', answer:'1', options:[{id:'1'}, {id:'2'}]}
  }
};
const T0 = new Date('2026-09-30T05:00:00.000Z');
const T1 = new Date('2026-09-30T05:01:00.000Z');

test('내보내기 파일 이름은 로컬 시각 기준', () => {
  assert.equal(api.exportFilename('복습문제_0929_Heredity.html', new Date(2026, 8, 30, 14, 3)),
    '복습문제_0929_Heredity_풀이기록_20260930-1403.json');
  assert.equal(api.exportFilename('a.htm', new Date(2026, 0, 2, 3, 4)), 'a_풀이기록_20260102-0304.json');
});

test('문서별 스냅샷 키', () => {
  assert.notEqual(api.exportKey('a.html'), api.exportKey('b.html'));
  assert.ok(api.exportKey('a.html').startsWith('od-review-export:v1:'));
});

test('손상·차단된 스냅샷 저장소는 빈 스냅샷', () => {
  for (const raw of ['{', 'null', '[]', '{"schema":2,"cards":{}}', '{"schema":1,"cards":[]}']) {
    assert.deepEqual(api.readSnapshot({getItem:()=>raw}, 'k'), {schema:1, cards:{}});
  }
  const blocked = {getItem(){throw Error('blocked')}, setItem(){throw Error('blocked')}};
  assert.deepEqual(api.readSnapshot(blocked, 'k'), {schema:1, cards:{}});
  assert.deepEqual(api.readSnapshot(null, 'k'), {schema:1, cards:{}});
  assert.doesNotThrow(() => api.writeSnapshot(blocked, 'k', {schema:1, cards:{}}));
  assert.doesNotThrow(() => api.writeSnapshot(null, 'k', {schema:1, cards:{}}));
});

test('스냅샷 저장과 복원', () => {
  const data = new Map();
  const storage = {getItem:k=>data.get(k), setItem:(k,v)=>data.set(k,v)};
  const snap = api.updateSnapshot({schema:1, cards:{}}, {p2:'1'}, ['p2'], T0);
  api.writeSnapshot(storage, 'k', snap);
  assert.deepEqual(api.readSnapshot(storage, 'k'), snap);
});

test('스냅샷 갱신: 같은 답은 시각 유지, 바뀌면 새 시각, 초기화하면 null', () => {
  let snap = api.updateSnapshot({schema:1, cards:{}}, {p2:'1'}, ['p2'], T0);
  assert.deepEqual(snap.cards.p2, {selected:'1', unsure:false, updatedAt:T0.toISOString()});
  snap = api.updateSnapshot(snap, {p2:'1'}, ['p2'], T1);
  assert.equal(snap.cards.p2.updatedAt, T0.toISOString());
  snap = api.updateSnapshot(snap, {p2:'2'}, ['p2'], T1);
  assert.deepEqual(snap.cards.p2, {selected:'2', unsure:false, updatedAt:T1.toISOString()});
  snap = api.updateSnapshot(snap, {p2:null}, ['p2'], T1);
  assert.deepEqual(snap.cards.p2, {selected:null, unsure:false, updatedAt:null});
  const before = {schema:1, cards:{}};
  api.updateSnapshot(before, {p2:'1'}, ['p2'], T0);
  assert.deepEqual(before, {schema:1, cards:{}}, '입력 스냅샷은 바꾸지 않는다');
});

test('스냅샷 갱신: selectedById에 없는 문항은 안 푼 것', () => {
  const snap = api.updateSnapshot({schema:1, cards:{}}, {}, ['p2'], T0);
  assert.deepEqual(snap.cards.p2, {selected:null, unsure:false, updatedAt:null});
});

test('내보내기: DOM 순서·안 푼 문제 null·요약', () => {
  let snap = {schema:1, cards:{}};
  snap = api.updateSnapshot(snap, {p2:'1', p10:'1', p3:'2'}, ['p2', 'p10', 'p3', 'p4'], T0);
  const out = api.buildExport(model, snap, {
    ids:['p2', 'p3', 'p4', 'p10'],
    titles:{p2:'둘째', p3:'셋째', p4:'넷째', p10:'열째'},
    range:'0929', now:T1
  });
  assert.equal(out.schema, 1);
  assert.equal(out.documentId, 'd.html');
  assert.equal(out.range, '0929');
  assert.equal(out.exportedAt, T1.toISOString());
  assert.deepEqual(out.skipped, ['s1']);
  assert.deepEqual(out.cards.map(c => c.id), ['p2', 'p3', 'p4', 'p10']);
  assert.deepEqual(out.cards[0], {id:'p2', title:'둘째', selected:'1', answer:'1', result:'correct', unsure:false, updatedAt:T0.toISOString()});
  assert.equal(out.cards[1].result, 'ambiguous');
  assert.deepEqual(out.cards[2], {id:'p4', title:'넷째', selected:null, answer:'1', result:null, unsure:false, updatedAt:null});
  assert.equal(out.cards[3].result, 'incorrect');
  assert.deepEqual(out.summary, {total:4, answered:3, unanswered:1, correct:1, incorrect:1, ambiguous:1, unsure:0});
});

test('내보내기: 스냅샷의 없는 보기·누락 항목은 안 푼 것', () => {
  const snap = {schema:1, cards:{p2:{selected:'X', updatedAt:T0.toISOString()}}};
  const out = api.buildExport(model, snap, {ids:['p2', 'p4'], titles:{}, range:'', now:T1});
  assert.equal(out.cards[0].selected, null);
  assert.equal(out.cards[0].updatedAt, null);
  assert.equal(out.cards[0].title, '');
  assert.equal(out.summary.answered, 0);
  assert.equal(out.summary.unanswered, 2);
});

test('애매함 표시: 바뀌면 새 시각, 안 푼 문제는 항상 false', () => {
  let snap = api.updateSnapshot({schema:1, cards:{}}, {p2:'1'}, ['p2'], T0, {p2:true});
  assert.deepEqual(snap.cards.p2, {selected:'1', unsure:true, updatedAt:T0.toISOString()});
  snap = api.updateSnapshot(snap, {p2:'1'}, ['p2'], T1, {p2:true});
  assert.equal(snap.cards.p2.updatedAt, T0.toISOString());
  snap = api.updateSnapshot(snap, {p2:'1'}, ['p2'], T1, {p2:false});
  assert.deepEqual(snap.cards.p2, {selected:'1', unsure:false, updatedAt:T1.toISOString()});
  snap = api.updateSnapshot(snap, {p2:null}, ['p2'], T1, {p2:true});
  assert.deepEqual(snap.cards.p2, {selected:null, unsure:false, updatedAt:null});
});

test('내보내기: 카드별 unsure와 요약, 옛 스냅샷은 false, 출제 모호와 별개', () => {
  const snap = {schema:1, cards:{
    p2:{selected:'1', unsure:true, updatedAt:T0.toISOString()},
    p3:{selected:'2', unsure:true, updatedAt:T0.toISOString()},
    p10:{selected:'1', updatedAt:T0.toISOString()},
    p4:{selected:null, unsure:true, updatedAt:null}}};
  const out = api.buildExport(model, snap, {ids:['p2', 'p3', 'p4', 'p10'], titles:{}, range:'', now:T1});
  assert.deepEqual(out.cards.map(c => c.unsure), [true, true, false, false]);
  assert.equal(out.cards[1].result, 'ambiguous');
  assert.equal(out.summary.unsure, 2);
});

test('시도 저장: 애매함 표시 복원, 다시 풀기로 삭제, 구레코드는 false', () => {
  const data = new Map();
  const storage = {getItem:k=>data.get(k), setItem:(k,v)=>data.set(k,v), removeItem:k=>data.delete(k)};
  api.writeAttempt(storage, 'k', card, '2', true);
  assert.equal(api.readAttempt(storage, 'k', card), '2');
  assert.equal(api.readUnsure(storage, 'k', card), true);
  api.writeAttempt(storage, 'k', card, '2');
  assert.equal(api.readUnsure(storage, 'k', card), false);
  api.writeAttempt(storage, 'k', card, '2', true);
  api.writeAttempt(storage, 'k', card, null, true);
  assert.equal(api.readUnsure(storage, 'k', card), false);
  assert.equal(api.readUnsure({getItem:()=>'{"version":"v1","selected":"2"}'}, 'k', card), false);
  assert.equal(api.readUnsure({getItem(){throw Error('x')}}, 'k', card), false);
});

function fakeWin(picker) {
  const log = {clicks:0, appended:0};
  const anchor = {click(){log.clicks++}, remove(){}};
  const win = {
    URL:{createObjectURL:() => 'blob:x', revokeObjectURL(){}},
    Blob: class { constructor(parts){ this.parts = parts; } },
    setTimeout: () => 0,
    document:{createElement:() => anchor, body:{append(){log.appended++}}}
  };
  if (picker) win.showDirectoryPicker = picker;
  return {win, log, anchor};
}

test('폴더 선택창으로 저장', async () => {
  const written = {};
  const picker = async () => ({
    async getFileHandle(name, opts) {
      written.name = name; written.opts = opts;
      return {async createWritable() { return {async write(t){ written.text = t; }, async close(){ written.closed = true; }}; }};
    }
  });
  const {win, log} = fakeWin(picker);
  assert.equal(await api.saveExport(win, '{"a":1}', 'f.json'), 'saved');
  assert.deepEqual(written, {name:'f.json', opts:{create:true}, text:'{"a":1}', closed:true});
  assert.equal(log.clicks, 0);
});

test('선택창 취소는 아무것도 저장하지 않음', async () => {
  const picker = async () => { const e = new Error('cancel'); e.name = 'AbortError'; throw e; };
  const {win, log} = fakeWin(picker);
  assert.equal(await api.saveExport(win, '{}', 'f.json'), 'cancelled');
  assert.equal(log.clicks, 0);
});

test('폴더 API 거부·미지원이면 다운로드로 대체', async () => {
  const denied = async () => { const e = new Error('no'); e.name = 'SecurityError'; throw e; };
  for (const picker of [denied, undefined]) {
    const {win, log, anchor} = fakeWin(picker);
    assert.equal(await api.saveExport(win, '{}', 'f.json'), 'downloaded');
    assert.equal(log.clicks, 1);
    assert.equal(anchor.download, 'f.json');
  }
});

test('권한 거부(NotAllowedError)는 취소로 처리하고 다운로드하지 않음', async () => {
  const picker = async () => { const e = new Error('picker active'); e.name = 'NotAllowedError'; throw e; };
  const {win, log} = fakeWin(picker);
  assert.equal(await api.saveExport(win, '{}', 'f.json'), 'cancelled');
  assert.equal(log.clicks, 0);
});
