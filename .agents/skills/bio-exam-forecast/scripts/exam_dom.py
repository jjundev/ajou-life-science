"""Existing standalone HTML parser, loaded without changing global sys.path."""
import html
from exam_sources import ROOT,_module
_mod=_module('_exam_html2md',ROOT/'.agents/skills/bio-problem-explain/scripts/vendor/html2md.py')
Node=_mod.Node

def parse(markup):
 parser=_mod.Builder();parser.feed(markup);return parser.root

def outer(node):
 if isinstance(node,str):return html.escape(node,quote=False)
 if node.tag=='svg':return _mod.serialize(node)
 attrs=''.join(f' {k}="{html.escape(v,quote=True)}"' for k,v in node.attrs.items())
 start=f'<{node.tag}{attrs}>'
 return start if node.tag in _mod.VOID else start+inner(node)+f'</{node.tag}>'

def inner(node):return ''.join(outer(c) for c in node.children)
