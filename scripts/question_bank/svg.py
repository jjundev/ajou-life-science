"""Validate and namespace the deliberately small, offline SVG figure format."""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
TAGS = {"svg", "g", "path", "line", "polyline", "polygon", "circle", "ellipse", "rect", "text", "tspan", "title", "desc"}
ATTRS = {"id", "viewBox", "role", "aria-label", "aria-labelledby", "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "width", "height", "d", "points", "dx", "dy", "fill", "fill-opacity", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "stroke-opacity", "font-size", "font-family", "font-weight", "text-anchor", "dominant-baseline", "baseline-shift", "transform", "opacity"}
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.:-]*\Z")
NUMBER = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
SEPARATOR = r"(?:[ \t\r\n]+,?[ \t\r\n]*|,[ \t\r\n]*)"
VIEWBOX = re.compile(r"[ \t\r\n]*" + NUMBER + (SEPARATOR + NUMBER) * 3 + r"[ \t\r\n]*\Z")


def validate_svg(text: str) -> list[str]:
    """Return actionable errors; no scripting, CSS, links or embedded images."""
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        return ["SVG declarations forbidden"]
    if re.search(r"<\?(?!xml\s)", text, re.I):
        return ["SVG processing instructions forbidden"]
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        return ["invalid SVG: " + str(error)]
    errors: list[str] = []
    if root.tag not in {"svg", f"{{{SVG_NS}}}svg"}:
        errors.append("SVG root required")
    try:
        viewbox = root.attrib.get("viewBox", "")
        if not VIEWBOX.fullmatch(viewbox):
            raise ValueError
        values = [float(value) for value in re.findall(NUMBER, viewbox)]
        if len(values) != 4 or not all(math.isfinite(value) for value in values) or values[2] <= 0 or values[3] <= 0:
            raise ValueError
    except ValueError:
        errors.append("SVG viewBox requires four finite numbers and positive width/height")
    ids: set[str] = set()
    references: list[str] = []
    for node in root.iter():
        tag = node.tag
        if tag.startswith(f"{{{SVG_NS}}}"):
            tag = tag[len(SVG_NS) + 2:]
        if tag not in TAGS:
            errors.append("forbidden SVG tag: " + node.tag)
        for key, value in node.attrib.items():
            # Backslash escapes can disguise CSS url() inside presentation values.
            if key not in ATTRS or re.search(r"url\s*\(", value, re.I) or (key in {"fill", "stroke"} and "\\" in value):
                errors.append("forbidden SVG attribute: " + key)
        if "id" in node.attrib:
            identifier = node.attrib["id"]
            if not IDENTIFIER.fullmatch(identifier):
                errors.append("invalid SVG id: " + identifier)
            if identifier in ids:
                errors.append("duplicate SVG id: " + identifier)
            ids.add(identifier)
        references.extend(node.attrib.get("aria-labelledby", "").split())
    for reference in references:
        if reference not in ids:
            errors.append("unknown SVG reference: " + reference)
    return errors


def inline_svg(text: str, prefix: str, alt: str) -> str:
    """Safely inline a figure, using assessment-asset-variant as its prefix."""
    errors = validate_svg(text)
    if errors:
        raise ValueError("invalid SVG: " + "; ".join(errors))
    if not IDENTIFIER.fullmatch(prefix):
        raise ValueError("invalid SVG prefix")
    root = ET.fromstring(text)
    for node in root.iter():
        if "id" in node.attrib:
            node.set("id", prefix + "-" + node.attrib["id"])
        if "aria-labelledby" in node.attrib:
            node.set("aria-labelledby", " ".join(prefix + "-" + identifier for identifier in node.attrib["aria-labelledby"].split()))
    root.set("role", "img")
    root.set("aria-label", alt)
    return ET.tostring(root, encoding="unicode")
