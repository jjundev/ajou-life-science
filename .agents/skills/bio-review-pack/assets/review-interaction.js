(function (scope) {
  'use strict';
  function stripDiagnosticPrefix(text, id) {
    const match = text.match(/^\s*(?:\((\d+)\)|([A-Z])[.)])\s*/);
    return match && (match[1] || match[2]) === id ? text.slice(match[0].length) : text;
  }
  function scrollAnswerIntoView(scroller, selectedLi, answerLi, selectedButton, answerButton) {
    if (!scroller || !selectedLi.getClientRects().length) return;
    const viewport = scroller.getBoundingClientRect();
    const height = scroller.clientHeight;
    const margin = 16;
    const span = (a, b) => {
      const x = a.getBoundingClientRect(), y = b.getBoundingClientRect();
      return {top:Math.min(x.top, y.top), bottom:Math.max(x.bottom, y.bottom)};
    };
    let target = span(selectedLi, answerLi);
    if (target.bottom - target.top > height - 2 * margin)
      target = span(selectedButton, answerButton);
    if (target.bottom - target.top > height - 2 * margin)
      target = span(selectedButton, selectedButton);
    scroller.scrollTop += (target.top + target.bottom - viewport.top - viewport.bottom) / 2;
  }
  function grade(card, selected) {
    if (!card.options.some(o => o.id === selected)) return null;
    if (card.mode === 'ambiguous') return 'ambiguous';
    return selected === card.answer ? 'correct' : 'incorrect';
  }
  function storageKey(documentId, cardId) {
    return 'od-review-attempt:v1:' + encodeURIComponent(documentId) + ':' + encodeURIComponent(cardId);
  }
  function readAttempt(storage, key, card) {
    try {
      const value = JSON.parse(storage.getItem(key));
      return value && value.version === card.version && grade(card, value.selected) !== null ? value.selected : null;
    } catch { return null; }
  }
  function writeAttempt(storage, key, card, selected) {
    try {
      if (selected === null) storage.removeItem(key);
      else storage.setItem(key, JSON.stringify({version:card.version, selected}));
    } catch {}
  }
  function exportKey(documentId) {
    return 'od-review-export:v1:' + encodeURIComponent(documentId);
  }
  function readSnapshot(storage, key) {
    const empty = () => ({schema:1, cards:{}});
    try {
      const value = JSON.parse(storage.getItem(key));
      return value && value.schema === 1 && value.cards && typeof value.cards === 'object' && !Array.isArray(value.cards)
        ? value : empty();
    } catch { return empty(); }
  }
  function writeSnapshot(storage, key, snapshot) {
    try { storage.setItem(key, JSON.stringify(snapshot)); } catch {}
  }
  function updateSnapshot(snapshot, selectedById, ids, now) {
    const cards = Object.assign({}, snapshot.cards);
    for (const id of ids) {
      const selected = selectedById[id] === undefined ? null : selectedById[id];
      const prev = cards[id];
      if (prev && prev.selected === selected) continue;
      cards[id] = {selected, updatedAt: selected === null ? null : now.toISOString()};
    }
    return {schema:1, cards};
  }
  function buildExport(model, snapshot, meta) {
    const counts = {correct:0, incorrect:0, ambiguous:0};
    const cards = meta.ids.map(id => {
      const data = model.cards[id];
      const entry = snapshot.cards[id] || {};
      const result = grade(data, entry.selected);
      if (result !== null) counts[result] += 1;
      return {
        id, title: meta.titles[id] || '',
        selected: result === null ? null : entry.selected,
        answer: data.answer, result,
        updatedAt: result === null ? null : (entry.updatedAt || null)
      };
    });
    const answered = counts.correct + counts.incorrect + counts.ambiguous;
    return {
      schema:1, documentId:model.documentId, range:meta.range, exportedAt:meta.now.toISOString(),
      summary:{total:cards.length, answered, unanswered:cards.length - answered,
        correct:counts.correct, incorrect:counts.incorrect, ambiguous:counts.ambiguous},
      skipped: model.skipped || [], cards
    };
  }
  function exportFilename(documentId, now) {
    const p = n => String(n).padStart(2, '0');
    const stamp = now.getFullYear() + p(now.getMonth() + 1) + p(now.getDate()) +
      '-' + p(now.getHours()) + p(now.getMinutes());
    return documentId.replace(/\.html?$/i, '') + '_풀이기록_' + stamp + '.json';
  }
  async function saveExport(win, text, filename) {
    if (typeof win.showDirectoryPicker === 'function') {
      try {
        const dir = await win.showDirectoryPicker({mode:'readwrite'});
        const file = await dir.getFileHandle(filename, {create:true});
        const out = await file.createWritable();
        await out.write(text);
        await out.close();
        return 'saved';
      } catch (error) {
        if (error && (error.name === 'AbortError' || error.name === 'NotAllowedError')) return 'cancelled';
      }
    }
    const url = win.URL.createObjectURL(new win.Blob([text], {type:'application/json'}));
    const a = win.document.createElement('a');
    a.href = url;
    a.download = filename;
    win.document.body.append(a);
    a.click();
    a.remove();
    win.setTimeout(() => win.URL.revokeObjectURL(url), 1000);
    return 'downloaded';
  }
  function mount(root, model, storage) {
    if (!model || model.schema !== 1 || !model.cards) return;
    const win = root.defaultView;
    const emit = (id, selected, result, restored = false) => root.dispatchEvent(
      new win.CustomEvent('od:answer', {detail:{id, selected, result, restored}}));
    const element = (tag, cls, text) => {
      const el = root.createElement(tag);
      el.className = cls;
      if (text !== undefined) el.textContent = text;
      return el;
    };
    const selectedById = {};
    let feedback = null;
    let feedbackTimer = null;
    let feedbackOwner = null;
    function clearFeedback(owner = null) {
      if (owner !== null && owner !== feedbackOwner) return;
      if (feedbackTimer !== null) win.clearTimeout(feedbackTimer);
      feedbackTimer = null;
      if (feedback) feedback.remove();
      feedback = null;
      feedbackOwner = null;
    }
    function showFeedback(result, id, message, duration) {
      clearFeedback();
      if (!message && result !== 'correct' && result !== 'incorrect') return;
      feedback = element('div', 'review-feedback');
      feedback.dataset.reviewFeedback = '';
      feedback.dataset.result = result;
      feedback.setAttribute('aria-hidden', 'true');
      feedback.append(
        element('span', 'review-feedback-icon'),
        element('span', 'review-feedback-text', message || (result === 'correct' ? '정답이에요' : '다시 확인해요'))
      );
      root.body.append(feedback);
      feedbackOwner = id;
      feedbackTimer = win.setTimeout(clearFeedback, duration || 1100);
    }
    for (const [id, data] of Object.entries(model.cards)) {
      const card = root.getElementById(id);
      if (!card || card.classList.contains('review-ready')) continue;
      const aid = Array.from(root.querySelectorAll('.aid')).find(n => n.dataset.cardId === id);
      const solution = (aid || card).querySelector('details.solution');
      const choices = Array.from(card.querySelectorAll('.choices > li'));
      const diagnostics = solution ? Array.from(solution.querySelectorAll('ol.steps > li')) : [];
      const options = data.options;
      // Validate every reference before moving a single original node.
      if (!solution || !Array.isArray(options) || choices.length !== options.length ||
          !options.length || !options.some(o => o.id === data.answer) ||
          new Set(options.map(o => o.index)).size !== options.length ||
          new Set(options.map(o => o.diagnostic)).size !== options.length ||
          options.some(o => !choices[o.index] || !diagnostics[o.diagnostic])) continue;
      const positions = diagnostics.map(n => ({node:n, parent:n.parentNode, next:n.nextSibling}));
      const diagnosticTexts = [];
      const choiceNodes = choices.map(n => Array.from(n.childNodes));
      const summary = solution.querySelector('summary');
      const summaryText = summary ? summary.textContent : '';
      const originalOpen = solution.open;
      const originalHidden = solution.hidden;
      let status, reset, notice;
      try {
        // Some future cards supply the caution only as metadata. Keep its full
        // explanation in the solution panel, without duplicating existing prose.
        const compact = text => text.replace(/\s+/g, '');
        if (data.mode === 'ambiguous' && data.notice &&
            !compact(solution.textContent).includes(compact(data.notice))) {
          notice = element('p', 'review-notice', data.notice);
          solution.append(notice);
        }
        const controls = options.map(o => {
          const li = choices[o.index];
          const button = element('button', 'review-choice');
          button.type = 'button';
          const complex = li.querySelector('a,button,input,select,textarea,table,div,p,figure,ul,ol');
          if (complex) {
            button.textContent = o.id + '번 선택';
            const content = element('div', 'review-choice-content');
            content.id = id + '-choice-content-' + o.index;
            content.append(...Array.from(li.childNodes));
            button.setAttribute('aria-describedby', content.id);
            li.append(button, content);
          } else {
            button.append(...Array.from(li.childNodes));
            li.append(button);
          }
          const badge = element('span', 'review-choice-label');
          badge.hidden = true;
          button.append(badge);
          button.setAttribute('aria-pressed', 'false');
          const list = element('ol', 'review-diagnostics');
          list.id = id + '-review-diagnostics-' + o.index;
          const diagnostic = diagnostics[o.diagnostic];
          const first = diagnostic.firstChild;
          if (first && first.nodeType === 3) {
            diagnosticTexts.push({node:first, text:first.textContent});
            first.textContent = stripDiagnosticPrefix(first.textContent, o.id);
          }
          diagnostic.classList.add('review-diagnostic');
          diagnostic.hidden = true;
          list.append(diagnostic);
          li.append(list);
          return {id:o.id, button, badge, diagnostic, list};
        });
        status = element('p', 'review-status');
        status.setAttribute('role', 'status');
        status.setAttribute('aria-live', 'polite');
        reset = element('button', 'review-reset text-btn', '다시 풀기');
        reset.type = 'button';
        card.querySelector('.choices').before(status);
        card.querySelector('.choices').after(reset);
        const key = storageKey(model.documentId, id);
        let selected = readAttempt(storage, key, data);
        selectedById[id] = selected;
        const expanded = new Set(selected === null ? [] : [selected, data.answer]);
        function paintDisclosure(c) {
          const answered = selected !== null;
          const open = answered && expanded.has(c.id);
          c.diagnostic.hidden = !open;
          c.list.hidden = !open;
          if (answered) {
            c.button.setAttribute('aria-expanded', String(open));
            c.button.setAttribute('aria-controls', c.list.id);
          } else {
            c.button.removeAttribute('aria-expanded');
            c.button.removeAttribute('aria-controls');
          }
        }
        function paint() {
          const answered = selected !== null;
          const result = grade(data, selected);
          reset.hidden = !answered;
          status.textContent = !answered ? '' : result === 'ambiguous'
            ? '단일 정답 판정 주의'
            : result === 'correct' ? '정답이에요.' : '정답이 아니에요. 보기별 이유를 확인해 보세요.';
          status.dataset.result = result || '';
          controls.forEach(c => {
            c.button.dataset.selected = String(c.id === selected);
            if (answered) c.button.removeAttribute('aria-pressed');
            else c.button.setAttribute('aria-pressed', 'false');
            c.button.dataset.result = !answered ? '' : c.id === data.answer
              ? (data.mode === 'ambiguous' ? 'intended' : 'correct')
              : c.id === selected ? (data.mode === 'ambiguous' ? 'uncertain' : 'selected') : '';
            c.badge.hidden = !answered;
            c.badge.textContent = !answered ? '' : [
              c.id === selected ? '내 선택' : '',
              c.id === data.answer ? (data.mode === 'ambiguous' ? '출제 의도상 답' : '정답')
                : data.mode === 'single' ? '정답 아님' : ''
            ].filter(Boolean).join(' · ');
            paintDisclosure(c);
          });
          solution.hidden = !answered;
          solution.open = answered;
          if (summary) summary.textContent = '추가 해설 · 수업과의 연결';
        }
        controls.forEach(c => c.button.addEventListener('click', () => {
          if (selected !== null) {
            if (expanded.has(c.id)) expanded.delete(c.id);
            else expanded.add(c.id);
            paintDisclosure(c);
            return;
          }
          selected = c.id;
          selectedById[id] = selected;
          expanded.add(selected);
          expanded.add(data.answer);
          writeAttempt(storage, key, data, selected);
          paint();
          emit(id, selected, grade(data, selected));
          showFeedback(grade(data, selected), id);
          const selectedOption = options.find(o => o.id === selected);
          const answerOption = options.find(o => o.id === data.answer);
          const selectedControl = controls.find(control => control.id === selected);
          const answerControl = controls.find(control => control.id === data.answer);
          win.requestAnimationFrame(() => {
            if (!card.isConnected || !card.getClientRects().length) return;
            scrollAnswerIntoView(root.querySelector('.content'),
              choices[selectedOption.index], choices[answerOption.index],
              selectedControl.button, answerControl.button);
          });
        }));
        reset.addEventListener('click', () => {
          clearFeedback(id);
          selected = null;
          selectedById[id] = null;
          expanded.clear();
          writeAttempt(storage, key, data, null);
          paint();
          emit(id, null, null);
          controls[0].button.focus();
        });
        card.classList.add('review-ready');
        solution.classList.add('review-extra');
        paint();
        if (selected !== null) emit(id, selected, grade(data, selected), true);
        else {
          try {
            if (storage.getItem(key) !== null) {
              writeAttempt(storage, key, data, null);
              emit(id, null, null, true);
            }
          } catch {}
        }
      } catch (error) {
        // Keep a readable static question if enhancement cannot be completed.
        diagnosticTexts.forEach(p => { p.node.textContent = p.text; });
        choices.forEach((li, i) => li.replaceChildren(...choiceNodes[i]));
        positions.slice().reverse().forEach(p => {
          p.node.hidden = false;
          p.node.classList.remove('review-diagnostic');
          p.parent.insertBefore(p.node, p.next);
        });
        for (const el of [status, reset, notice]) if (el) el.remove();
        solution.hidden = originalHidden;
        solution.open = originalOpen;
        if (summary) summary.textContent = summaryText;
        solution.classList.remove('review-extra');
        card.classList.remove('review-ready');
        win.console.warn('문항 상호작용을 적용하지 못했습니다:', id, error);
      }
    }
    const exportCards = Array.from(root.querySelectorAll('main article.card')).filter(el => model.cards[el.id]);
    const pager = root.querySelector('.pager');
    if (exportCards.length && pager && !pager.querySelector('.review-export-bar')) {
      const ids = exportCards.map(el => el.id);
      const titles = {};
      exportCards.forEach(el => { titles[el.id] = ((el.querySelector('h3') || {}).textContent || '').trim(); });
      const snapKey = exportKey(model.documentId);
      let snapshot = readSnapshot(storage, snapKey);
      root.addEventListener('od:leave', ({detail}) => {
        const id = detail && detail.screen && detail.screen.id;
        if (!model.cards[id]) return;
        snapshot = updateSnapshot(snapshot, selectedById, [id], new Date());
        writeSnapshot(storage, snapKey, snapshot);
      });
      const bar = element('div', 'review-export-bar');
      const button = element('button', 'btn btn-primary review-export', 'JSON 내보내기');
      button.type = 'button';
      const note = element('p', 'review-export-note sr-only');
      note.setAttribute('role', 'status');
      note.setAttribute('aria-live', 'polite');
      const helpWrap = element('div', 'review-export-help-wrap');
      const help = element('button', 'text-btn review-export-help', '?');
      help.type = 'button';
      help.setAttribute('aria-label', '저장 폴더 도움말');
      help.setAttribute('aria-expanded', 'false');
      const popup = element('div', 'review-export-popup');
      popup.id = 'review-export-popup';
      popup.setAttribute('role', 'note');
      popup.hidden = true;
      help.setAttribute('aria-controls', popup.id);
      popup.append(
        element('p', 'review-export-popup-text',
          'Chrome은 다운로드·문서·바탕 화면 같은 시스템 폴더를 막아요. 그 안에 만들어 둔 하위 폴더를 골라 주세요. ' +
          '막힌 폴더를 골랐다면 "다른 폴더 선택"을 눌러 다시 고르면 돼요.'),
        element('button', 'text-btn review-export-popup-close', '닫기'));
      popup.querySelector('button').type = 'button';
      helpWrap.append(help, popup);
      const setHelp = open => {
        popup.hidden = !open;
        help.setAttribute('aria-expanded', String(open));
      };
      help.addEventListener('click', () => setHelp(popup.hidden));
      popup.querySelector('button').addEventListener('click', () => { setHelp(false); help.focus(); });
      root.addEventListener('keydown', e => { if (e.key === 'Escape' && !popup.hidden) { setHelp(false); help.focus(); } });
      root.addEventListener('click', e => { if (!popup.hidden && !helpWrap.contains(e.target)) setHelp(false); });
      root.addEventListener('od:screen', () => setHelp(false));
      bar.append(button, helpWrap, note);
      pager.prepend(bar);
      root.addEventListener('od:screen', () => { note.textContent = ''; });
      button.addEventListener('click', async () => {
        if (button.disabled) return;
        button.disabled = true;
        const now = new Date();
        snapshot = updateSnapshot(snapshot, selectedById, ids, now);
        writeSnapshot(storage, snapKey, snapshot);
        const data = buildExport(model, snapshot, {ids, titles, range: root.body.dataset.range || '', now});
        let outcome;
        try { outcome = await saveExport(win, JSON.stringify(data, null, 2) + '\n', exportFilename(model.documentId, now)); }
        finally { button.disabled = false; }
        const message = outcome === 'saved' ? '고른 폴더에 저장했어요'
          : outcome === 'downloaded' ? '다운로드 폴더에 저장했어요' : '저장을 취소했어요';
        note.textContent = message + '.';
        showFeedback(outcome, 'export', message, 2200);
      });
    }
    // Existing page CSS hides side panels when printing. Move original details,
    // including static questions, into their cards for print, then restore them.
    if (!root.documentElement.dataset.reviewPrint) {
      root.documentElement.dataset.reviewPrint = 'ready';
      let printPositions = [];
      win.addEventListener('beforeprint', () => {
        if (printPositions.length) return;
        root.querySelectorAll('.aid[data-card-id]').forEach(aid => {
          const card = root.getElementById(aid.dataset.cardId);
          if (!card) return;
          Array.from(aid.children).forEach(node => {
            printPositions.push({node, parent:aid, open:node.open});
            if (node.tagName === 'DETAILS') node.open = true;
            card.append(node);
          });
        });
      });
      win.addEventListener('afterprint', () => {
        printPositions.forEach(p => {p.parent.append(p.node); p.node.open = p.open;});
        printPositions = [];
      });
    }
  }
  const api = {stripDiagnosticPrefix, grade, storageKey, readAttempt, writeAttempt, mount,
    exportKey, readSnapshot, writeSnapshot, updateSnapshot, buildExport, exportFilename, saveExport};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else scope.ReviewInteraction = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
