(() => {
  'use strict';
  const models = JSON.parse(document.getElementById('exam-model').textContent);
  const fold = JSON.parse(document.getElementById('exam-casefold').textContent);
  const summary = document.getElementById('summary');
  const normalize = (s, sensitive) => { const n = s.normalize('NFC').trim(); return sensitive ? n : Array.from(n).map(c => fold[c] ?? c.toLowerCase()).join(''); };
  document.getElementById('submit-exam').addEventListener('click', () => {
    let correct = 0, matched = 0, pending = 0, blank = 0;
    for (const [id, model] of Object.entries(models)) {
      const card = document.getElementById(id), answer = model.answer;
      const input = model.format === 'mcq' ? card.querySelector('input:checked') : card.querySelector('input[type=text]');
      const value = input ? input.value : '';
      let result;
      if (!value.trim()) { blank++; result = '미응답'; }
      else if (model.format === 'mcq') { const ok = value === answer.option_id; correct += Number(ok); result = ok ? '정답' : '오답'; }
      else {
        const ok = [answer.canonical, ...answer.accepted].some(x => normalize(x, answer.case_sensitive) === normalize(value, answer.case_sensitive));
        matched += Number(ok); pending += Number(!ok); result = ok ? '자동 일치' : '자기채점 대기';
      }
      card.querySelector('.result').textContent = result;
      card.querySelectorAll('.solution,.provenance').forEach(n => { n.hidden = false; });
    }
    summary.textContent = `객관식 정답 ${correct}/55 · 단답형 자동 일치 ${matched} · 자기채점 대기 ${pending} · 미응답 ${blank}`;
  });
  document.getElementById('reset-exam').addEventListener('click', () => {
    document.querySelectorAll('input').forEach(n => { if (n.type === 'radio') n.checked = false; else n.value = ''; });
    document.querySelectorAll('.solution,.provenance').forEach(n => { n.hidden = true; });
    document.querySelectorAll('.result').forEach(n => { n.textContent = ''; }); summary.textContent = '';
  });
  if (window.renderMathInElement) window.renderMathInElement(document.querySelector('main'), {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],ignoredTags:['script','noscript','style','textarea','pre','code','input'],throwOnError:false});
})();
