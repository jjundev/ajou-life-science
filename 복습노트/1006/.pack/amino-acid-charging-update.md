# 1006 아미노산 준비·충전·번역 보충 (2026-10-20)

## 변경

- 사용자 승인 설계에 따라 기존 s3-trna의 trna-lifecycle에 ATP를 사용하는 충전, 합성효소의 아미노산 및 tRNA 인식, 알라닌 tRNA 수용 줄기의 인식 표지, 일부 합성효소의 교정 기능을 추가했다.
- s3-ribosome의 amino-acid-supply 보충에 번역의 산물이 개별 아미노산이 아닌 폴리펩티드라는 구분, AUG–GCU–UUU 예, 준비된 재료와 주문서 비유를 추가했다.
- 사람 기준 음식 단백질 소화·흡수, 체내 합성(피루브산의 아미노기 전이로 알라닌 생성), 기존 단백질 분해·재사용, 필수 아미노산을 설명했다. 유전자가 아미노산 합성 효소도 암호화한다는 간접 관계를 남겼다.
- 수업 밖 상세 설명에는 보충 배지와 실제 자료 링크를 붙였다. 기존 교수님 인용·학습 범위 주의는 보존했다.
- HTML·정리노트 MD·요약 패널·manifest 필수 용어를 동기화했다. 재작성 시 현재 HTML/MD의 충전·인식 설명과 amino-acid-supply를 보존해야 한다.
- bio-review-pack의 SKILL.md와 content-rules.md, review-prompt.md에 준비 상태·생성/선택/운반/연결 구분·각 짝맞춤 주체의 확인 기준을 연결했다. 혼동 위험이 있는 토픽만 적용하며 영양·대사 설명을 모든 차시에 강제하지 않는다.

## 근거 대조

- Molecular Biology of the Cell, 4판, From RNA to Protein (NBK26829): ATP를 사용하는 부착, 두 단계의 짝맞춤, tRNA 인식 부위의 차이, 교정과 오충전의 영향을 대조했다.
- Transfer RNA Structure and Identity (NBK6236): 알라닌 tRNA의 수용 줄기 인식 표지를 대조했다.
- National Academies, Committee Overview (NBK224619): 식이·체내 합성·체단백질 분해에서 아미노산이 공급되는 흐름을 대조했다. 세 경로를 설명하되 모든 생물의 유일한 공급원이라고 쓰지 않았다.
- Colorado State University, Absorption of Amino Acids and Peptides in the Small Intestine: 단백질 소화·작은 펩타이드/아미노산 흡수와 혈액으로의 방출을 대조했다. NCBI의 Physiology, Small Bowel 및 Physiology, Nutrient Absorption의 검색 본문에서도 장세포 내 작은 펩타이드 분해를 확인했다.
- NLM MeSH, Alanine (D000409): 피루브산으로부터 아미노기 전이로 알라닌이 생성되는 것을 확인했다.
- National Academies, Protein and Amino Acids (NBK234922): 필수 아미노산의 식이 공급 필요성과 조건에 따른 합성량의 한계를 대조했다.
- 웹 원문 직접 열기 일부는 CAPTCHA/접근 오류였다. 해당 자료는 검색 서비스가 반환한 원문 발췌와 소제목별 본문으로 대조했으며, 원문 전체를 읽었다고 주장하지 않는다. 출처 링크는 학생용 HTML에 남겼다.

## 검증

- manifest.py: OK.
- check_html.py --manifest --note --review: OK.
- html2md.py --check: OK. 복습문제 MD와 기존 SVG는 재변환 후 내용 변경이 없었다.
- skill-creator quick_validate.py: Skill is valid.
- Chromium 1280/375px × light/dark: 전체 화면 가로 넘침 없음, JavaScript 오류 없음, KaTeX 오류 없음. 요약 12개가 패널로 이동하고 본문에 남은 요약은 0개, 관련 출처 링크 8개, 테마 전환 확인.
- 수정한 보충의 제목·본문·하단을 스크롤하여 캡처했다. 모바일 다크의 합성효소 인식 및 아미노산 공급원, 데스크톱 라이트의 번역 구분을 직접 시각 확인했다.
- 독립 읽기 전용 검토: 수정이 필요한 발견 없음. 생성·충전·해독·연결 구분, 대화 범위 충족, 보충의 범위 및 스킬의 선택적 적용을 확인했다.
- 임시 브라우저 검사에서 요약 개수를 잘못 고정한 검증 코드가 한 차례 실패했다. manifest에서 실제 개수 12를 확인해 검증 코드만 수정한 뒤 네 조합을 모두 재검사했다. 제품 결함으로 기록하지 않는다.
- 브라우저 결과: amino-acid-charging-browser-results.json. 임시 캡처와 백업: /tmp/bio1006-charging-20261020/.
