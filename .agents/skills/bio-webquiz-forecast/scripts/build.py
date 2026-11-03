#!/usr/bin/env python3
"""웹과제 예상 세트(.pack/v<K>) → 복습문제 형식 HTML, 그리고 버전 관리.

조립은 bio-review-pack assemble.build_review를 그대로 쓴다. 치환 2개(정리노트 링크, data-range)는
각각 정확히 1회여야 한다. 장 폴더 루트에는 HTML만 두고 소스는 숨김 폴더 `.pack/v<K>/`에 둔다.
CLI:
  build.py <src>              .pack/v<K> → 웹과제예상/<N>장/복습문제_<N>장_웹과제예상_v<K>.html
  build.py --next <repo> <N>  다음 버전 번호 출력
  build.py --init <repo> <N>  다음 버전 폴더(.pack/v<K>/cards) 생성 후 경로 출력
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

REVIEW_PACK = Path(__file__).resolve().parents[2] / "bio-review-pack" / "scripts"
sys.path.insert(0, str(REVIEW_PACK))
import assemble  # noqa: E402
import manifest as manifest_mod  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'bio-exam-forecast' / 'scripts'))
import exam_presentations

PACK = ".pack"  # 장 폴더의 숨김 소스 폴더(해설 부속 파일도 여기에 둔다)
VERSION_RE = re.compile(r"v(\d+)")
HTML_VERSION_RE = re.compile(r"_v(\d+)\.html$")


class BuildError(RuntimeError):
    pass


def load_pack(src: Path | str) -> dict:
    src = Path(src)
    m = json.loads((src / "pack.json").read_text(encoding="utf-8"))
    n, k = m["chapter"], m["version"]
    if src.name != f"v{k}" or src.parent.name != PACK or src.parent.parent.name != f"{n}장":
        raise BuildError(f"폴더({src})가 pack.json(chapter={n}, version={k})과 맞지 않음")
    m["range"], m["slug"] = f"{n}장", f"웹과제예상_v{k}"
    return m


def _once(html: str, old: str, new: str) -> str:
    if html.count(old) != 1:
        raise BuildError(f"치환 대상이 정확히 1개가 아님({html.count(old)}개): {old}")
    return html.replace(old, new)


def render(src: Path | str, *, dual: bool | None = None) -> tuple[str, str]:
    src = Path(src)
    m = load_pack(src)
    try:
        html = assemble.build_review(m, src)
    except (assemble.AssembleError, ValueError) as e:
        raise BuildError(str(e)) from e
    html = _once(html, f'href="{manifest_mod.note_name(m)}"', f'href="{m["note_href"]}"')
    html = _once(html, f'data-range="{m["range"]}"', f'data-range="{m["range"]}-v{m["version"]}"')
    if dual is None:
        dual = (src / 'presentations.json').is_file()
    if dual:
        html = exam_presentations.decorate(html, m, 'practice', exam_presentations.set_hash(src))
    return manifest_mod.review_name(m), html


def build(src: Path | str) -> Path:
    src = Path(src).resolve()
    name, raw = render(src, dual=False)
    out = src.parents[1] / name
    m = load_pack(src)
    question_hash = exam_presentations.set_hash(src)
    exam = exam_presentations.web_exam(raw, m)
    texts = dict(practice=exam_presentations.decorate(raw, m, 'practice', question_hash),
                 exam=exam_presentations.decorate(exam, m, 'exam', question_hash))
    exam_presentations.write_pair(src, texts)
    return out


def next_version(chapter_dir: Path | str) -> int:
    d = Path(chapter_dir)
    nums = [0]
    if (d / PACK).is_dir():
        nums += [int(m.group(1)) for p in (d / PACK).iterdir()
                 if p.is_dir() and (m := VERSION_RE.fullmatch(p.name))]
    if d.is_dir():
        nums += [int(m.group(1)) for p in d.iterdir() if (m := HTML_VERSION_RE.search(p.name))]
    return max(nums) + 1


def init_version(repo: Path | str, chapter: int, version: int | None = None) -> Path:
    d = Path(repo) / "웹과제예상" / f"{chapter}장"
    k = version or next_version(d)
    src = d / PACK / f"v{k}"
    if src.exists():
        raise BuildError(f"이미 있는 버전: {src}")
    (src / "cards").mkdir(parents=True)
    return src


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if len(args) == 3 and args[0] == "--next":
            print(next_version(Path(args[1]) / "웹과제예상" / f"{args[2]}장"))
        elif len(args) == 3 and args[0] == "--init":
            print(init_version(args[1], int(args[2])))
        elif len(args) == 1:
            print(build(args[0]))
        else:
            print(__doc__, file=sys.stderr)
            return 2
    except BuildError as e:
        print(f"빌드 실패: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
