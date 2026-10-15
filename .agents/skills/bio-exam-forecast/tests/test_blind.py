from exam_fixtures import make_pack,make_candidates
from exam_blind import write_blind
from exam_dom import parse
from exam_contract import ExamError
import pytest

def test_blind_retains_visuals_and_short(repo,tmp_path):
 p=make_pack(repo);out=write_blind(p,tmp_path/'blind/index.html');s=out.read_text();root=parse(s)
 assert len(list(root.find_all(lambda n:n.tag=='article')))==75
 assert len(list(root.find_all(lambda n:n.tag=='input' and n.attrs.get('type')=='text')))==20
 assert 'exam-model' not in s and 'solution' not in s and 'provenance' not in s and 'Aa' not in s
 assert 'source_refs' not in s
 p.write_text('<main></main>')
 with pytest.raises(ExamError):write_blind(p,tmp_path/'empty.html')
