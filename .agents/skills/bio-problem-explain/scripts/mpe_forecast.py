"""Explicit, version-bound adapter for validated webquiz forecast HTML."""
import json
import re
from pathlib import Path
from mpe_shared import Node, parse, inner, compact, math_delimiter_errors, prose_text
from mpe_source import inside, existing_path, nfc, sha256, subparts
from mpe_types import ExplainError, Problem, SourcePack

FILENAME_RE = r'복습문제_([1-9]\d*장)_(웹과제예상_v[1-9]\d*)\.html'
QUESTION_IDS = tuple(f'p{i}' for i in range(1, 16))
CARD_IDS = ('o1', 'o2', *QUESTION_IDS)


def one(node, cls, id_, optional=False):
    nodes = list(node.find_all(lambda n: cls in n.classes))
    if optional and not nodes:
        return None
    if len(nodes) != 1:
        raise ExplainError(f'{id_}: {cls} 누락/중복')
    return nodes[0]


def load_forecast_source(path: Path, repo: Path) -> SourcePack:
    path = inside(existing_path(Path(path)), repo)
    match = re.fullmatch(FILENAME_RE, nfc(path.name))
    if not match:
        raise ExplainError('예상문제 파일명 오류')
    chapter = int(match[1][:-1])
    version = int(match[2].split('_v')[1])
    expected = Path(repo) / '웹과제예상' / f'{chapter}장'
    if nfc(path.parent.resolve()) != nfc(expected.resolve()):
        raise ExplainError('예상문제 장 폴더 불일치')
    try:
        src = path.parent / 'src' / f'v{version}'
        contexts = [inside(existing_path(src / name), repo) for name in ('pack.json', 'blueprint.md')]
        manifest = json.loads(contexts[0].read_text(encoding='utf-8'))
        if not isinstance(manifest, dict) or any(type(manifest.get(k)) is not int or manifest[k] != value
                                               for k, value in [('chapter', chapter), ('version', version)]):
            raise ExplainError('예상문제 manifest 장·버전 불일치')
        ids = [p['id'] for p in manifest['problems']]
        if len(ids) != len(CARD_IDS) or set(ids) != set(CARD_IDS):
            raise ExplainError('manifest 카드 집합 불일치')
        key = manifest['answer_key']
        if not isinstance(key, dict) or set(key) != set(QUESTION_IDS) or any(v not in tuple('ABCDE') for v in key.values()):
            raise ExplainError('manifest 정답키 집합/값 불일치')
        root = parse(path.read_text(encoding='utf-8'))
        cards = list(root.find_all(lambda n: n.tag == 'article' and 'card' in n.classes))
        ids = [n.attrs.get('id') for n in cards]
        if len(ids) != len(CARD_IDS) or set(ids) != set(CARD_IDS):
            raise ExplainError('예상문제 카드 누락/중복/알 수 없는 ID')
        by_id = {n.attrs['id']: n for n in cards}
        problems = []
        for id_ in QUESTION_IDS:
            node = by_id[id_]
            titles = list(node.find_all(lambda n: n.tag == 'h3'))
            if len(titles) != 1 or not titles[0].text().strip():
                raise ExplainError(f'{id_}: 제목 누락/중복')
            source = node.attrs.get('data-source', '').strip()
            if not source:
                raise ExplainError(f'{id_}: 출처 누락')
            problem = one(node, 'problem', id_)
            solution = one(node, 'solution', id_)
            steps_node = one(solution, 'steps', id_)
            steps = tuple(inner(n).strip() for n in steps_node.children if isinstance(n, Node) and n.tag == 'li')
            if not steps or any(not compact(s) for s in steps):
                raise ExplainError(f'{id_}: 풀이 단계 누락')
            answer = one(solution, 'answer', id_)
            # Static forecast cards use .answer for grading; data-correct is optional.
            letters = re.fullmatch(r'\s*(?:정답\s*[:：]\s*)?([A-E])\s*\.?\s*', answer.text())
            if not letters or letters[1] != key[id_] or node.attrs.get('data-correct', key[id_]) != key[id_]:
                raise ExplainError(f'{id_}: 카드 정답·manifest 정답키 불일치')
            original = one(node, 'original', id_, optional=True)
            original_html = inner(original, True).strip() if original else ''
            statement = inner(problem).strip()
            if not compact(statement):
                raise ExplainError(f'{id_}: 빈 문제')
            fields = (statement, original_html, *steps, inner(answer))
            if any(math_delimiter_errors(prose_text(parse(value))) for value in fields):
                raise ExplainError(f'{id_}: 수식 구분자 오류')
            problems.append(Problem(id_, int(id_[1:]), titles[0].text().strip(), source,
                                    original_html, statement, '', (), steps, inner(answer).strip(),
                                    subparts(statement, original_html)))
        hashes = tuple(sorted((str(p), sha256(p)) for p in contexts))
        return SourcePack('forecast', match[1], match[2], path, sha256(path), tuple(problems), hashes)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if isinstance(exc, ExplainError):
            raise
        raise ExplainError('예상문제 입력 오류: ' + str(exc)) from exc
