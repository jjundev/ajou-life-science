# Content semantic review — all 18 items
Reviewer: read_explanations (blind solver before keys were disclosed; semantic reviewer afterward).
Result: PASS, 18/18. All 72 choices were checked against actual wording. No unanswered ambiguity or blocking correction. No fragment was edited.
Scope: understand/recall/solve/verify/hidden sum for each final fragment. Current p1–p9 recall headings rechecked after normalization. New cards are unchanged from the blind inputs, verified by direct text comparison.
Recall criteria are actionable: roles/components/directions/conditions identify what to inspect rather than just supplying an answer number. Correct choices and all distractors have matching reasons. verify provides elimination, reversal, conservation, structural, or conditional cross-check. Summaries preserve each answer and condition. Optional start/pitfall/retry are absent without constituting missing required material.
## Per-choice mapping
| Item | Choice | Actual claim | Criterion | Application and verdict | Explanation location |
|---|---|---|---|---|---|
| p1:main | 1 | 엽록체가 있으므로 미토콘드리아는 필요 없다. | 광합성하는 잎 세포는 엽록체와 미토콘드리아를 함께 갖고 두 대사를 수행한다. | (1) 엽록체가 있으면 미토콘드리아가 필요 없다는 주장은 광합성과 세포호흡을 같은 기능으로 취급해요. 이 세포에는 두 역할이 함께 필요하므로 틀려요. | explanations/p1.html solve (1) |
| p1:main | 2 | 엽록체가 광합성을 하고 미토콘드리아가 세포호흡을 한다. | 광합성하는 잎 세포는 엽록체와 미토콘드리아를 함께 갖고 두 대사를 수행한다. | (2) 엽록체를 광합성, 미토콘드리아를 세포호흡에 연결했어요. 각 소기관의 대표 기능과 일치하므로 맞아요. | explanations/p1.html solve (2) |
| p1:main | 3 | 미토콘드리아는 광합성, 엽록체는 세포호흡을 맡는다. | 광합성하는 잎 세포는 엽록체와 미토콘드리아를 함께 갖고 두 대사를 수행한다. | (3) 미토콘드리아에 광합성을, 엽록체에 세포호흡을 붙였어요. 두 소기관의 기능을 뒤바꾸었으므로 틀려요. | explanations/p1.html solve (3) |
| p1:main | 4 | 밤에는 미토콘드리아가 사라진다. | 광합성하는 잎 세포는 엽록체와 미토콘드리아를 함께 갖고 두 대사를 수행한다. | (4) 밤에 미토콘드리아가 사라진다는 주장은 빛 조건을 소기관의 존재 조건과 혼동해요. 미토콘드리아는 빛이 없는 동안에도 세포호흡에 참여하므로 틀려요. | explanations/p1.html solve (4) |

<!-- p1 sha256=cc17bd6125183744e0dbdab4c46d65ae379d3c7ce0f9f5095c2b6a997b9231b7 -->
| p2:main | 1 | 세포벽: 인지질 이중층 / 세포막: 셀룰로스 | 벽은 세포막 바깥의 셀룰로스 구조, 막은 인지질 이중층이다. | (1) 세포벽을 인지질 이중층, 세포막을 셀룰로스라고 했어요. 두 구조의 재료를 뒤바꾸었으므로 틀려요. | explanations/p2.html solve (1) |
| p2:main | 2 | 세포벽: 세포막 안쪽 / 세포막: 가장 바깥의 단단한 벽 | 벽은 세포막 바깥의 셀룰로스 구조, 막은 인지질 이중층이다. | (2) 세포벽을 세포막 안쪽이라고 했어요. 실제로는 벽이 막 바깥에 있으므로 위치 기준에서 틀려요. | explanations/p2.html solve (2) |
| p2:main | 3 | 세포벽: 셀룰로스 / 세포막: 인지질 이중층 | 벽은 세포막 바깥의 셀룰로스 구조, 막은 인지질 이중층이다. | (3) 세포벽의 재료를 셀룰로스, 세포막의 구조를 인지질 이중층으로 연결했어요. 두 기준에 맞으므로 맞아요. | explanations/p2.html solve (3) |
| p2:main | 4 | 두 구조는 같은 구조를 다르게 부른 이름이다. | 벽은 세포막 바깥의 셀룰로스 구조, 막은 인지질 이중층이다. | (4) 두 이름이 같은 구조라는 주장이에요. 재료와 위치가 각각 다른 두 구조이므로 틀려요. | explanations/p2.html solve (4) |

<!-- p2 sha256=d2a8cc26370c9208faab71593b075dc9301591745f339b5457751231a44e59ce -->
| p3:main | 1 | 키네신·미세소관·소낭 | 미세소관은 길, 키네신은 ATP를 쓰는 운반자, 소낭은 화물이다. | (1) 키네신을 길로, 미세소관을 운반자로 놓았어요. 트랙과 운동단백질의 역할이 뒤바뀌었으므로 부적합해요. | explanations/p3.html solve (1) |
| p3:main | 2 | 미세소관·키네신·소낭 | 미세소관은 길, 키네신은 ATP를 쓰는 운반자, 소낭은 화물이다. | (2) 미세소관을 길, 키네신을 운반자, 소낭을 짐에 놓았어요. 주어진 수송에서 세 역할이 모두 맞으므로 적합해요. | explanations/p3.html solve (2) |
| p3:main | 3 | 미세섬유·소낭·키네신 | 미세소관은 길, 키네신은 ATP를 쓰는 운반자, 소낭은 화물이다. | (3) 길을 미세섬유로 바꾸고 소낭을 운반자로 놓았어요. 이 문제는 미세소관을 따른 수송이며 소낭은 화물이므로 부적합해요. | explanations/p3.html solve (3) |
| p3:main | 4 | 소낭·액틴·미세소관 | 미세소관은 길, 키네신은 ATP를 쓰는 운반자, 소낭은 화물이다. | (4) 소낭을 길, 액틴을 운반자, 미세소관을 짐으로 놓았어요. 화물·트랙·운동단백질의 구분과 맞지 않으므로 부적합해요. | explanations/p3.html solve (4) |

<!-- p3 sha256=73c75abe16ff8a3d7d549a876dce62b7695dbe62651a963e390adc673fb7b1c9 -->
| p4:main | 1 | 미세소관을 이용한 소낭 수송 | 액틴은 미세섬유의 단위체, 튜불린은 미세소관의 단위체이다. | (1) 미세소관을 이용한 소낭 수송은 튜불린 트랙을 사용해요. 문제에서 그 관이 보존됐으므로 액틴 조립 방해의 직접 효과를 묻는 답으로는 부적합해요. | explanations/p4.html solve (1) |
| p4:main | 2 | 방추사 형성 | 액틴은 미세섬유의 단위체, 튜불린은 미세소관의 단위체이다. | (2) 방추사 형성은 미세소관과 연결돼요. 표적이 된 액틴이 아니라 보존된 튜불린 구조의 기능이므로 부적합해요. | explanations/p4.html solve (2) |
| p4:main | 3 | 미세섬유가 관여하는 근육 수축 | 액틴은 미세섬유의 단위체, 튜불린은 미세소관의 단위체이다. | (3) 근육 수축은 액틴 미세섬유와 연결돼요. 방해받은 재료와 기능이 직접 이어지므로 적합해요. | explanations/p4.html solve (3) |
| p4:main | 4 | 키네신이 걷는 미세소관 트랙 형성 | 액틴은 미세섬유의 단위체, 튜불린은 미세소관의 단위체이다. | (4) 키네신이 걷는 트랙은 튜불린 미세소관이에요. 이 트랙의 형성 자체를 액틴 조립 방해의 직접 표적으로 볼 수 없으므로 부적합해요. | explanations/p4.html solve (4) |

<!-- p4 sha256=bbf0ff8107ef208a99425c998742b8350786a26746135437800e9fc12050051d -->
| p5:main | 1 | 아데닌과 리보스 | 아데노신은 아데닌+리보스인 뉴클레오사이드이다. | (1) 아데닌과 리보스를 골랐어요. 염기와 올바른 당을 함께 갖추었고 인산기를 더하지 않았으므로 맞아요. | explanations/p5.html solve (1) |
| p5:main | 2 | 아데닌과 디옥시리보스 | 아데노신은 아데닌+리보스인 뉴클레오사이드이다. | (2) 아데닌에 디옥시리보스를 붙였어요. 아데노신의 당은 리보스이므로 당의 종류가 달라 틀려요. | explanations/p5.html solve (2) |
| p5:main | 3 | 리보스와 인산기 세 개만 | 아데노신은 아데닌+리보스인 뉴클레오사이드이다. | (3) 리보스와 인산기만 골랐어요. 아데닌이 빠졌고 아데노신에 포함되지 않는 인산기를 더했으므로 틀려요. | explanations/p5.html solve (3) |
| p5:main | 4 | 아데닌과 인산기 세 개만 | 아데노신은 아데닌+리보스인 뉴클레오사이드이다. | (4) 아데닌과 인산기만 골랐어요. 필요한 당 리보스가 빠졌고 불필요한 인산기를 더했으므로 틀려요. | explanations/p5.html solve (4) |

<!-- p5 sha256=a442707a877afd041365ab56ed18206e19a0686bf5dc07035befb2aa7b4c6836 -->
| p6:main | 1 | ATP가 전자를 내놓아 ADP가 된다. | ATP 합성은 ADP+Pi에 에너지를 투입하는 방향이다. | (1) ATP가 전자를 내놓아 ADP가 된다고 했어요. ATP와 ADP의 전환은 여기서 인산기 수 변화로 판단하므로 틀려요. | explanations/p6.html solve (1) |
| p6:main | 2 | ATP에 인산기를 하나 더 붙인다. | ATP 합성은 ADP+Pi에 에너지를 투입하는 방향이다. | (2) ATP에 인산기를 더 붙인다고 했어요. 에너지를 저장하는 ATP 합성의 출발물은 이미 인산기 3개인 ATP가 아니라 ADP이므로 틀려요. | explanations/p6.html solve (2) |
| p6:main | 3 | ADP에 인산기를 붙이는 데 에너지를 투입한다. | ATP 합성은 ADP+Pi에 에너지를 투입하는 방향이다. | (3) ADP에 인산기를 붙이는 데 에너지를 넣는다고 했어요. 인산기 2개에서 3개로 가는 합성 방향과 에너지 투입 조건이 함께 맞으므로 맞아요. | explanations/p6.html solve (3) |
| p6:main | 4 | 아데노신에서 리보스를 떼어낸다. | ATP 합성은 ADP+Pi에 에너지를 투입하는 방향이다. | (4) 아데노신에서 리보스를 떼어낸다고 했어요. ATP를 만들려면 아데노신 골격을 두고 인산기를 붙여야 하므로 틀려요. | explanations/p6.html solve (4) |

<!-- p6 sha256=e441e37ba1cf3b2275a8caef0e13a0d6f20f55538cbe9bb26722bc6e7dfed128 -->
| p7:main | 1 | 기질: 포도당 / 활성 부위: 젖당의 일부 | 기질=효소가 작용하는 반응물, 활성부위=효소 쪽 결합 자리이다. | (1) 포도당은 젖당이 잘린 뒤의 생성물이에요. 이를 기질로 둔 것과 활성 부위를 젖당의 일부로 둔 것이 모두 기준과 달라 틀려요. | explanations/p7.html solve (1) |
| p7:main | 2 | 기질: 젖당 / 활성 부위: 효소의 일부 | 기질=효소가 작용하는 반응물, 활성부위=효소 쪽 결합 자리이다. | (2) 반응 전 들어가는 젖당을 기질로, 결합 자리를 효소의 일부로 두었어요. 반응 전후와 자리의 소속을 모두 맞춰 맞아요. | explanations/p7.html solve (2) |
| p7:main | 3 | 기질: 효소 / 활성 부위: 포도당의 일부 | 기질=효소가 작용하는 반응물, 활성부위=효소 쪽 결합 자리이다. | (3) 효소는 반응을 촉진하는 촉매이지 여기서 반응물 기질이 아니에요. 활성 부위도 포도당에 속하지 않으므로 틀려요. | explanations/p7.html solve (3) |
| p7:main | 4 | 기질: 갈락토오스 / 활성 부위: 세포벽의 일부 | 기질=효소가 작용하는 반응물, 활성부위=효소 쪽 결합 자리이다. | (4) 갈락토오스는 반응 후 생성물이에요. 활성 부위는 세포벽이 아니라 효소에 있으므로 틀려요. | explanations/p7.html solve (4) |

<!-- p7 sha256=be17aee314ec82fab465173aec82fe1f3e038ce06ae74ca6d501d4293dd6d85f -->
| p8:main | 1 | 약물은 젖당이 결합하는 자리와 맞는 구조를 가진다. | 같은 활성부위를 점유하는 약물은 해당 결합 자리에 맞는 성질/구조를 갖는다. | (1) 젖당이 결합하는 자리에 맞는 구조라고 했어요. 같은 활성 부위에 들어간다는 조건을 직접 설명하므로 적합해요. | explanations/p8.html solve (1) |
| p8:main | 2 | 약물이 포도당을 ATP로 바꾸기 때문이다. | 같은 활성부위를 점유하는 약물은 해당 결합 자리에 맞는 성질/구조를 갖는다. | (2) 포도당을 ATP로 바꾸기 때문이라고 했어요. 제시된 원인은 ATP 생성이 아니라 활성 부위 점유이므로 부적합해요. | explanations/p8.html solve (2) |
| p8:main | 3 | 약물이 세포벽의 바깥을 두껍게 만든다. | 같은 활성부위를 점유하는 약물은 해당 결합 자리에 맞는 성질/구조를 갖는다. | (3) 세포벽을 두껍게 만든다는 설명이에요. 세포벽 변화는 약물이 효소의 결합 자리를 차지한다는 조건과 연결되지 않아 부적합해요. | explanations/p8.html solve (3) |
| p8:main | 4 | 약물은 효소의 모든 부분과 같은 구조여야 한다. | 같은 활성부위를 점유하는 약물은 해당 결합 자리에 맞는 성질/구조를 갖는다. | (4) 효소의 모든 부분과 같은 구조여야 한다고 했어요. 필요한 것은 결합 자리에 맞는 구조이지 효소 전체를 복제하는 것이 아니므로 부적합해요. | explanations/p8.html solve (4) |

<!-- p8 sha256=755978aaed6c333a993432a734e5b5a7ef5a388b2876aef15ad7cb3a460cf388 -->
| p9:main | 1 | 자발적 반응도 전혀 일어나지 않는다. | Ea는 속도 장벽이고 반응 전후 자유에너지 차이 ΔG와 구별한다. | (1) 자발적 반응도 일어나지 않는다고 했어요. 장벽을 없앤 조건은 시작을 막는 조건이 아니라 쉽게 하는 조건이므로 틀려요. | explanations/p9.html solve (1) |
| p9:main | 2 | 에너지가 필요한 모든 반응도 저절로 진행된다. | Ea는 속도 장벽이고 반응 전후 자유에너지 차이 ΔG와 구별한다. | (2) 에너지가 필요한 모든 반응도 저절로 진행된다고 했어요. 반응 전후 ΔG는 그대로이므로 필요한 에너지 공급 조건이 사라지지 않아 틀려요. | explanations/p9.html solve (2) |
| p9:main | 3 | 자발적 반응은 더 쉽게 진행될 수 있지만 반응 전후 에너지 차이는 그대로다. | Ea는 속도 장벽이고 반응 전후 자유에너지 차이 ΔG와 구별한다. | (3) 자발적 반응이 쉽게 진행될 수 있으면서 반응 전후 에너지 차이가 유지된다고 했어요. 장벽과 ΔG를 분리한 조건에 맞으므로 맞아요. | explanations/p9.html solve (3) |
| p9:main | 4 | 생성물이 자동으로 기질과 같은 물질이 된다. | Ea는 속도 장벽이고 반응 전후 자유에너지 차이 ΔG와 구별한다. | (4) 생성물이 자동으로 기질과 같은 물질이 된다고 했어요. 장벽 변화는 반응을 시작하기 쉬운 정도의 변화이며 분자 정체를 같게 만드는 변화가 아니므로 틀려요. | explanations/p9.html solve (4) |

<!-- p9 sha256=1d3d42ac64170cd8398562c236db1816b872769dae5b06be3c4f35468ec0b96d -->
| p10:main | 1 | 산화: 전자를 얻었기 때문이다. | 전자 얻음=환원, 잃음=산화이며 NAD+→NADH는 전자 수용이다. | (1) 산화: 전자를 얻었기 때문이다. — 틀려요. 전자를 얻는 것은 환원이고 잃는 것이 산화예요. | explanations/p10.html solve (1) |
| p10:main | 2 | 환원: 전자를 얻었기 때문이다. | 전자 얻음=환원, 잃음=산화이며 NAD+→NADH는 전자 수용이다. | (2) 환원: 전자를 얻었기 때문이다. — 맞아요. 산소 포함 여부를 먼저 추측하지 말고 전자의 유입을 기준으로 판단해요. | explanations/p10.html solve (2) |
| p10:main | 3 | 산화: 인산기를 잃었기 때문이다. | 전자 얻음=환원, 잃음=산화이며 NAD+→NADH는 전자 수용이다. | (3) 산화: 인산기를 잃었기 때문이다. — 틀려요. NAD⁺와 NADH의 전환은 인산기 제거로 판정하지 않아요. | explanations/p10.html solve (3) |
| p10:main | 4 | 환원: 이산화탄소를 방출했기 때문이다. | 전자 얻음=환원, 잃음=산화이며 NAD+→NADH는 전자 수용이다. | (4) 환원: 이산화탄소를 방출했기 때문이다. — 틀려요. 이 변화의 기준은 전자 획득이지 CO₂ 방출이 아니에요. | explanations/p10.html solve (4) |

<!-- p10 sha256=1134b10d941d24c16ad075c2b5ab952227f107707ff2f656d6a9aebaa4cbe6df -->
| p11:main | 1 | 지방이 이미 CO₂만큼 산화되어 있기 때문이다. | 같은 질량의 지방은 더 환원되어 완전 산화 때 더 많은 전자를 공여할 수 있다. | (1) 지방이 이미 CO₂만큼 산화되어 있기 때문이다. — 틀려요. 이미 산화된 CO₂는 일반적인 호흡 연료처럼 더 산화해 에너지를 얻는 출발물이 아니에요. | explanations/p11.html solve (1) |
| p11:main | 2 | 지방이 효소의 활성화 에너지를 없애기 때문이다. | 같은 질량의 지방은 더 환원되어 완전 산화 때 더 많은 전자를 공여할 수 있다. | (2) 지방이 효소의 활성화 에너지를 없애기 때문이다. — 틀려요. 연료의 산화 상태와 효소가 낮추는 반응 장벽은 다른 기준이에요. | explanations/p11.html solve (2) |
| p11:main | 3 | 지방은 상대적으로 C–H 결합이 많고 더 환원되어 있어 산화되며 넘길 전자가 많기 때문이다. | 같은 질량의 지방은 더 환원되어 완전 산화 때 더 많은 전자를 공여할 수 있다. | (3) 지방은 상대적으로 C–H 결합이 많고 더 환원되어 있어 산화되며 넘길 전자가 많기 때문이다. — 맞아요. 더 환원된 탄소가 산화되어 산소 쪽으로 전자를 넘기며 얻는 에너지와 연결해요. | explanations/p11.html solve (3) |
| p11:main | 4 | 지방은 전자를 받지 않고 산소를 만들어 내기 때문이다. | 같은 질량의 지방은 더 환원되어 완전 산화 때 더 많은 전자를 공여할 수 있다. | (4) 지방은 전자를 받지 않고 산소를 만들어 내기 때문이다. — 틀려요. 산소는 호흡 끝에서 소비되는 최종 전자수용체예요. | explanations/p11.html solve (4) |

<!-- p11 sha256=86cfd07afbe1ade2f4e1c0e545755a7193ddcfe4db4f973d53c21b87a47764af -->
| p12:main | 1 | 시트르산 회로에서 만들어져 밖으로 나간다. | O2는 호흡 전자전달계의 최종 전자수용체이며 환원되어 물 생성에 쓰인다. | (1) 시트르산 회로에서 만들어져 밖으로 나간다. — 틀려요. 시트르산 회로에서 나오는 기체는 CO₂예요. | explanations/p12.html solve (1) |
| p12:main | 2 | 전자전달계 끝에서 전자를 받아 환원되고 물 생성에 쓰인다. | O2는 호흡 전자전달계의 최종 전자수용체이며 환원되어 물 생성에 쓰인다. | (2) 전자전달계 끝에서 전자를 받아 환원되고 물 생성에 쓰인다. — 맞아요. 산소는 전자를 마지막으로 받아 물이 되는 쪽이며 소비돼요. | explanations/p12.html solve (2) |
| p12:main | 3 | 전자전달계에서 전자를 잃어 산화된다. | O2는 호흡 전자전달계의 최종 전자수용체이며 환원되어 물 생성에 쓰인다. | (3) 전자전달계에서 전자를 잃어 산화된다. — 틀려요. 산소는 전자를 주는 쪽이 아니라 받는 쪽이에요. | explanations/p12.html solve (3) |
| p12:main | 4 | 포도당의 탄소를 받아 이산화탄소가 된다. | O2는 호흡 전자전달계의 최종 전자수용체이며 환원되어 물 생성에 쓰인다. | (4) 포도당의 탄소를 받아 이산화탄소가 된다. — 틀려요. 포도당 탄소의 CO₂ 방출과 산소의 전자수용을 구분해야 해요. | explanations/p12.html solve (4) |

<!-- p12 sha256=c777b11bf797c2e4b4646c08fb144874c979d0eecbd2c0db3312e681aae9dac3 -->
| p13:main | 1 | 해당과정: 내막 / 시트르산 회로: 세포질 | 진핵 호흡은 해당과정=세포질, TCA=기질, ETC=내막이다. | (1) 해당과정: 내막 / 시트르산 회로: 세포질 — 틀려요. 해당과정은 세포질, 시트르산 회로는 미토콘드리아 기질이에요. | explanations/p13.html solve (1) |
| p13:main | 2 | 해당과정: 기질 / 전자전달계: 세포질 | 진핵 호흡은 해당과정=세포질, TCA=기질, ETC=내막이다. | (2) 해당과정: 기질 / 전자전달계: 세포질 — 틀려요. 해당과정과 전자전달계의 장소를 모두 잘못 연결했어요. | explanations/p13.html solve (2) |
| p13:main | 3 | 시트르산 회로: 내막 / ATP 합성효소: 기질 속에만 떠 있음 | 진핵 호흡은 해당과정=세포질, TCA=기질, ETC=내막이다. | (3) 시트르산 회로: 내막 / ATP 합성효소: 기질 속에만 떠 있음 — 틀려요. 시트르산 회로는 기질이고 ATP 합성효소는 내막에 있어요. | explanations/p13.html solve (3) |
| p13:main | 4 | 해당과정: 세포질 / 시트르산 회로: 기질 / 전자전달계: 내막 | 진핵 호흡은 해당과정=세포질, TCA=기질, ETC=내막이다. | (4) 해당과정: 세포질 / 시트르산 회로: 기질 / 전자전달계: 내막 — 맞아요. 미토콘드리아 안이라는 범위를 막과 액체 공간으로 더 구분해요. | explanations/p13.html solve (4) |

<!-- p13 sha256=21b034112984be768c082cc6191979838be126fca1772ad7e58c42b06c8f2f22 -->
| p14:main | 1 | 탄소 1개가 CO₂로 나가고 NADH가 생기지만 이 단계에서 ATP를 직접 만들지는 않는다. | 피루브산 산화는 C3→C2+CO2, NADH 생성, 직접 ATP0이다. | (1) 탄소 1개가 CO₂로 나가고 NADH가 생기지만 이 단계에서 ATP를 직접 만들지는 않는다. — 맞아요. C3에서 C2 아세틸기를 남기며 CO₂ 1개와 NADH를 만들고 직접 ATP 생성은 없어요. | explanations/p14.html solve (1) |
| p14:main | 2 | 탄소 3개가 모두 CO₂가 되고 ATP가 직접 3개 생긴다. | 피루브산 산화는 C3→C2+CO2, NADH 생성, 직접 ATP0이다. | (2) 탄소 3개가 모두 CO₂가 되고 ATP가 직접 3개 생긴다. — 틀려요. 남은 C2는 아세틸-CoA로 이어지고 이 단계에 직접 ATP 생성은 없어요. | explanations/p14.html solve (2) |
| p14:main | 3 | CO₂는 생기지 않고 ATP만 직접 생긴다. | 피루브산 산화는 C3→C2+CO2, NADH 생성, 직접 ATP0이다. | (3) CO₂는 생기지 않고 ATP만 직접 생긴다. — 틀려요. CO₂가 처음 생기는 단계가 피루브산 산화예요. | explanations/p14.html solve (3) |
| p14:main | 4 | 산소를 생성하며 해당과정이 처음 시작된다. | 피루브산 산화는 C3→C2+CO2, NADH 생성, 직접 ATP0이다. | (4) 산소를 생성하며 해당과정이 처음 시작된다. — 틀려요. 해당과정은 앞서 세포질에서 끝났고 산소를 생성하는 단계도 아니에요. | explanations/p14.html solve (4) |

<!-- p14 sha256=75cc8114ab8154a70c80cebd6e6d4dc768ca9d5188b49d968bd8de04890f5466 -->
| p15:main | 1 | 기질 수준 인산화이므로 반드시 미토콘드리아 기질에서 일어난다. | substrate-level은 반응물 인산기를 ADP에 직접 전달하는 방식이며 matrix 주소와 무관하다. | (1) 기질 수준 인산화이므로 반드시 미토콘드리아 기질에서 일어난다. — 틀려요. 기질 수준의 기질은 substrate이고 미토콘드리아 공간인 matrix와 뜻이 달라요. | explanations/p15.html solve (1) |
| p15:main | 2 | 산화적 인산화이므로 반드시 H⁺ 귀환이 필요하다. | substrate-level은 반응물 인산기를 ADP에 직접 전달하는 방식이며 matrix 주소와 무관하다. | (2) 산화적 인산화이므로 반드시 H⁺ 귀환이 필요하다. — 틀려요. 직접 인산기를 건네는 조건은 기질 수준 인산화예요. | explanations/p15.html solve (2) |
| p15:main | 3 | 기질 수준 인산화이며 여기의 기질은 공간이 아니라 반응 물질을 뜻한다. | substrate-level은 반응물 인산기를 ADP에 직접 전달하는 방식이며 matrix 주소와 무관하다. | (3) 기질 수준 인산화이며 여기의 기질은 공간이 아니라 반응 물질을 뜻한다. — 맞아요. 해당과정은 세포질에서도 반응물의 인산기를 직접 ADP에 넘길 수 있어요. | explanations/p15.html solve (3) |
| p15:main | 4 | 전자전달계가 CO₂를 직접 ATP로 바꾼 것이다. | substrate-level은 반응물 인산기를 ADP에 직접 전달하는 방식이며 matrix 주소와 무관하다. | (4) 전자전달계가 CO₂를 직접 ATP로 바꾼 것이다. — 틀려요. ATP의 인산화는 CO₂를 ATP로 바꾸는 반응이 아니에요. | explanations/p15.html solve (4) |

<!-- p15 sha256=fde37571a7b45eca25ac289ddcdac3679af83f52c92102debddfacb529d57ab2 -->
| p16:main | 1 | 퍼냄: 막 사이 공간에서 기질 / 귀환: 기질에서 막 사이 공간 | 펌프는 기질→막간, 합성효소 경유 귀환은 막간→기질이다. | (1) 퍼냄: 막 사이 공간에서 기질 / 귀환: 기질에서 막 사이 공간 — 틀려요. 퍼내는 방향과 돌아오는 방향을 모두 뒤집었어요. | explanations/p16.html solve (1) |
| p16:main | 2 | 퍼냄과 귀환 모두 ATP 합성효소가 맡는다. | 펌프는 기질→막간, 합성효소 경유 귀환은 막간→기질이다. | (2) 퍼냄과 귀환 모두 ATP 합성효소가 맡는다. — 틀려요. 퍼내기는 전자전달계, 정상적인 ATP 합성과 연결되는 귀환은 ATP 합성효소가 맡아요. | explanations/p16.html solve (2) |
| p16:main | 3 | 퍼냄: 기질에서 막 사이 공간 / 귀환: ATP 합성효소를 거쳐 기질로 | 펌프는 기질→막간, 합성효소 경유 귀환은 막간→기질이다. | (3) 퍼냄: 기질에서 막 사이 공간 / 귀환: ATP 합성효소를 거쳐 기질로 — 맞아요. 내막을 사이에 둔 두 방향과 두 단백질 계를 구분했어요. | explanations/p16.html solve (3) |
| p16:main | 4 | 귀환은 인지질 이중층을 단백질 없이 자유롭게 지난다. | 펌프는 기질→막간, 합성효소 경유 귀환은 막간→기질이다. | (4) 귀환은 인지질 이중층을 단백질 없이 자유롭게 지난다. — 틀려요. 전하를 띤 H⁺는 소수성 지질층을 자유롭게 통과하지 못해요. | explanations/p16.html solve (4) |

<!-- p16 sha256=8c8b32c90b6670df6a2f7a88312f2c62a9699a9838ffb5dcf0ee6460bdb35023 -->
| p17:main | 1 | H⁺가 줄고 pH가 올라간다. | 단기·펌프지속·누출무시 조건에서 막간 H+축적→pH하강→기질과 차이증가이다. | (1) H⁺가 줄고 pH가 올라간다. — 틀려요. 나오는 길이 막힌 채 유입되므로 H⁺는 줄지 않아요. | explanations/p17.html solve (1) |
| p17:main | 2 | H⁺가 늘고 pH가 내려가며 기질과의 pH 차이가 커진다. | 단기·펌프지속·누출무시 조건에서 막간 H+축적→pH하강→기질과 차이증가이다. | (2) H⁺가 늘고 pH가 내려가며 기질과의 pH 차이가 커진다. — 맞아요. H⁺ 축적은 산성화이므로 pH는 내려가고, 기질 쪽과의 차이는 커져요. | explanations/p17.html solve (2) |
| p17:main | 3 | H⁺가 늘고 pH도 올라간다. | 단기·펌프지속·누출무시 조건에서 막간 H+축적→pH하강→기질과 차이증가이다. | (3) H⁺가 늘고 pH도 올라간다. — 틀려요. H⁺ 농도와 pH는 반대로 변해요. | explanations/p17.html solve (3) |
| p17:main | 4 | H⁺가 기질과 즉시 같은 농도가 된다. | 단기·펌프지속·누출무시 조건에서 막간 H+축적→pH하강→기질과 차이증가이다. | (4) H⁺가 기질과 즉시 같은 농도가 된다. — 틀려요. 새는 길을 무시하고 귀환을 막았으므로 즉시 평형화되지 않아요. | explanations/p17.html solve (4) |

<!-- p17 sha256=5d3a4eeee507253578e716dd5910ad8a643d865cc76cb23c259f91f0d8dd8243 -->
| p18:main | 1 | 산화적 ATP 합성은 바로 억제되며 전자전달계 단백질을 직접 막은 것과는 구별한다. | 직접 약물 표적은 ATP synthase H+통로이며 ETC에는 이후 간접 역압 영향이 가능하다. | (1) 산화적 ATP 합성은 바로 억제되며 전자전달계 단백질을 직접 막은 것과는 구별한다. — 맞아요. 직접 표적은 ATP 합성효소이며, 축적된 기울기는 나중에 전자전달에도 영향을 줄 수 있어요. | explanations/p18.html solve (1) |
| p18:main | 2 | 전자전달계의 모든 H⁺ 펌프가 약물에 직접 막혔다. | 직접 약물 표적은 ATP synthase H+통로이며 ETC에는 이후 간접 역압 영향이 가능하다. | (2) 전자전달계의 모든 H⁺ 펌프가 약물에 직접 막혔다. — 틀려요. 약물의 직접 표적을 별개의 H⁺ 펌프까지 확장했어요. | explanations/p18.html solve (2) |
| p18:main | 3 | 전자전달은 어떤 시간이 지나도 반드시 정상 속도로 유지된다. | 직접 약물 표적은 ATP synthase H+통로이며 ETC에는 이후 간접 역압 영향이 가능하다. | (3) 전자전달은 어떤 시간이 지나도 반드시 정상 속도로 유지된다. — 틀려요. 귀환이 막혀 기울기가 커지면 추가 펌핑이 어려워져 전자전달도 느려질 수 있어요. | explanations/p18.html solve (3) |
| p18:main | 4 | ATP 합성효소를 막아도 산화적 ATP 합성은 같은 속도로 유지된다. | 직접 약물 표적은 ATP synthase H+통로이며 ETC에는 이후 간접 역압 영향이 가능하다. | (4) ATP 합성효소를 막아도 산화적 ATP 합성은 같은 속도로 유지된다. — 틀려요. H⁺ 흐름으로 효소를 돌려 ATP를 만드는 경로가 차단돼요. | explanations/p18.html solve (4) |

<!-- p18 sha256=8a02103762d6997a196e7e3337539b946ebafc9ad8d38ff197ef9f3bc2635eae -->

## Item-level answer/verify/sum review
| Item | Blind choice | Content result | Separate verification used |
|---|---|---|---|
| p1:main | 2 | pass; solve/verify/sum concordant | 완성 답과 검산 소거로 확인해요. 기능을 합친 (1), 역할을 뒤바꾼 (3), 밤에 소기관이 없어진다는 (4)를 제외하면 두 기능을 올바르게 나눈 (2)만 남아요. |
| p2:main | 3 | pass; solve/verify/sum concordant | 완성 답과 검산 바깥에서 안으로 경계를 다시 그려 봐요. 셀룰로스 벽을 지난 뒤 인지질 이중층 막을 만나므로, 위치와 재료를 동시에 유지하는 연결은 (3)이에요. |
| p3:main | 2 | pass; solve/verify/sum concordant | 완성 답과 검산 운반자를 먼저 거꾸로 찾아요. ATP를 써서 미세소관 위를 걷는 것은 키네신이므로, 둘째 자리에 키네신이 있고 나머지도 맞는 (2)를 확인할 수 있어요. |
| p4:main | 3 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 1장 p.20–21의 재료와 기능 대응을 다시 대조해요. 튜불린 관련 기능을 묶어 제외하면, 방해받은 액틴과 연결된 근육 수축 (3)이 남아요. |
| p5:main | 1 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 1장 p.14의 염기와 당이 뉴클레오사이드를 이룬다는 구성 관계로 다시 확인해요. ATP에서 인산기 세 개를 구성상 빼고 남는 아데노신에는 아데닌과 리보스가 있어 답은 (1)이에요. |
| p6:main | 3 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 2장 p.32–33의 ATP 가수분해와 합성 방향을 대조해요. 인산기 하나를 잃는 사용 방향의 반대가 ADP에 Pi를 붙이는 합성 방향이므로 답은 (3)이에요. |
| p7:main | 2 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 2장 p.34 그림 2.4에서 결합 전 들어오는 젖당과 방출되는 포도당·갈락토오스를 대조해요. 효소는 남아 다시 작용하므로, 기질은 젖당이고 결합 자리도 효소에 있는 (2)를 확인해요. |
| p8:main | 1 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 2장 p.34의 활성 부위와 기질 결합 원리를 주어진 약물 조건에 적용한 설명이에요. 약물의 작용을 지워 보고도 남는 ‘같은 자리에 들어간다’는 조건과 직접 연결되는 보기는 (1)뿐이에요. 실제 약물 실험을 인용한 것은 아니에요. |
| p9:main | 3 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 2장 p.33–34 그림 2.3에서 반응물·생성물의 높이를 유지한 채 봉우리만 낮아지는 모습을 대조해요. 출발·도착의 차이와 중간 장벽을 분리한 보기는 (3)이에요. |
| p10:main | 2 | pass; solve/verify/sum concordant | 완성 답과 검산 역방향도 확인해요. NADH가 전자를 내주어 NAD⁺가 되는 것은 산화이므로, 이 문제의 반대 변화는 환원이에요. 전자 획득과 환원을 함께 만족하는 보기는 (2) 하나예요. 근거: 교재2장 인쇄36, 37. |
| p11:main | 3 | pass; solve/verify/sum concordant | 완성 답과 검산 반대 극단인 CO₂를 대조해요. 탄소가 이미 많이 산화된 CO₂는 이런 추가 산화의 연료가 되기 어려워요. 출발 연료가 이미 산화되어서 더 많은 에너지가 난다는 (1)의 논리는 거꾸로예요. 네 보기 중 출발 상태와 전자 전달을 함께 설명한 것은 (3)뿐이에요. 근거: 교재1장 인쇄10, 교재2장 인쇄36,39. |
| p12:main | 2 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 그림 2.13에서 전자 화살표의 끝에 O₂와 H₂O가 있는 것을 대조해요. 산소는 전자를 주는 쪽이나 회로에서 나오는 기체가 아니에요. 이 역할을 모두 만족하는 설명은 (2)예요. 근거: 교재2장 인쇄41 그림2.13. |
| p13:main | 4 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 호흡 개관의 경계를 따라 다시 분류해요. 미토콘드리아 밖은 해당과정이고, 내부를 다시 기질과 내막으로 나누면 회로와 전달계가 분리돼요. 모든 대응이 맞는 보기는 (4) 하나예요. 근거: 교재2장 인쇄37–41. |
| p14:main | 1 | pass; solve/verify/sum concordant | 완성 답과 검산 탄소 보존으로 검산해요. 시작 C3은 아세틸기의 C2와 CO₂의 C1로 나뉘어 합계가 3이에요. 세 탄소 모두 CO₂가 되거나 CO₂가 없다는 설명을 제외하면, 직접 ATP 없음까지 맞춘 (1)만 남아요. 근거: 교재2장 인쇄39–40. |
| p15:main | 3 | pass; solve/verify/sum concordant | 완성 답과 검산 장소로 역검사해요. 해당과정이 미토콘드리아 밖에서 이 방식의 ATP를 만든다는 한 사례만으로도 ‘반드시 matrix’라는 (1)은 배제돼요. 직접 전달이라는 조건과 물질 뜻을 모두 보존하는 (3)이 답이에요. 근거: 교재2장 인쇄38 그림2.9, 인쇄40. |
| p16:main | 3 | pass; solve/verify/sum concordant | 완성 답과 검산 교재 그림 2.13의 두 종류 화살표를 대조해요. H⁺ 펌핑은 밖으로, 합성효소 귀환은 안으로 그려져 있어 두 방향을 분리한 (3)만 맞아요. 전자 이동 화살표를 H⁺ 귀환으로 바꾸지 않아요. 근거: 교재2장 인쇄41–42 그림2.13. |
| p17:main | 2 | pass; solve/verify/sum concordant | 완성 답과 검산 부호를 거꾸로 확인해요. 막 사이 공간 pH가 올라간다는 것은 H⁺ 감소를 뜻하지만, 유입은 계속되고 유출은 막혔다는 물질 수지와 충돌해요. 이 모순을 피하고 차이 증가까지 맞춘 것은 (2)예요. 이 결론은 제시한 짧은 구간에만 적용해요. 근거: 교재2장 인쇄41–42 기울기 원리의 조건부 적용; pH관계는 제공 기준. |
| p18:main | 1 | pass; solve/verify/sum concordant | 완성 답과 검산 인과 경로를 다시 그려 검산해요. 통로 차단, 귀환 감소, 산화적 ATP 합성 억제 순서가 먼저예요. 펌프 직접 차단을 추가한 (2), 모든 시간 정상이라 확대한 (3), 합성 유지라는 (4)를 제외하면 (1)만 남아요. 기질 수준 ATP까지 즉시 0이라는 뜻은 아니에요. 근거: 교재2장 인쇄41–42 결합원리의 조건부 추론. |

## Precision checks
- p4 asks direct effect: preserved tubulin structures do not imply zero indirect cellular effect; explanation keeps the direct scope.
- p8 states same-site competition in the problem and does not claim all inhibitors mimic substrates; no experimental drug result is invented.
- p9 preserves ΔG and separates spontaneous direction from activation barrier/speed; no claim of every reaction becoming spontaneous.
- p13 uses 세포질(cytosol) at course simplification level; final note specifies cytoplasmic fluid and matrix/inner membrane distinctions. No answer ambiguity.
- p14 separates pyruvate 1 molecule from glucose 1 molecule, C3=C2+C1 and ATP-direct=0; NADH is not counted as ATP.
- p16 distinguishes protein routes from H+ lipid freedom; ATP synthase route is the ATP-coupled return rather than an absolute claim excluding every leak.
- p17 repeats short observation/pump continues/no other leak assumptions; H+ rise decreases local pH but increases spatial pH difference. p18 distinguishes direct block from delayed ETC slowdown and excludes total cellular ATP=0.
- p10–p18 reference page ranges are broader than exact definitions in some items (NAD+ reduction figure is p38), but general electron definition p36 and final note support the logic; exact source table below supplies precise pages.

## Bound artifact hashes
- source.json: 96b3e6f1fdb2a1d69cda662b802e84537beef744ad24ee1f559acede87e4c82c
- final note: eb86460e0c74655e61a002acfb586a0adb74b2274e5352fbce28cc7b5caab2b6