(() => {
  'use strict';
  // Original question numbers are presentation metadata; keep source/model bytes intact.
  document.querySelectorAll('article.card > .problem').forEach(problem => {
    const paragraph = problem.querySelector('p');
    if (!paragraph) return;
    const walker = document.createTreeWalker(paragraph, NodeFilter.SHOW_TEXT);
    let text;
    while ((text = walker.nextNode()) && !text.textContent.trim()) {}
    if (text) text.textContent = text.textContent.replace(/^\s*(?:\d{1,3}[.)]|\(\d{1,3}\))\s+/, '');
  });
  // Capture prompt text before KaTeX rewrites the math.
  const prompt = window.ReviewPrompt;
  const texts = {};
  document.querySelectorAll('main article.card').forEach(card => {
    const problem = card.querySelector('.problem');
    texts[card.id] = {
      // The prompt already prints the card id, so drop the "p1." label from the heading.
      title: (card.querySelector('h3')?.textContent || '').replace(/\s+/g, ' ').trim().replace(/^p\d+\.\s*/i, ''),
      stem: problem ? (prompt ? prompt.problemText(problem) : problem.textContent.replace(/\s+/g, ' ').trim()) : '',
      options: Array.from(card.querySelectorAll('.exam-input label')).filter(label => label.querySelector('input[type=radio]'))
        .map(label => ({id: label.querySelector('input').value, text: label.textContent.replace(/\s+/g, ' ').trim().replace(/^[A-Z]\.\s*/, '')})),
      explanations: Array.from(card.querySelectorAll('.solution ol.steps > li'))
        .map(li => ({label: '풀이', text: li.textContent.replace(/\s+/g, ' ').trim()}))
    };
  });
  const models = JSON.parse(document.getElementById('exam-model').textContent);
  const fold = JSON.parse(document.getElementById('exam-casefold').textContent);
  const summary = document.getElementById('summary');
  const normalize = (s, sensitive) => { const n = s.normalize('NFC').trim(); return sensitive ? n : Array.from(n).map(c => fold[c] ?? c.toLowerCase()).join(''); };
  let submitted = false, current = null, attempt = null;
  const meta = JSON.parse(document.getElementById('exam-meta').textContent);
  const presentation = document.getElementById('presentation-meta');
  const mode = presentation ? JSON.parse(presentation.textContent) : {mode:'exam'};
  const practice = mode.mode === 'practice';
  document.querySelectorAll('.exam-input input').forEach(input => {
    input.autocomplete = 'off'; input.disabled = false;
    if (input.type === 'radio') input.checked = false;
    else input.value = '';
  });
  if (presentation) Object.assign(meta, {documentId:mode.documentId, mode:mode.mode, questionSetHash:mode.questionSetHash});
  const checked = new Set();
  const results = document.getElementById('exam-results');
  const filter = document.getElementById('results-filter');
  const labels = {correct:'정답', incorrect:'오답', matched:'자동 일치', pending:'자기채점 대기', unanswered:'미응답'};
  function resultRoute() {
    const active = submitted && location.hash === '#exam-results';
    document.body.classList.toggle('exam-results', active);
    results.hidden = !active;
    syncControls(); showAid();
    if (active) {
      const toggle = document.getElementById('toggle-right');
      if (matchMedia('(min-width: 1024px)').matches && toggle.getAttribute('aria-expanded') !== 'true') toggle.click();
      document.getElementById('results-title').focus({preventScroll:true});
      document.querySelector('.content').scrollTop = 0;
    }
  }
  function syncControls() {
    const button = document.getElementById('submit-exam');
    const ids = Object.keys(models);
    button.hidden = practice || (!submitted && current !== ids[ids.length - 1]);
    document.body.classList.toggle('exam-last-unsubmitted', !practice && !submitted && current === ids[ids.length - 1]);
    const explanation = document.getElementById('open-explanation');
    if (explanation) explanation.hidden = !practice && !submitted;
    const tools = document.querySelector('.presentation-links');
    if (tools) tools.hidden = !practice && !submitted;
  }
  function openResults() {
    if (location.hash === '#exam-results') resultRoute();
    else location.hash = 'exam-results';
  }
  window.addEventListener('hashchange', resultRoute);
  window.addEventListener('popstate', resultRoute);
  // The shared question pager must not consume arrow keys on the results screen.
  document.addEventListener('keydown', e => {
    if (document.body.classList.contains('exam-results') && ['ArrowLeft','ArrowRight'].includes(e.key)) e.preventDefault();
  }, true);
  // Keep result-screen swipes from reaching the shared question pager.
  document.addEventListener('touchend', e => {
    if (document.body.classList.contains('exam-results') && results.contains(e.target)) e.stopPropagation();
  }, {capture:true, passive:true});
  function filterResults() {
    let shown = 0;
    results.querySelectorAll('.exam-result-row').forEach(row => {
      row.hidden = filter.value !== 'all' && row.dataset.result !== filter.value;
      shown += Number(!row.hidden);
    });
    document.getElementById('results-count').textContent = `${shown} / ${attempt.cards.length}문항`;
    document.getElementById('results-empty').hidden = shown !== 0;
  }
  filter.addEventListener('change', filterResults);
  function renderResults() {
    const {summary:s} = attempt;
    const percent = s.mcq.total ? Math.round(s.mcq.correct / s.mcq.total * 100) : 0;
    const text = `객관식 정답 ${s.mcq.correct}/${s.mcq.total} · 정답률 ${percent}% · 단답형 자동 일치 ${s.short.matched} · 자기채점 대기 ${s.short.pending} · 미응답 ${s.unanswered}`;
    summary.textContent = text;
    document.getElementById('results-summary').textContent = text;
    const list = document.getElementById('results-list'); list.replaceChildren();
    for (const card of attempt.cards) {
      const row = document.createElement('li'); row.className = 'exam-result-row'; row.dataset.result = card.result;
      const heading = document.createElement('h3'); heading.textContent = card.id + ' · ' + (card.format === 'mcq' ? '객관식' : '단답형');
      const status = document.createElement('p'); status.className = 'exam-result-status'; status.textContent = labels[card.result];
      const dl = document.createElement('dl');
      const fields = [['내 답', card.selected === null ? '미응답' : card.selected],
        ['정답', card.format === 'mcq' ? card.answer.option_id : card.answer.canonical]];
      if (card.format === 'short') fields.push(['허용답', card.answer.accepted.join(', ') || '없음']);
      for (const [name,value] of fields) {
        const dt = document.createElement('dt'); dt.textContent = name;
        const dd = document.createElement('dd'); dd.textContent = value; dl.append(dt, dd);
      }
      const link = document.createElement('a'); link.href = '#' + card.id; link.textContent = '문제·해설 보기';
      link.setAttribute('aria-label', card.id + ' 문제·해설 보기');
      link.addEventListener('click', () => {
        const toggle = document.getElementById('toggle-right');
        if (toggle.getAttribute('aria-expanded') !== 'true') toggle.click();
      });
      row.append(heading, status, dl, link); list.append(row);
    }
    filter.value = 'all'; filterResults();
  }
  const promptStatus = {matched: 'correct', correct: 'correct', incorrect: 'incorrect', pending: 'pending', unanswered: 'unanswered'};
  const copyButton = document.getElementById('copy-prompt');
  copyButton.addEventListener('click', async () => {
    if (!attempt || !prompt || copyButton.disabled) return;
    const status = document.getElementById('prompt-status');
    copyButton.disabled = true;
    try {
      const items = attempt.cards.map(card => {
        const t = texts[card.id] || {title: '', stem: '', options: [], explanations: []};
        const mcq = card.format === 'mcq';
        return {id: card.id, title: t.title, stem: t.stem, format: mcq ? 'mcq' : 'short',
          options: mcq ? t.options : null, selected: card.selected,
          answer: mcq ? card.answer.option_id : card.answer.canonical,
          accepted: mcq ? null : card.answer.accepted.filter(x => x !== card.answer.canonical),
          status: promptStatus[card.result], explanations: t.explanations};
      });
      const text = prompt.buildReviewPrompt({kind: 'exam', documentId: meta.documentId, range: meta.range, items});
      if (await prompt.copyText(window, text)) status.textContent = '복기 프롬프트를 복사했어요. AI 채팅에 붙여 넣으세요.';
      else {
        prompt.openPromptDialog(document, text);
        status.textContent = '자동 복사가 막혀 있어요. 열린 창에서 직접 복사해 주세요.';
      }
    } finally { copyButton.disabled = false; }
  });
  const aid = document.getElementById('exam-aid');
  const empty = document.querySelector('#panel-right .panel-empty');
  const valueOf = (card, model) => model.format === 'mcq' ? (card.querySelector('input:checked')?.value || '') : card.querySelector('input[type=text]').value;
  const tocIcons = {
    empty: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/></svg>',
    done: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.8 2.8L16 10"/></svg>',
    incorrect: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9 9l6 6m0-6-6 6"/></svg>',
    pending: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.88 2.08C12.5 12.15 12 12.75 12 14m0 2.25h.01"/></svg>'
  };
  function progress() {
    const results = new Map(attempt?.cards.map(card => [card.id, card.result]));
    let answered = 0;
    for (const [id, model] of Object.entries(models)) {
      const value = valueOf(document.getElementById(id), model);
      const done = Boolean(value.trim());
      const result = results.get(id) ?? (practice && checked.has(id) ? gradeValue(value, model) : null);
      answered += Number(done);
      const link = document.querySelector('.toc-list a[href="#' + id + '"]');
      if (link) {
        let mark = link.querySelector('.toc-mark');
        if (!mark) { mark = document.createElement('span'); mark.className = 'toc-mark'; mark.setAttribute('aria-hidden', 'true'); link.append(mark); }
        const icon = tocIcons[result] ?? (done ? tocIcons.done : tocIcons.empty);
        mark.classList.toggle('is-done', icon === tocIcons.done);
        mark.dataset.result = result ?? '';
        mark.innerHTML = icon;
        const label = labels[result] ?? (done ? '응답함' : '미응답');
        link.setAttribute('aria-label', link.querySelector('.toc-title').textContent + ' · ' + label);
      }
    }
    document.getElementById('progress-n').textContent = answered;
    document.getElementById('progress-total').textContent = Object.keys(models).length;
    document.getElementById('progress-bar').style.transform = 'scaleX(' + answered / Object.keys(models).length + ')';
  }
  function showAid() {
    aid.replaceChildren();
    const isResults = submitted && location.hash === '#exam-results';
    document.getElementById('panel-right-title').textContent = isResults ? '채점표' : '풀이 도움';
    document.querySelector('#toggle-right span').textContent = isResults ? '채점표' : '풀이';
    if (isResults) {
      empty.hidden = true;
      const legend = document.createElement('p'); legend.className = 'scorecard-legend';
      legend.textContent = '○ 정답·자동 일치 · × 오답 · ? 자기채점 대기 · — 미응답';
      const table = document.createElement('table'); table.id = 'exam-scorecard';
      const caption = document.createElement('caption'); caption.textContent = '전체 문항 채점표'; table.append(caption);
      const tbody = document.createElement('tbody');
      const symbols = {correct:'○', incorrect:'×', matched:'○', pending:'?', unanswered:'—'};
      let row;
      attempt.cards.forEach((card, i) => {
        if (i % 5 === 0) { row = document.createElement('tr'); tbody.append(row); }
        const cell = document.createElement('td');
        const link = document.createElement('a'); link.href = '#' + card.id; link.dataset.result = card.result;
        link.textContent = `${i + 1} ${symbols[card.result]}`;
        link.setAttribute('aria-label', `${i + 1}번 · ${labels[card.result]} · 문제와 해설 보기`);
        cell.append(link); row.append(cell);
      });
      table.append(tbody); aid.append(legend, table);
      return;
    }
    const card = current && document.getElementById(current);
    const show = Boolean(card) && (practice ? checked.has(card.id) : submitted);
    empty.hidden = show;
    empty.textContent = practice ? '답을 확인하면 현재 문제의 정답과 풀이가 나옵니다.' : submitted ? '문제를 선택하면 정답과 풀이가 여기에 나옵니다.' : '전체 제출 후 현재 문제의 정답과 풀이를 확인할 수 있습니다.';
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
    progress(); syncControls(); showAid();
    document.querySelector('.toc-list a[aria-current="true"]')?.scrollIntoView({block:'nearest'});
  });
  function gradeValue(value, model) {
    if (!value.trim()) return 'unanswered';
    const answer = model.answer;
    if (model.format === 'mcq') return value === answer.option_id ? 'correct' : 'incorrect';
    return [answer.canonical, ...answer.accepted].some(x => normalize(x, answer.case_sensitive) === normalize(value, answer.case_sensitive)) ? 'matched' : 'pending';
  }
  function checkPractice(card) {
    const value = valueOf(card, models[card.id]);
    if (!value.trim()) return;
    submitted = false; attempt = null; summary.textContent = '';
    checked.add(card.id);
    card.querySelector('.result').textContent = labels[gradeValue(value, models[card.id])];
    card.querySelectorAll('.solution,.provenance').forEach(n => { n.hidden = false; });
    progress(); showAid(); syncControls();
    const toggle = document.getElementById('toggle-right');
    if (toggle.getAttribute('aria-expanded') !== 'true') toggle.click();
  }
  if (practice) {
    for (const [id, model] of Object.entries(models)) {
      if (model.format !== 'short') continue;
      const card = document.getElementById(id), button = document.createElement('button');
      button.className = 'btn check-answer'; button.type = 'button'; button.textContent = '답 확인';
      card.querySelector('.exam-input').append(button);
      button.addEventListener('click', () => checkPractice(card));
    }
    const resultsButton = document.createElement('button');
    resultsButton.className = 'text-btn'; resultsButton.type = 'button'; resultsButton.id = 'practice-results'; resultsButton.textContent = '학습 결과 보기';
    document.querySelector('.presentation-links').append(resultsButton);
    resultsButton.addEventListener('click', () => document.getElementById('submit-exam').click());
  }
  document.querySelector('main').addEventListener('input', e => {
    if (practice && e.target.matches('.exam-input input')) {
      submitted = false; attempt = null;
      const card = e.target.closest('article.card'); checked.delete(card.id);
      card.querySelector('.result').textContent = '';
      card.querySelectorAll('.solution,.provenance').forEach(n => { n.hidden = true; });
      summary.textContent = ''; showAid(); syncControls();
    }
    progress();
  });
  document.querySelector('main').addEventListener('change', e => {
    if (submitted || !e.target.matches('.exam-input input[type=radio]:checked')) return;
    const card = e.target.closest('article.card');
    if (practice) { checkPractice(card); return; }
    const ids = Object.keys(models);
    if (card.id !== current || ids.indexOf(current) === ids.length - 1) return;
    document.getElementById('pager-next').click();
    const heading = document.getElementById(current)?.querySelector('h3');
    if (heading) { heading.tabIndex = -1; heading.focus({preventScroll:true}); }
  });
  document.getElementById('submit-exam').addEventListener('click', () => {
    if (submitted) { openResults(); return; }
    if (!practice && current !== Object.keys(models).at(-1)) return;
    const cards = Object.entries(models).map(([id, model]) => {
      const card = document.getElementById(id), answer = model.answer;
      const value = practice && !checked.has(id) ? '' : valueOf(card, model);
      const result = gradeValue(value, model);
      card.querySelector('.result').textContent = labels[result];
      card.querySelectorAll('.solution,.provenance').forEach(n => { n.hidden = practice && !checked.has(id); });
      return {id, format:model.format, selected:value.trim() ? value : null, answer, result};
    });
    const count = (format, result) => cards.filter(c => c.format === format && (!result || c.result === result)).length;
    const unanswered = cards.filter(c => c.result === 'unanswered').length;
    attempt = {schema:'bio-exam-attempt', schemaVersion:1, ...meta,
      attemptId:window.crypto?.randomUUID ? window.crypto.randomUUID() : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2),
      submittedAt:new Date().toISOString(),
      summary:{total:cards.length, answered:cards.length-unanswered, unanswered,
        mcq:{total:count('mcq'), correct:count('mcq','correct'), incorrect:count('mcq','incorrect'), unanswered:count('mcq','unanswered')},
        short:{total:count('short'), matched:count('short','matched'), pending:count('short','pending'), unanswered:count('short','unanswered')}}, cards};
    submitted = true;
    if (!practice) document.querySelectorAll('.exam-input input').forEach(n => { n.disabled = true; });
    document.getElementById('submit-exam').textContent = '전체 결과';
    progress(); renderResults(); showAid(); openResults();

  });
  function resetExam() {
    if ((submitted || checked.size) && !window.confirm('답안과 결과를 초기화하고 다시 풀까요? 복기하려면 먼저 복기 프롬프트를 복사하세요.')) return;
    submitted = false; attempt = null; checked.clear();
    document.querySelectorAll('.exam-input input').forEach(n => { n.disabled = false; if (n.type === 'radio') n.checked = false; else n.value = ''; });
    document.querySelectorAll('.solution,.provenance').forEach(n => { n.hidden = true; });
    document.querySelectorAll('.result').forEach(n => { n.textContent = ''; });
    summary.textContent = ''; document.getElementById('results-list').replaceChildren();
    document.getElementById('results-summary').textContent = '';
    document.getElementById('prompt-status').textContent = '';
    document.getElementById('submit-exam').textContent = '전체 제출';
    progress(); showAid(); resultRoute();
    location.hash = 'p1';
  }
  document.getElementById('reset-exam').addEventListener('click', resetExam);
  if (window.renderMathInElement) window.renderMathInElement(document.querySelector('main'), {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],ignoredTags:['script','noscript','style','textarea','pre','code','input'],throwOnError:false});
})();
