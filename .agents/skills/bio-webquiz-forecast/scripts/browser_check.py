#!/usr/bin/env python3
"""8단계 브라우저 확인: 연습형·시험형 두 문제판을 한 번에 검사한다.

CLI: browser_check.py <연습형 복습문제_<N>장_웹과제예상_v<K>.html> --out <RUN>/browser.json [--shots <dir>]

- 저장소 루트를 127.0.0.1 임의 포트로 띄운다(끝나면 끈다). 1280×900·375×812 × light·dark.
- 동작 시간 제한 3초(탐색 20초). 셀렉터가 틀려 30초씩 기다리는 일을 막는다.
- 실패는 멈추지 않고 모두 모아 JSON에 남기며 하나라도 있으면 exit 1.
- 이 결과는 증거일 뿐이다. 화면 품질(겹침·간격)은 저장한 스크린샷을 에이전트가 직접 보고 판단한다.

런타임 DOM(review-interaction.js·시험형 스크립트가 바꾼 뒤):
- 연습형: 시작 화면(.hero) → hash로 #pN 이동, 보기 `button.review-choice`(data-selected, data-result=
  correct|selected), 상태 `.review-status`, 다시 풀기 `.review-reset`, 애매함 `.review-unsure`.
- 시험형: 시작 화면 → hash로 #p1, `input[type=radio][name=pN]`, 선택하면 다음 문항으로 이동,
  `#submit-exam` → `#exam-results`의 `#results-list > li.exam-result-row` 15개, `#reset-exam`.
"""
from __future__ import annotations

import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sys
import threading
from urllib.parse import quote

VIEWPORTS = [(1280, 900), (375, 812)]
THEMES = ["light", "dark"]
ACTION_TIMEOUT = 3000
NAV_TIMEOUT = 20000
SETTLE_MS = 600  # 문항 전환 애니메이션이 끝난 뒤 찍는다
VENDOR = Path(__file__).resolve().parents[2] / "bio-problem-explain" / "assets" / "vendor"
# 문제판은 CDN의 KaTeX·Pretendard를 쓴다. 같은 버전의 로컬 사본으로 대신 응답해 네트워크를 기다리지 않는다.
CDN_MAP = {"https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/": VENDOR / "katex",
           "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/": VENDOR / "pretendard"}
CONTENT_TYPES = {".css": "text/css", ".js": "application/javascript", ".woff2": "font/woff2",
                 ".woff": "font/woff", ".ttf": "font/ttf"}


def route_external(origin: str, served: set[str], blocked: set[str]):
    """Serve pinned CDN files locally; abort any other external request (recorded)."""
    def handle(route):
        url = route.request.url
        if url.startswith(origin) or url.startswith(("data:", "blob:")):
            return route.continue_()
        for prefix, folder in CDN_MAP.items():
            if url.startswith(prefix):
                local = folder / url[len(prefix):].split("?")[0]
                if local.is_file():
                    served.add(url)
                    return route.fulfill(path=str(local), content_type=CONTENT_TYPES.get(local.suffix, "application/octet-stream"))
        blocked.add(url)
        return route.abort()
    return handle


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Run:
    """One page × viewport × theme; collects failures instead of raising."""

    def __init__(self, page, label: str, origin: str):
        self.page, self.label, self.origin = page, label, origin
        self.failures: list[str] = []
        self.errors: list[str] = []
        self.served: set[str] = set()
        self.blocked: set[str] = set()
        page.on("pageerror", lambda e: self.errors.append(f"pageerror: {e}"))
        page.on("console", lambda m: self.errors.append(f"console: {m.text}") if m.type == "error" else None)
        page.on("requestfailed", lambda r: self.errors.append(f"requestfailed: {r.url}") if r.url.startswith(origin) else None)
        page.on("response", lambda r: self.errors.append(f"{r.status}: {r.url}") if r.status >= 400 and r.url.startswith(origin) else None)
        page.context.route("**/*", route_external(origin, self.served, self.blocked))

    def expect(self, ok: bool, what: str):
        if not ok:
            self.failures.append(f"{self.label}: {what}")
        return ok

    def step(self, what: str, fn):
        try:
            return fn()
        except Exception as e:  # Playwright TimeoutError and friends: record and continue
            self.failures.append(f"{self.label}: {what}: {type(e).__name__}: {str(e).splitlines()[0]}")
            return None

    def go(self, card: str):
        self.page.evaluate("(id) => { location.hash = id; }", card)
        self.page.locator(f"#{card}").wait_for(state="visible")

    def no_overflow(self, where: str):
        self.expect(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), f"{where}: 가로 넘침")


def model(page) -> dict[str, str]:
    data = page.evaluate('JSON.parse(document.getElementById("review-interaction-model").textContent)')
    return {cid: c["answer"] for cid, c in data["cards"].items()}


def check_practice(run: Run, url: str, ids: list[str]) -> dict:
    page = run.page
    page.goto(url, wait_until="domcontentloaded")
    run.expect(page.locator(".hero").first.is_visible(), "연습형: 시작 화면 없음")
    answers = run.step("연습형: 답 모델 읽기", lambda: model(page)) or {}
    run.expect(set(answers) == set(ids), f"연습형: 답 모델 카드 {sorted(answers)} ≠ {ids}")
    run.expect(page.locator("article.card#o1").count() == 1 and page.locator("article.card#o2").count() == 1, "연습형: 개요 o1·o2 없음")
    checked = 0
    for cid in ids:
        if cid not in answers:
            continue
        def one(cid=cid):
            run.go(cid)
            buttons = page.locator(f"#{cid} .review-choice")
            letters = "ABCDE"[: buttons.count()]
            right = letters.index(answers[cid])
            wrong = (right + 1) % len(letters)
            buttons.nth(wrong).click()
            run.expect(buttons.nth(wrong).get_attribute("data-selected") == "true", f"{cid}: 오답 선택 표시 없음")
            run.expect(buttons.nth(wrong).get_attribute("data-result") == "selected", f"{cid}: 오답 data-result")
            run.expect(bool((page.locator(f"#{cid} .review-status").text_content() or "").strip()), f"{cid}: 채점 상태 문구 없음")
            run.expect(page.evaluate("location.hash") == f"#{cid}", f"{cid}: 선택 뒤 현재 문항을 벗어남")
            run.expect(page.locator(f"#{cid} .review-diagnostic:visible").count() >= 1, f"{cid}: 보기별 설명이 보이지 않음")
            page.locator(f"#{cid} .review-reset").click()
            run.expect(page.locator(f"#{cid} .review-choice[data-selected='true']").count() == 0, f"{cid}: 다시 풀기 뒤 선택 남음")
            buttons.nth(right).click()
            run.expect(buttons.nth(right).get_attribute("data-result") == "correct", f"{cid}: 정답 표시 없음")
            return True
        if run.step(f"{cid}: 연습형 조작", one):
            checked += 1
    run.expect(page.locator(".review-unsure").count() == len(ids), "연습형: 애매함 표시 버튼 수")
    run.expect(page.locator('button:has-text("복기")').count() >= 1, "연습형: 복기 프롬프트 버튼 없음")
    run.no_overflow("연습형")
    run.step("연습형: 새로고침", lambda: page.reload(wait_until="domcontentloaded"))
    run.expect(page.locator(".review-choice[data-selected='true']").count() == 0, "연습형: 새로고침 뒤 선택 남음")
    run.expect((page.locator("#progress-n").text_content() or "").strip() == "0", "연습형: 새로고침 뒤 진행 수가 0이 아님")
    return {"cards_checked": checked}


def check_exam(run: Run, url: str, ids: list[str], answers: dict[str, str]) -> dict:
    page = run.page
    page.on("dialog", lambda d: d.accept())
    page.goto(url, wait_until="domcontentloaded")
    run.expect(page.locator(".hero").first.is_visible(), "시험형: 시작 화면 없음")
    run.expect(page.locator("article.card#o1, article.card#o2").count() == 0, "시험형: 개요 카드가 있음")
    run.expect(page.locator(".presentation-links a").count() == 0, "시험형: 제출 전 다른 판 링크 노출")
    run.expect("출제 개요" not in (page.locator("body").inner_text() or ""), "시험형: '출제 개요' 문구가 보임")
    run.expect((page.locator("#progress-total").text_content() or "").strip() == str(len(ids)), "시험형: 진행 총수 ≠ 문항 수")
    for n, cid in enumerate(ids):
        def one(cid=cid, n=n):
            run.go(cid)
            letter = answers.get(cid, "A") if n % 2 == 0 else ("B" if answers.get(cid) != "B" else "C")
            page.locator(f"#{cid} input[type=radio][value='{letter}']").check()
            if n + 1 < len(ids):
                page.locator(f"#{ids[n + 1]}").wait_for(state="visible")
            return True
        run.step(f"{cid}: 시험형 선택 후 다음 문항 이동", one)
    run.expect(page.locator(".solution:visible").count() == 0, "시험형: 제출 전 풀이 노출")
    run.step("시험형: 마지막 문항", lambda: run.go(ids[-1]))
    run.step("시험형: 제출", lambda: page.locator("#submit-exam").click())
    rows = page.locator("#results-list > li.exam-result-row")
    run.expect(page.locator("#exam-results").is_visible(), "시험형: 제출 뒤 결과 영역 숨김")
    row_count = rows.count()
    run.expect(row_count == len(ids), f"시험형: 결과 행 {row_count} ≠ {len(ids)}")
    if row_count:
        first = rows.first.inner_text()
        run.expect(all(word in first for word in ("내 답", "정답")), "시험형: 결과 행에 내 답·정답 없음")
    run.no_overflow("시험형 결과")
    run.step("시험형: 새로고침", lambda: page.reload(wait_until="domcontentloaded"))
    run.expect(page.locator("input:checked").count() == 0, "시험형: 새로고침 뒤 답 남음")
    run.expect(page.locator("#exam-results").is_hidden(), "시험형: 새로고침 뒤 결과 노출")
    return {"rows": row_count}


def check(practice: Path, shots: Path | None = None, viewports=VIEWPORTS, themes=THEMES) -> dict:
    from playwright.sync_api import sync_playwright
    practice = practice.resolve()
    exam = practice.with_name(practice.name.replace("_v", "_시험형_v"))
    repo = practice.parents[2]
    ids = sorted({m for m in re.findall(r'<article class="card[^"]*" id="(p\d+)"', practice.read_text(encoding="utf-8"))},
                 key=lambda c: int(c[1:]))
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(repo)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}/"
    url = lambda p: origin + quote(p.relative_to(repo).as_posix())
    report = {"practice": {"path": str(practice), "sha256": sha256(practice)},
              "exam": {"path": str(exam), "sha256": sha256(exam) if exam.is_file() else None},
              "viewports": [f"{w}x{h}" for w, h in viewports], "themes": list(themes), "runs": [], "failures": []}
    if not exam.is_file():
        report["failures"].append(f"시험형 파일 없음: {exam.name}")
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height in viewports:
                for theme in themes:
                    for kind, path in (("practice", practice), ("exam", exam)):
                        if not path.is_file():
                            continue
                        ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=theme)
                        page = ctx.new_page()
                        page.set_default_timeout(ACTION_TIMEOUT)
                        page.set_default_navigation_timeout(NAV_TIMEOUT)
                        run = Run(page, f"{kind} {width}x{height} {theme}", origin)
                        if kind == "practice":
                            detail = run.step("연습형 검사", lambda: check_practice(run, url(path), ids)) or {}
                            answers = run.step("답 모델", lambda: model(page)) or {}
                        else:
                            detail = run.step("시험형 검사", lambda: check_exam(run, url(path), ids, answers)) or {}
                        if shots is not None:
                            shots.mkdir(parents=True, exist_ok=True)
                            figure = next((c for c in ids if page.locator(f"#{c} svg").count()), ids[-1])
                            for cid in dict.fromkeys((ids[0], figure)):
                                shot = shots / f"{kind}-{width}x{height}-{theme}-{cid}.png"
                                run.step(f"스크린샷 {cid}", lambda: (run.go(cid), page.wait_for_timeout(SETTLE_MS), page.screenshot(path=str(shot), timeout=10000)))
                        run.failures += [f"{run.label}: {e}" for e in run.errors]
                        report["runs"].append({"label": run.label, "detail": detail, "failures": run.failures,
                                               "cdn_served_locally": len(run.served),
                                               "external_blocked": sorted(run.blocked)})
                        report["failures"] += run.failures
                        ctx.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    report["status"] = "fail" if report["failures"] else "pass"
    return report


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="연습형·시험형 브라우저 확인")
    parser.add_argument("html", type=Path, help="연습형 문제판 HTML")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shots", type=Path)
    args = parser.parse_args(argv)
    if "_시험형_" in args.html.name:
        print("연습형 HTML을 넘기세요(시험형은 자동으로 찾는다)", file=sys.stderr)
        return 2
    report = check(args.html, args.shots)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"browser: {report['status']} · 실행 {len(report['runs'])}회 · 실패 {len(report['failures'])}건 → {args.out}")
    for line in report["failures"][:20]:
        print("  " + line)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
