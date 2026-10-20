(function (scope) {
  'use strict';
  const GROUPS = [
    ['incorrect', '오답'],
    ['unsure', '애매함 표시(맞혔지만 확신 없음)'],
    ['pending', '자기채점 대기'],
    ['unanswered', '미응답'],
    ['ambiguous', '출제 모호'],
  ];
  const KIND = {review:'복습문제', exam:'시험 예상문제'};
  const GROUP_RULE = '2. 다시 볼 문항을 개념별로 묶고, 반복되거나 선행 개념인 묶음부터 다뤄.';
  const DEEP_RULE = '2. 오답·애매함·미응답 문항이 없어. 아래 맞힌 문항이 다룬 개념을 조건을 바꾼 변형 질문으로 하나씩 확인해서, 실제로 이해했는지 찍었는지 가려 줘.';

  function countBy(items) {
    const counts = {correct:0, unsure:0, incorrect:0, unanswered:0, ambiguous:0, pending:0};
    items.forEach(item => {counts[item.status] = (counts[item.status] || 0) + 1;});
    return counts;
  }
  function summaryLine(items) {
    const c = countBy(items);
    let line = `- 문항 ${items.length}개 · 응답 ${items.length - c.unanswered} · 정답 ${c.correct + c.unsure}(그중 애매함 ${c.unsure})` +
      ` · 오답 ${c.incorrect} · 미응답 ${c.unanswered}`;
    if (c.pending) line += ` · 자기채점 대기 ${c.pending}`;
    if (c.ambiguous) line += ` · 출제 모호 ${c.ambiguous}`;
    return line;
  }
  function answerLine(item) {
    if (item.format === 'short') {
      const mine = item.selected == null ? '없음' : `"${item.selected}"`;
      const accepted = item.accepted && item.accepted.length ? ` (허용: ${item.accepted.join(', ')})` : '';
      return `내 답: ${mine} / 정답: ${item.answer}${accepted}`;
    }
    const mine = item.selected == null ? '없음' : `[${item.selected}]`;
    return `내 답: ${mine} / 정답: [${item.answer}]`;
  }
  function itemBlock(item) {
    const lines = [`#### ${item.id}. ${item.title}`, `문제: ${item.stem}`];
    if (item.format !== 'short' && item.options && item.options.length) {
      lines.push('보기:');
      item.options.forEach(opt => lines.push(`- [${opt.id}] ${opt.text}`));
    }
    lines.push(answerLine(item));
    if (item.explanations && item.explanations.length) {
      lines.push('해설:');
      item.explanations.forEach(e => lines.push(e.label ? `- ${e.label}: ${e.text}` : `- ${e.text}`));
    }
    return lines.join('\n');
  }
  function buildReviewPrompt(record) {
    const items = record.items || [];
    const range = record.range;
    const review = items.filter(item => item.status !== 'correct');
    const correct = items.filter(item => item.status === 'correct');
    const out = [
      '# 생명과학 복기 요청',
      '',
      `너는 내 생명과학 튜터야. 아래는 내가 방금 푼 ${KIND[record.kind] || KIND.review}(${range})의 풀이 기록이야. 이 기록을 출발점으로 내 약한 개념을 찾아 대화로 보완 학습을 진행해 줘.`,
      '',
      '## 진행 규칙',
      '1. 먼저 기록에서 보이는 핵심 진단을 짧게 공유해. 확인된 사실(내 선택, 정답)과 네 가설을 구분하고, 정답률만으로 이해도를 단정하지 마.',
      review.length ? GROUP_RULE : DEEP_RULE,
      '3. 한 번에 한 개념만 겨냥한 질문을 하나씩 내. 보기는 숫자로 달고, "모르겠다"와 "답은 골랐지만 찍었거나 확신이 없다"를 별도 숫자 보기로 넣어. 나는 숫자만 답해도 돼.',
      '4. 원래 문항을 그대로 다시 묻지 말고, 조건이나 비교 대상을 한 가지만 바꾼 새 질문으로 확인해.',
      '5. 내가 틀리거나 확신이 없으면 맞는 부분과 잘못 연결한 부분을 짚고, 표현을 바꾼 재확인 질문을 한 번 더 내. 설명을 본 뒤 맞힌 것은 "코칭 후 이해"로 기록하고 원래 알던 것으로 치지 마.',
      `6. "출제 모호" 문항은 내 오개념의 증거로 쓰지 마. 해설은 진단 근거로만 쓰고, 이 범위(${range}) 수업 밖 내용으로 넓히지 마.`,
      '7. "자기채점 대기" 단답형은 먼저 내 답이 정답·허용답과 같은 뜻인지 판정해 줘.',
      '8. 모든 묶음을 다루거나 내가 그만하자고 하면 다음 다섯 항목으로 정리해 줘: 내가 어려웠던 부분 / 코칭한 부분 / 학습한 부분 / 아직 어려운 부분 / 복습해야 할 부분.',
      '',
      '## 기록 요약',
      `- 자료: ${record.documentId}`,
      summaryLine(items),
      '',
    ];
    if (review.length) {
      out.push('## 다시 볼 문항', '');
      GROUPS.forEach(([status, title]) => {
        const group = review.filter(item => item.status === status);
        if (!group.length) return;
        out.push(`### ${title}`, '');
        group.forEach(item => out.push(itemBlock(item), ''));
      });
    }
    if (correct.length) {
      out.push('## 확신 있게 맞힌 문항');
      correct.forEach(item => out.push(`- ${item.id}. ${item.title}`));
      out.push('');
    }
    out.push('준비됐으면 핵심 진단부터 공유하고 첫 질문을 내 줘.');
    return out.join('\n') + '\n';
  }

  function problemText(problemEl) {
    const clone = problemEl.cloneNode(true);
    clone.querySelectorAll('.choices').forEach(node => node.remove());
    // KaTeX may already have rendered; restore its TeX source instead of MathML + glyph text.
    clone.querySelectorAll('.katex').forEach(node => {
      const tex = node.querySelector('annotation[encoding="application/x-tex"]');
      if (!tex) return;
      const fence = node.closest('.katex-display') ? '$$' : '$';
      node.replaceWith(clone.ownerDocument.createTextNode(fence + tex.textContent.trim() + fence));
    });
    clone.querySelectorAll('img').forEach(img => {
      img.replaceWith(clone.ownerDocument.createTextNode(` [그림: ${img.getAttribute('alt') || ''}] `));
    });
    return clone.textContent.replace(/\s+/g, ' ').trim();
  }

  function execCopy(win, text) {
    const doc = win.document;
    const area = doc.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.top = '0';
    area.style.left = '-9999px';
    area.style.opacity = '0';
    doc.body.append(area);
    try {
      area.select();
      return doc.execCommand('copy') === true;
    } catch (_) {
      return false;
    } finally {
      area.remove();
    }
  }
  async function copyText(win, text) {
    const clipboard = win.navigator && win.navigator.clipboard;
    if (clipboard && typeof clipboard.writeText === 'function') {
      try {
        await clipboard.writeText(text);
        return true;
      } catch (_) {}
    }
    return execCopy(win, text);
  }

  const DIALOG_CSS = `
.review-prompt-dialog{width:min(44rem,calc(100vw - 2rem));max-height:calc(100vh - 2rem);padding:1rem 1.1rem;border:1px solid #c9ccd3;border-radius:10px;background:#fff;color:#1d2330;box-shadow:0 12px 36px rgba(0,0,0,.18)}
.review-prompt-dialog::backdrop{background:rgba(15,20,30,.45)}
.review-prompt-dialog h2{margin:0 0 .35rem;font-size:1.05rem}
.review-prompt-dialog p{margin:0 0 .6rem;font-size:.9rem;color:#4a5263}
.review-prompt-dialog textarea{display:block;box-sizing:border-box;width:100%;height:min(55vh,28rem);padding:.6rem;border:1px solid #c9ccd3;border-radius:6px;font:13px/1.5 ui-monospace,Consolas,monospace;resize:vertical}
.review-prompt-dialog .review-prompt-actions{display:flex;justify-content:flex-end;margin-top:.7rem}
.review-prompt-dialog button{padding:.4rem 1rem;border:1px solid #c9ccd3;border-radius:6px;background:#f4f5f7;color:inherit;font:inherit;cursor:pointer}
@media (prefers-color-scheme:dark){.review-prompt-dialog{background:#1e222b;color:#e6e8ee;border-color:#3a404d}.review-prompt-dialog p{color:#aab1c0}.review-prompt-dialog textarea{background:#14171d;color:#e6e8ee;border-color:#3a404d}.review-prompt-dialog button{background:#2a2f3a;border-color:#3a404d}}
`;
  function openPromptDialog(doc, text) {
    if (!doc.getElementById('review-prompt-style')) {
      const style = doc.createElement('style');
      style.id = 'review-prompt-style';
      style.textContent = DIALOG_CSS;
      doc.head.append(style);
    }
    let dialog = doc.querySelector('dialog.review-prompt-dialog');
    if (!dialog) {
      dialog = doc.createElement('dialog');
      dialog.className = 'review-prompt-dialog';
      dialog.setAttribute('aria-labelledby', 'review-prompt-title');
      const title = doc.createElement('h2');
      title.id = 'review-prompt-title';
      title.textContent = '복기 프롬프트';
      const note = doc.createElement('p');
      note.textContent = 'Ctrl+C(⌘C)로 복사해 AI 채팅에 붙여 넣으세요.';
      const area = doc.createElement('textarea');
      area.readOnly = true;
      area.setAttribute('aria-label', '복기 프롬프트');
      const actions = doc.createElement('div');
      actions.className = 'review-prompt-actions';
      const close = doc.createElement('button');
      close.type = 'button';
      close.textContent = '닫기';
      close.addEventListener('click', () => dialog.close());
      actions.append(close);
      dialog.append(title, note, area, actions);
      doc.body.append(dialog);
    }
    const area = dialog.querySelector('textarea');
    area.value = text;
    if (!dialog.open) dialog.showModal();
    area.focus();
    area.select();
    return dialog;
  }

  const api = {buildReviewPrompt, problemText, copyText, openPromptDialog};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else scope.ReviewPrompt = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
