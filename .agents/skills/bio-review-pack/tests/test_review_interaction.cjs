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
