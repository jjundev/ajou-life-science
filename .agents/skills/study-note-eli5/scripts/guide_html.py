"""HTML-contract validation for Study Note ELI5 artifacts."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser


@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None]
    parent: "Node | None" = None
    text: list[str] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)


class GuideParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {})
        self.stack = [self.root]
        self.nodes: list[Node] = [self.root]
        self.ids: dict[str, Node] = {}
        self.errors: list[str] = []
    def handle_starttag(self, tag, attrs):
        node = Node(tag.lower(), dict(attrs), self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        ident = node.attrs.get("id")
        if ident:
            if ident in self.ids: self.errors.append(f"duplicate HTML id: {ident}")
            self.ids[ident] = node
        if node.tag not in self.VOID: self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID: self.handle_endtag(tag)
    def handle_endtag(self, tag):
        tag = tag.lower()
        matches = [i for i in range(len(self.stack) - 1, 0, -1) if self.stack[i].tag == tag]
        if not matches:
            self.errors.append(f"unmatched closing tag: {tag}")
            return
        index = matches[0]
        if index != len(self.stack) - 1: self.errors.append(f"broken nesting before: {tag}")
        del self.stack[index:]
    def handle_data(self, data):
        self.stack[-1].text.append(data)
    def close(self):
        super().close()
        if len(self.stack) > 1:
            self.errors.extend(f"unclosed tag: {node.tag}" for node in self.stack[1:])


def parse_guide(html: str) -> GuideParser:
    parser = GuideParser()
    try:
        parser.feed(html); parser.close()
    except Exception as error:
        parser.errors.append(f"HTML parse error: {error}")
    return parser


def descendants(node: Node) -> list[Node]:
    return [item for child in node.children for item in (child, *descendants(child))]


def text_of(node: Node) -> str:
    if node.tag in {"script", "style", "template"}: return ""
    return " ".join([*node.text, *(text_of(child) for child in node.children)]).strip()


def ancestor_has(node: Node, key: str, value: str) -> bool:
    current: Node | None = node
    while current:
        if current.attrs.get(key) == value: return True
        current = current.parent
    return False


def ancestor_tag(node: Node, tag: str) -> bool:
    current: Node | None = node.parent
    while current:
        if current.tag == tag:
            return True
        current = current.parent
    return False


def _nodes(guide, **attrs):
    return [node for node in guide.nodes if all(node.attrs.get(key) == value for key, value in attrs.items())]


def _visible_teaching(node: Node) -> bool:
    current: Node | None = node
    while current:
        if current.tag in {"details", "script", "style", "template"} or "hidden" in current.attrs or current.attrs.get("aria-hidden") == "true":
            return False
        current = current.parent
    return bool(text_of(node))


def mapping_errors(guide: GuideParser, data: dict) -> list[str]:
    errors = []
    facts = {fact["id"]: fact for fact in data["inventory"]["facts"]}
    mappings = data.get("mappings", [])
    seen = set()
    for mapping in mappings:
        if not isinstance(mapping, dict) or mapping.get("fact_id") not in facts:
            errors.append("mapping references unknown fact"); continue
        fact_id = mapping["fact_id"]
        if fact_id in seen: errors.append(f"duplicate mapping: {fact_id}")
        seen.add(fact_id)
        targets = mapping.get("target_ids")
        if not isinstance(targets, list) or not targets or len(targets) != len(set(targets)):
            errors.append(f"invalid mapping targets: {fact_id}"); continue
        for target_id in targets:
            node = guide.ids.get(target_id)
            if node is None:
                errors.append(f"missing fact target: {fact_id}/{target_id}"); continue
            fact = facts[fact_id]
            if fact.get("scope") == "deferred":
                if not ancestor_has(node, "data-role", "boundary") or not _visible_teaching(node):
                    errors.append(f"fact target is not visible boundary: {fact_id}/{target_id}")
            elif not ancestor_has(node, "data-role", "teaching") or not _visible_teaching(node):
                errors.append(f"fact target is not visible teaching: {fact_id}/{target_id}")
            elif fact.get("concept_id") and not ancestor_has(node, "data-concept", fact["concept_id"]):
                errors.append(f"fact target concept mismatch: {fact_id}/{target_id}")
    for fact_id in facts:
        if fact_id not in seen: errors.append(f"fact missing mapping: {fact_id}")
    return errors


def question_errors(guide: GuideParser, inventory: dict) -> list[str]:
    errors = []
    expected = {item["id"]: item for item in inventory["questions"]}
    nodes = _nodes(guide, **{"data-question-id": None})
    nodes = [node for node in guide.nodes if "data-question-id" in node.attrs]
    found = {}
    for node in nodes:
        ident = node.attrs.get("data-question-id")
        if ancestor_has(node, "data-role", "recall"):
            errors.append(f"generated recall has question id: {ident}")
        if ident in found: errors.append(f"duplicate question: {ident}")
        found[ident] = node
    if set(found) != set(expected):
        for ident in sorted(set(expected) - set(found)): errors.append(f"missing question: {ident}")
        for ident in sorted(set(found) - set(expected)): errors.append(f"unexpected question: {ident}")
    for ident, item in expected.items():
        node = found.get(ident)
        if not node: continue
        if node.attrs.get("data-status") != item["status"]:
            errors.append(f"question status mismatch: {ident}"); continue
        children = descendants(node)
        parts = {part: [child for child in children if child.attrs.get("data-part") == part and text_of(child)] for part in ("prompt", "answer", "reason", "trap", "deferred-reason")}
        solutions = [child for child in children if child.tag == "details" and child.attrs.get("data-role") == "solution"]
        if item["status"] == "deferred":
            if not parts["deferred-reason"] or parts["answer"] or parts["reason"] or solutions:
                errors.append(f"invalid deferred question: {ident}")
        else:
            if any(not parts[key] for key in ("prompt", "answer", "reason", "trap")) or not solutions:
                errors.append(f"incomplete active question: {ident}")
            if not all(ancestor_has(part, "data-role", "solution") for part in parts["answer"]):
                errors.append(f"answer not in solution: {ident}")
            fact_by_id = {fact["id"]: fact for fact in inventory["facts"]}
            required = {fact_by_id[fid].get("concept_id") for fid in item["fact_ids"] if fact_by_id[fid].get("concept_id")}
            hrefs = {child.attrs.get("href") for child in children if child.tag == "a"}
            for concept in required:
                if f"#concept-{concept}" not in hrefs: errors.append(f"missing concept remedy: {ident}/{concept}")
    return errors

def answerability_errors(guide: GuideParser, data: dict) -> list[str]:
    if data.get("schema_version") != 2:
        return []
    errors = []
    facts = {fact["id"]: fact for fact in data["inventory"]["facts"]}
    mapping = {
        item.get("fact_id"): set(item.get("target_ids", []))
        for item in data.get("mappings", [])
        if isinstance(item, dict)
    }
    nodes = {
        node.attrs.get("data-question-id"): node
        for node in guide.nodes if "data-question-id" in node.attrs
    }
    for question in data["inventory"]["questions"]:
        if question.get("status") == "deferred":
            continue
        ident = question["id"]
        node = nodes.get(ident)
        expected_format = question.get("format")
        if node is not None and node.attrs.get("data-format") != expected_format:
            errors.append(f"question format mismatch: {ident}")
        requirements = question.get("requirements")
        answerability = question.get("answerability")
        if not isinstance(requirements, list) or not requirements:
            errors.append(f"question missing requirements: {ident}")
            continue
        if any(fact_id not in facts for fact_id in requirements):
            errors.append(f"question has unknown requirement: {ident}")
        if not isinstance(answerability, dict):
            errors.append(f"question missing answerability: {ident}")
            continue
        teaching_targets = answerability.get("teaching_target_ids")
        if not isinstance(teaching_targets, list):
            errors.append(f"question missing teaching targets: {ident}")
            teaching_targets = []
        for fact_id in requirements:
            valid = mapping.get(fact_id, set()) & set(teaching_targets)
            if not valid or not any(
                target in guide.ids
                and ancestor_has(guide.ids[target], "data-role", "teaching")
                and _visible_teaching(guide.ids[target])
                for target in valid
            ):
                errors.append(f"question not answerable from teaching: {ident}/{fact_id}")
        if expected_format == "multiple_choice":
            diagnostics = answerability.get("option_diagnostics")
            if not isinstance(diagnostics, dict) or not diagnostics or any(not text_of_value(value) for value in diagnostics.values()):
                errors.append(f"question missing option diagnostics: {ident}")
            elif (
                type(question.get("option_count")) is not int
                or len(diagnostics) != question["option_count"]
            ):
                errors.append(f"option diagnostics count mismatch: {ident}")
            elif set(diagnostics) != {
                str(index) for index in range(1, question["option_count"] + 1)
            }:
                errors.append(f"option diagnostic keys mismatch: {ident}")
        elif expected_format == "short_answer":
            rubric = answerability.get("rubric")
            if not isinstance(rubric, list) or not rubric or any(not text_of_value(value) for value in rubric):
                errors.append(f"question missing short-answer rubric: {ident}")
        if question.get("diagram_required"):
            targets = answerability.get("figure_target_ids")
            if not isinstance(targets, list) or not targets or any(target not in guide.ids for target in targets):
                errors.append(f"question missing figure evidence: {ident}")
            elif any(
                not ancestor_has(guide.ids[target], "data-role", "teaching")
                or not _visible_teaching(guide.ids[target])
                or (
                    guide.ids[target].tag != "svg"
                    and guide.ids[target].attrs.get("data-role") != "figure-evidence"
                )
                for target in targets
            ):
                for target in targets:
                    target_node = guide.ids.get(target)
                    if (
                        target_node is not None
                        and (
                            not ancestor_has(target_node, "data-role", "teaching")
                            or not _visible_teaching(target_node)
                            or (
                                target_node.tag != "svg"
                                and target_node.attrs.get("data-role") != "figure-evidence"
                            )
                        )
                    ):
                        errors.append(
                            f"figure evidence is not visible teaching: {ident}/{target}"
                        )
        if question.get("grading") == "ambiguous":
            conflicts = [
                child for child in descendants(node)
                if child.attrs.get("data-role") == "source-conflict" and text_of(child)
            ] if node else []
            if not conflicts:
                errors.append(f"ambiguous question missing disclosed conflict: {ident}")
    return errors

def text_of_value(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def learning_errors(guide: GuideParser, inventory: dict) -> list[str]:
    errors = []
    concepts = {item["id"]: item for item in inventory["concepts"]}
    concept_nodes = [node for node in guide.nodes if node.attrs.get("data-concept")]
    found = {node.attrs.get("data-concept"): node for node in concept_nodes}
    if set(found) != set(concepts): errors.append("concept set mismatch")
    for concept_id, concept in concepts.items():
        node = found.get(concept_id)
        if not node: continue
        recalls = [item for item in descendants(node) if item.attrs.get("data-role") == "recall"]
        if not 1 <= len(recalls) <= 3: errors.append(f"invalid recall count: {concept_id}")
        for recall in recalls:
            answers = [item for item in descendants(recall) if item.attrs.get("data-part") == "model-answer"]
            if recall.attrs.get("data-generated") != "true" or not text_of(recall) or not answers:
                errors.append(f"invalid recall: {concept_id}")
            if answers and not all(ancestor_tag(answer, "details") for answer in answers):
                errors.append(f"model answer not hidden: {concept_id}")
        hrefs = {item.attrs.get("href") for item in descendants(node) if item.tag == "a"}
        for prerequisite in concept["prerequisites"]:
            if f"#concept-{prerequisite}" not in hrefs: errors.append(f"missing prerequisite link: {concept_id}/{prerequisite}")
    for node in guide.nodes:
        remedy = node.attrs.get("data-remedy")
        if remedy is not None:
            if remedy not in {"term", "confusion", "process", "condition"} or node.attrs.get("href", "") not in {f"#concept-{key}" for key in concepts}:
                errors.append("invalid remedy link")
    return errors


def resource_errors(guide: GuideParser, html: str) -> list[str]:
    errors = []
    for node in guide.nodes:
        if node.tag in {"img", "iframe", "object", "embed", "audio", "video"} or (node.tag == "script" and node.attrs.get("src")):
            errors.append(f"external resource element: {node.tag}")
        if node.tag == "link" and "stylesheet" in (node.attrs.get("rel") or ""):
            errors.append("external stylesheet")
    if re.search(r"@import|url\s*\(|\b(fetch|XMLHttpRequest|WebSocket|sendBeacon)\b", html, re.I):
        errors.append("network-dependent code")
    return errors

def partial_delivery_errors(
    html: str, data: dict, scope: dict[str, dict]
) -> list[str]:
    if data.get("delivery_mode") != "partial":
        return []
    guide = parse_guide(html)
    errors = []
    banners = [
        node for node in guide.nodes
        if node.attrs.get("data-role") == "partial-banner"
        and _visible_teaching(node)
        and "PARTIAL" in text_of(node)
    ]
    if not banners:
        errors.append("partial banner missing")
    omitted_nodes = [
        node for node in guide.nodes
        if node.attrs.get("data-role") == "omitted-questions"
        and _visible_teaching(node)
    ]
    if not omitted_nodes:
        errors.append("partial omitted-question list missing")
        return errors
    text = " ".join(text_of(node) for node in omitted_nodes)
    declared = {
        item.get("id") for item in data.get("inventory", {}).get("questions", [])
        if isinstance(item, dict)
    }
    for ident in sorted(set(scope) - declared):
        if ident not in text:
            errors.append(f"partial omitted question not disclosed: {ident}")
    return errors


def validate_html(html: str, data: dict) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("inventory"), dict) or not isinstance(data.get("mappings"), list):
        return ["invalid coverage shape for HTML validation"]
    guide = parse_guide(html)
    errors = list(guide.errors)
    if not html.lstrip().lower().startswith("<!doctype html>"): errors.append("missing HTML doctype")
    errors.extend(mapping_errors(guide, data))
    errors.extend(question_errors(guide, data["inventory"]))
    errors.extend(answerability_errors(guide, data))
    errors.extend(learning_errors(guide, data["inventory"]))
    errors.extend(resource_errors(guide, html))
    return errors
