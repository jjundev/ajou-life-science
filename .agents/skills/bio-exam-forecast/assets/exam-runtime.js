(() => {
  'use strict';
  const models = JSON.parse(document.getElementById('exam-model').textContent);
  const fold = JSON.parse(document.getElementById('exam-casefold').textContent);
  const summary = document.getElementById('summary');
  const normalize = (s, sensitive) => { const n = s.normalize('NFC').trim(); return sensitive ? n : Array.from(n).map(c => fold[c] ?? c.toLowerCase()).join(''); };
  let submitted = false, current = null;
  const aid = document.getElementById('exam-aid');
  const empty = document.querySelector('#panel-right .panel-empty');
  const valueOf = (card, model) => model.format === 'mcq' ? (card.querySelector('input:checked')?.value || '') : card.querySelector('input[type=text]').value;
  function progress() {
    let answered = 0;
    for (const [id, model] of Object.entries(models)) {
      const done = Boolean(valueOf(document.getElementById(id), model).trim());
      answered += Number(done);
      const link = document.querySelector('.toc-list a[href="#' + id + '"]');
      if (link) {
        let mark = link.querySelector('.toc-mark');
        if (!mark) { mark = document.createElement('span'); mark.className = 'toc-mark'; mark.setAttribute('aria-hidden', 'true'); link.append(mark); }
        mark.classList.toggle('is-done', done);
        mark.innerHTML = done ? '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.8 2.8L16 10"/></svg>' : '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/></svg>';
        link.setAttribute('aria-label', link.querySelector('.toc-title').textContent + (done ? ' · 응답함' : ' · 미응답'));
      }
    }
    document.getElementById('progress-n').textContent = answered;
    document.getElementById('progress-total').textContent = Object.keys(models).length;
    document.getElementById('progress-bar').style.transform = 'scaleX(' + answered / Object.keys(models).length + ')';
  }
  function showAid() {
    aid.replaceChildren();
    const card = current && document.getElementById(current);
    const show = submitted && Boolean(card);
    empty.hidden = show;
    empty.textContent = submitted ? '문제를 선택하면 정답과 풀이가 여기에 나옵니다.' : '전체 제출 후 현재 문제의 정답과 풀이를 확인할 수 있습니다.';
    const title = document.getElementById('aid-for');
    title.hidden = !card;
    title.textContent = card ? card.querySelector('h3').textContent : '';
    if (!show) return;
    const result = card.querySelector('.result').cloneNode(true);
    const solution = card.querySelector('.solution').cloneNode(true);
    solution.hidden = false;
    aid.append(result, solution);
    const data = JSON.parse(card.querySelector('.provenance').textContent);
    const details = document.createElement('details');
    details.className = 'provenance';
    const heading = document.createElement('summary'); heading.textContent = '출처 보기'; details.append(heading);
    const list = document.createElement('ul');
    for (const ref of data.refs) { const item = document.createElement('li'); item.textContent = ref.path + ' · ' + ref.locator; list.append(item); }
    details.append(list); aid.append(details);
    document.querySelector('#panel-right .panel-inner').scrollTop = 0;
  }
  document.addEventListener('od:screen', ({detail}) => {
    current = detail.screen.matches('article.card') ? detail.screen.id : null;
    progress(); showAid();
    document.querySelector('.toc-list a[aria-current="true"]')?.scrollIntoView({block:'nearest'});
  });
  document.querySelector('main').addEventListener('input', progress);
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
    submitted = true;
    document.querySelectorAll('.exam-input input').forEach(n => { n.disabled = true; });
    showAid();
    summary.textContent = `객관식 정답 ${correct}/55 · 단답형 자동 일치 ${matched} · 자기채점 대기 ${pending} · 미응답 ${blank}`;
  });
  document.getElementById('reset-exam').addEventListener('click', () => {
    submitted = false;
    document.querySelectorAll('input').forEach(n => { n.disabled = false; if (n.type === 'radio') n.checked = false; else n.value = ''; });
    document.querySelectorAll('.solution,.provenance').forEach(n => { n.hidden = true; });
    document.querySelectorAll('.result').forEach(n => { n.textContent = ''; }); summary.textContent = ''; progress(); showAid();
  });
  if (window.renderMathInElement) window.renderMathInElement(document.querySelector('main'), {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],ignoredTags:['script','noscript','style','textarea','pre','code','input'],throwOnError:false});
})();
