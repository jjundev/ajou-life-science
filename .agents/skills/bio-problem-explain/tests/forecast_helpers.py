"""Synthetic forecast inputs; never writes real coursework."""
import json
from pathlib import Path


def forecast_source_file(repo: Path, chapter: int = 4, version: int = 5) -> Path:
    folder = repo / '웹과제예상' / f'{chapter}장'
    src = folder / 'src' / f'v{version}'
    (src / 'cards').mkdir(parents=True, exist_ok=True)
    note = repo / '복습노트/0922/정리노트_0922_Test.html'
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text('<html><body><section id="s1-concept">개념</section></body></html>')
    cards = []
    for id_ in ('o1', 'o2'):
        cards.append(f'<article class="card" id="{id_}"><h3>예상 개요</h3><p>합성 세트예요.</p></article>')
    key = {}
    for i in range(1, 16):
        answer = 'ABCDE'[(i-1) % 5]
        key[f'p{i}'] = answer
        choices = ''.join(f'<li>{letter}. 합성 보기 {letter}</li>' for letter in 'ABCDE')
        cards.append(f'<article class="card" id="p{i}" data-source="생성 예상" data-correct="{answer}">'
                     f'<h3>{i}. 합성 문제</h3><div class="problem"><p>맞는 보기는?</p><ul class="choices">{choices}</ul></div>'
                     f'<details class="solution"><summary>풀이</summary><ol class="steps"><li>조건을 확인해요.</li></ol>'
                     f'<p class="answer">정답: {answer}</p></details></article>')
    ids = ['o1', 'o2', *key]
    manifest = {'course': '생명과학', 'chapter': chapter, 'version': version,
                'note_href': '../../복습노트/0922/정리노트_0922_Test.html',
                'parts': [{'id': 'partA', 'title': '예상문제', 'short': '문제'}],
                'problems': [{'id': id_, 'part': 'partA'} for id_ in ids],
                'answer_key': key, 'exam_sources': {}, 'types_required': {}, 'forbidden': []}
    (src / 'pack.json').write_text(json.dumps(manifest, ensure_ascii=False))
    (src / 'blueprint.md').write_text('| 카드 | 정답 | 토픽 |\n|---|---|---|\n' + ''.join(f'| {id_} | {value} | 합성 |\n' for id_, value in key.items()))
    for id_, card in zip(ids, cards):
        (src / 'cards' / f'{id_}.html').write_text(card)
    path = folder / f'복습문제_{chapter}장_웹과제예상_v{version}.html'
    model = {'cards': {id_: {'answer': value, 'mode': 'single', 'options': [{'id': letter, 'index': i} for i, letter in enumerate('ABCDE')]}
                       for id_, value in key.items()}, 'skipped': ['o1', 'o2']}
    path.write_text('<html><body><section id="questions">' + ''.join(cards) + '</section>'
                    '<script id="review-interaction-model" type="application/json">' + json.dumps(model) + '</script></body></html>')
    return path


def forecast_acceptance_source(repo: Path, chapter: int = 4, version: int = 5) -> Path:
    """Buildable synthetic cards for both skill checkers, not an academic set."""
    import base64
    path = forecast_source_file(repo, chapter, version)
    src = path.parent/'src'/f'v{version}'
    manifest = json.loads((src/'pack.json').read_text())
    manifest.update(review_title='합성 연동 검증', review_intro='학술 검토가 아닌 테스트 세트예요.',
                    footer_review='합성 테스트', legacy=True)
    (src/'pack.json').write_text(json.dumps(manifest, ensure_ascii=False))
    (path.parent/'pixel.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII='))
    for i in range(1, 16):
        answer = manifest['answer_key'][f'p{i}']
        choices = ''.join(f'<li>{letter}. 보기 {i}{letter}</li>' for letter in 'ABCDE')
        diag = ''.join(f'<li>{letter}. {"맞아요" if letter == answer else "틀려요"}. 합성 판단 기준 {letter}예요.</li>' for letter in 'ABCDE')
        media = ('<svg viewBox="0 0 100 30" role="img" aria-label="합성 그림"><rect width="100" height="30" class="fig-ink"/></svg>'
                 '<table><tr><th>조건</th></tr><tr><td>합성 조건</td></tr></table><img src="pixel.png" alt="합성 픽셀">') if i == 1 else ''
        card = (f'<article class="card" id="p{i}" data-source="예상 {chapter}장 {i}" data-types="계산"><h3>P{i}. [예상] 제목 {i}</h3>'
                f'<div class="problem"><p>합성 문제 {i}에서 $1+1$의 값을 판단해요?</p><ul class="choices">{choices}</ul>{media}</div>'
                '<details class="original"><summary>원문 정보 보기</summary>기출 원문이 아닌 합성 예상문제예요.</details>'
                '<details class="hint"><summary>힌트 보기</summary>조건을 읽어요.</details>'
                f'<details class="solution"><summary>풀이 보기</summary><ol class="steps">{diag}'
                '<li>수업과의 연결: <a href="../../복습노트/0922/정리노트_0922_Test.html#s1-concept">정리노트</a></li></ol>'
                f'<p class="answer">정답: {answer}</p></details></article>')
        (src/'cards'/f'p{i}.html').write_text(card)
    return path
