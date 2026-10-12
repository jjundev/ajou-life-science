from pathlib import Path
from mpe_types import Problem, SourcePack

def problem():
    return Problem('p1', 1, '행렬', 'HW1 Problem 1', '<p>Find (a), (b).</p>',
                   '<p>$A=1$</p>', '<ol><li>(a) $A$</li><li>(b) $A^2$</li></ol>',
                   (), ('계산',), '1', ('a', 'b'))

def fragment(p=None):
    p = p or problem()
    parts = ''.join(f'<div data-subpart="{key}"><p>첫 식에서 계산하고 대입해 확인해요. $1=1$</p></div>' for key in p.subparts)
    return ('<div class="layer eli5" data-explanation="understand"><p>구할 것을 읽어요.</p></div>'
            '<div class="layer formal" data-explanation="recall">'
            '<h4>이 문제를 봤을 때 떠올릴 개념과 공식</h4>'
            '<p>제곱을 구하라는 단서에서 같은 수의 곱을 떠올려요. '
            '$A^2=A\\cdot A$이며 A는 주어진 스칼라예요.</p></div>'
            '<div class="layer formal" data-explanation="start"><p>$A=1$부터 써요.</p></div>'
            f'<div class="layer formal" data-explanation="solve">{parts}</div>'
            f'<div class="layer formal" data-explanation="verify">{parts}</div>'
            '<div class="layer warn" data-explanation="pitfall"><p>행과 열을 바꾸지 않아요.</p></div>'
            '<div class="layer formal" data-explanation="retry"><ul><li>다시 계산해요.</li></ul></div>'
            '<div class="sum" hidden><p>시작·판단·검산</p></div>')

def pack(path=Path('복습문제_0917_Recursion.html')):
    return SourcePack('review', '0917', 'Recursion', path, '0'*64, (problem(),))

def approved(pack, fragments, artifacts=None):
    from mpe_contract import payload_hash
    from mpe_render import artifact_hashes
    base = {'status': 'pass', 'reviewer': 'test fixture', 'evidence': 'fixture calculation at evidence.txt'}
    keys = [f'{p.id}:{s}' for p in pack.problems for s in p.subparts]
    result = {'input_hash': payload_hash(pack, fragments),
              'source_visual': dict(base), 'browser': dict(base),
              'content': {**base, 'items': {k: dict(base) for k in keys}},
              'independent': {**base, 'items': {k: {**base, 'method': 'exact', 'conclusion': '1=1'} for k in keys}},
              'references': []}
    if artifacts:
        result['artifact_hashes'] = artifact_hashes(artifacts)
    return result


def source_file(repo, date='0917', slug='Recursion', empty=False):
    path=repo / '복습노트' / date / f'복습문제_{date}_{slug}.html'
    path.parent.mkdir(parents=True,exist_ok=True)
    card = '' if empty else ('''<article class="card" id="p1" data-source="1001 기출">
<h3>1. 재귀 함수</h3><div class="problem"><p>함수 결과를 구해요.</p><pre><code>printf("$%d", n);</code></pre></div>
<details class="original"><summary>원문</summary><blockquote>원래 질문</blockquote></details>
<details class="hint"><summary>힌트</summary><p>반복을 세어요.</p></details>
<details class="solution"><summary>풀이</summary><ol class="steps"><li>값을 확인해요.</li></ol><p class="answer">1</p></details></article>''')
    path.write_text('<section id="questions">'+card+'</section>',encoding='utf-8')
    return path

def acceptance_pack(repo):
    import base64, html
    from mpe_source import load_source
    path=source_file(repo)
    code='for (int i = 0; i < n && p != NULL; ++i) { printf("$%d: very long diagnostic message for local scrolling only", i); }'
    text=path.read_text().replace('<p>함수 결과를 구해요.</p><pre><code>printf("$%d", n);</code></pre>',
       '<pre><code>'+html.escape(code)+'</code></pre><ol><li>(a) 상태를 구하라</li><li>(b) 복잡도를 설명하라</li></ol>')
    card=text[text.index('<article'):text.index('</article>')+10]
    text=text.replace('</section>',card.replace('id="p1"','id="p2"').replace('1001 기출','1002 기출')+'</section>')
    path.write_text(text)
    (path.parent/'그림.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII='))
    pack=load_source(path,repo)
    extra=('<table><tr><th>연산</th><th>상태</th></tr><tr><td>push(1)</td><td>[1]</td></tr><tr><td>pop()</td><td>[]</td></tr></table>'
           '<svg viewBox="0 0 100 30" role="img" aria-label="상태 그림"><defs><clipPath id="state"><rect width="100" height="30"/></clipPath></defs><rect width="100" height="30" clip-path="url(#state)"/></svg>'
           '<figure><img src="그림.png" alt="검증용 픽셀"><figcaption>로컬 그림 자원 검증</figcaption></figure>')
    fragments={p.id:fragment(p).replace('<div class="sum" hidden>', '<div class="sum" hidden><div class="summary-group"><h4>핵심 규칙</h4><p>$A^2=A\\cdot A$</p></div>')+extra for p in pack.problems}
    return pack,fragments
