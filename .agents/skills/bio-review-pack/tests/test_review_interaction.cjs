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

test('시도 저장: 애매함 표시 복원(정답만), 다시 풀기로 삭제, 구레코드는 false', () => {
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
  api.writeAttempt(storage, 'k', card, '1', true);
  assert.equal(api.readUnsure(storage, 'k', card), false);
  api.writeAttempt(storage, 'k', {...card, mode:'ambiguous'}, '1', true);
  assert.equal(api.readUnsure(storage, 'k', {...card, mode:'ambiguous'}), false);
});


const promptModel = {
  documentId: '0929.html',
  cards: {
    p1: {version:'v', mode:'single', answer:'2', options:[{id:'1', index:0, diagnostic:0}, {id:'2', index:1, diagnostic:1}]},
    p11: {version:'v', mode:'ambiguous', answer:'3', notice:'주의문',
      options:[{id:'1', index:0, diagnostic:0}, {id:'2', index:1, diagnostic:1}, {id:'3', index:2, diagnostic:2}]},
    p2: {version:'v', mode:'single', answer:'1', options:[{id:'1', index:0, diagnostic:0}, {id:'2', index:1, diagnostic:1}]}
  }
};
function texts(id, n) {
  const options = Array.from({length:n}, (_, i) => ({id:String(i + 1), text:`${id} 보기${i + 1}`}));
  const diagnostics = Object.fromEntries(options.map(o => [o.id, `${id} 이유${o.id}`]));
  return {title:`${id} 제목`, stem:`${id} 문제`, options, diagnostics, extras:[`수업과의 연결: ${id}`]};
}
const promptTexts = {p1:texts('p1', 2), p11:texts('p11', 3), p2:texts('p2', 2)};
const promptIds = ['p1', 'p11', 'p2'];

test('프롬프트 record: 상태·해설 규칙', () => {
  const record = api.buildPromptRecord(promptModel, promptTexts, promptIds, {p1:'1', p11:'1'}, {}, '0929');
  assert.equal(record.kind, 'review');
  assert.equal(record.documentId, '0929.html');
  assert.equal(record.range, '0929');
  const [p1, p11, p2] = record.items;
  assert.deepEqual(record.items.map(i => i.id), promptIds);
  assert.equal(p1.status, 'incorrect');
  assert.equal(p1.format, 'mcq');
  assert.equal(p1.title, 'p1 제목');
  assert.equal(p1.stem, 'p1 문제');
  assert.equal(p1.selected, '1');
  assert.equal(p1.answer, '2');
  assert.deepEqual(p1.options, promptTexts.p1.options);
  assert.deepEqual(p1.explanations.map(e => e.label), ['내 선택 [1]', '정답 [2]', '']);
  assert.deepEqual(p1.explanations.map(e => e.text), ['p1 이유1', 'p1 이유2', '수업과의 연결: p1']);
  assert.equal(p11.status, 'ambiguous');
  const labels = p11.explanations.map(e => e.label);
  assert.ok(labels.includes('내 선택 [1]'));
  assert.ok(labels.includes('출제 의도상 답 [3]'));
  assert.deepEqual(p11.explanations.find(e => e.label === '출제 주의'), {label:'출제 주의', text:'주의문'});
  assert.equal(p2.status, 'unanswered');
  assert.equal(p2.selected, null);
  assert.deepEqual(p2.explanations.map(e => e.label), ['정답 [1]', '']);
});

test('프롬프트 record: 정답+애매함은 unsure, 같은 보기는 해설 하나', () => {
  const record = api.buildPromptRecord(promptModel, promptTexts, ['p1'], {p1:'2'}, {p1:true}, '0929');
  const [p1] = record.items;
  assert.equal(p1.status, 'unsure');
  assert.deepEqual(p1.explanations.filter(e => e.label !== ''), [{label:'정답 [2]', text:'p1 이유2'}]);
  const plain = api.buildPromptRecord(promptModel, promptTexts, ['p1'], {p1:'2'}, {}, '0929');
  assert.equal(plain.items[0].status, 'correct');
});

test('API에 JSON 내보내기 함수가 없다', () => {
  assert.ok(['saveExport','buildExport','exportFilename','resolveExportDir','handleStore','updateSnapshot'].every(k => !(k in api)));
  assert.equal(typeof api.captureCardText, 'function');
});

test('단답형은 입력 확인 전 미응답, 일치 또는 자기채점 대기', () => {
  const short = {format:'short',answer:{canonical:'Aa',accepted:['대립유전자'],case_sensitive:true}};
  assert.equal(api.grade(short,undefined), null);
  assert.equal(api.grade(short,' '), null);
  assert.equal(api.grade(short,' Aa '), 'correct');
  assert.equal(api.grade(short,'대립유전자'), 'correct');
  assert.equal(api.grade(short,'aa'), 'pending');
  assert.equal(api.grade({...short,answer:{...short.answer,case_sensitive:false}},'aa'), 'correct');
  const record = api.buildPromptRecord({cards:{p1:short}}, {p1:{title:'단답',stem:'발문',extras:['풀이 근거']}}, ['p1'], {p1:'Aa'}, {}, '시험범위');
  assert.equal(record.items[0].format, 'short');
  assert.equal(record.items[0].answer, 'Aa');
  assert.equal(record.items[0].status, 'correct');
  assert.equal(record.items[0].explanations[0].text, '풀이 근거');
});
