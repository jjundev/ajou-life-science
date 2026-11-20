import hashlib
import json
import subprocess
import sys
from pathlib import Path

import fitz
import pytest
from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_pdf.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def quiz(tmp_path):
    folder = tmp_path / "캡처"
    folder.mkdir()
    pages = []
    for number, color in ((2, "blue"), (1, "red")):
        image = folder / f"문제 {number}.png"
        Image.new("RGB", (40, 24), color).save(image)
        pages.append({
            "question": number,
            "source": str(image),
            "sha256": digest(image),
            "crop": [4, 2, 32, 22],
        })
    return {"chapter": 9, "date": "2026-11-19", "expected_questions": 2, "pages": pages}


def run(tmp_path, quiz, *args):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(quiz))
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, str(manifest)],
        capture_output=True, text=True,
    )


def test_build_orders_and_crops_pages(tmp_path, quiz):
    candidate = tmp_path / "draft.pdf"
    result = run(tmp_path, quiz, "build", "--output", str(candidate))
    assert result.returncode == 0, result.stderr
    with fitz.open(candidate) as pdf:
        assert len(pdf) == 2
        assert "9장" in pdf.metadata["title"]
        for page, color in zip(pdf, (bytes([255, 0, 0]), bytes([0, 0, 255])), strict=True):
            pixmap = page.get_pixmap(dpi=144)
            assert (pixmap.width, pixmap.height) == (28, 20)
            assert pixmap.samples == color * (28 * 20)


@pytest.mark.parametrize(("mutation", "error"), [
    (lambda quiz: quiz.update(chapter=0), "chapter"),
    (lambda quiz: quiz.update(date="2026-02-30"), "date"),
    (lambda quiz: quiz["pages"].pop(), "missing"),
    (lambda quiz: quiz["pages"].append(quiz["pages"][0]), "duplicate"),
    (lambda quiz: quiz["pages"][0].update(crop=[0, 0, 100, 20]), "crop"),
    (lambda quiz: quiz["pages"][0].update(sha256="0" * 64), "SHA-256"),
])
def test_invalid_manifest_leaves_no_pdf(tmp_path, quiz, mutation, error):
    mutation(quiz)
    output = tmp_path / "candidate.pdf"
    result = run(tmp_path, quiz, "build", "--output", str(output))
    assert result.returncode != 0
    assert error in result.stderr
    assert not output.exists()


def test_publish_requires_review_hash_and_preserves_conflicts(tmp_path, quiz):
    candidate = tmp_path / "draft.pdf"
    assert run(tmp_path, quiz, "build", "--output", str(candidate)).returncode == 0
    repo = tmp_path / "repo"
    (repo / "웹과제").mkdir(parents=True)
    target = repo / "웹과제/9장/raw/웹과제_9장_2026-11-19.pdf"

    def publish(sha256):
        return run(tmp_path, quiz, "publish", "--candidate", str(candidate),
                   "--reviewed-sha256", sha256, "--repo", str(repo))

    assert publish("0" * 64).returncode != 0
    assert not target.exists()
    reviewed = digest(candidate)
    result = publish(reviewed)
    assert result.returncode == 0, result.stderr
    assert digest(target) == reviewed
    assert publish(reviewed).returncode == 0

    target.unlink()
    target.write_bytes(b"existing")
    assert publish(reviewed).returncode != 0
    assert target.read_bytes() == b"existing"


def test_publish_rejects_candidate_from_different_manifest(tmp_path, quiz):
    candidate = tmp_path / "draft.pdf"
    assert run(tmp_path, quiz, "build", "--output", str(candidate)).returncode == 0
    repo = tmp_path / "repo"
    (repo / "웹과제").mkdir(parents=True)
    quiz["pages"][0]["crop"] = [4, 2, 33, 22]
    result = run(tmp_path, quiz, "publish", "--candidate", str(candidate),
                 "--reviewed-sha256", digest(candidate), "--repo", str(repo))
    assert result.returncode != 0
    assert "page 2" in result.stderr
    assert not (repo / "웹과제/9장").exists()
