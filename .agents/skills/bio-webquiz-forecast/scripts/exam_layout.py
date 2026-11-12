"""Check the published exam layout against its authored pack."""
from __future__ import annotations

from exam_dom import Node, parse


def expected_sections(pack: dict, *, include_empty: bool = False) -> dict[str, list[str]]:
    sections = {part['id']: [] for part in pack['parts']}
    for problem in pack['problems']:
        if problem['id'] in pack['answer_key']:
            sections[problem['part']].append(problem['id'])
    return sections if include_empty else {part: ids for part, ids in sections.items() if ids}


def check_layout(html: str, expected: dict[str, list[str]]) -> list[str]:
    root = parse(html)
    navs = list(root.find_all(lambda node: node.tag == 'nav' and 'toc' in node.classes))
    mains = list(root.find_all(lambda node: node.tag == 'main'))
    if len(navs) != 1 or len(mains) != 1:
        return [f'[exam-layout] 시험형: 목차와 본문이 각각 하나여야 함 (목차 {len(navs)}, 본문 {len(mains)})']

    errors = []
    links = [link.attrs.get('href') for link in navs[0].find_all(lambda node: node.tag == 'a')]
    expected_links = [f'#{part}' for part in expected]
    if links != expected_links:
        errors.append(f'[exam-layout] 시험형 목차 링크: {links} ≠ {expected_links}')

    main = mains[0]
    sections = [node for node in main.children if isinstance(node, Node) and node.tag == 'section']
    section_ids = [section.attrs.get('id') for section in sections]
    if section_ids != list(expected):
        errors.append(f'[exam-layout] 시험형 본문 섹션: {section_ids} ≠ {list(expected)}')

    cards_by_section = {section: [] for section in sections}
    for card in main.find_all(lambda node: node.tag == 'article' and 'card' in node.classes):
        cid = card.attrs.get('id')
        if card.parent not in cards_by_section:
            errors.append(f'[exam-layout] 시험형 {cid}: 본문 섹션 바로 아래에 있어야 함')
        else:
            cards_by_section[card.parent].append(cid)

    for section, part in zip(sections, section_ids):
        if part in expected and cards_by_section[section] != expected[part]:
            errors.append(f'[exam-layout] 시험형 {part} 문항: {cards_by_section[section]} ≠ {expected[part]}')
    return errors
