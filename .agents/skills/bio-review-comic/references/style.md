# 공통 그림체: 플랫 일러스트

인물·생물 구조·과정·비유 사물을 모두 같은 플랫 일러스트풍으로 그린다. 둥글고 또렷한 남색 윤곽선, 단순하고 구별하기 쉬운 형태, 머스터드·청록·남색 중심의 면색, 밝은 아이보리 배경을 사용한다. 표정은 친근하고 읽기 쉽게, 사물은 작동 관계가 선명하게 보이게 한다. 질감·음영은 형태를 보조하는 약한 수준으로 제한한다. 수채화 번짐·거친 종이 질감·입체 클레이 렌더링을 공통 스타일에 섞지 않는다. 같은 차수에서 인물 비율·선 굵기·색의 역할을 유지한다.

`storyboard.json`의 `style`은 다음을 기본으로 하고 해당 차수의 반복 대상 약속을 덧붙인다.

```text
Unified flat editorial illustration for a Korean biology learning comic. Clear rounded navy outlines, simplified readable shapes, mostly solid matte mustard yellow, muted teal and navy fills on a clean pale ivory background. Friendly expressive human characters; equally clear object-only and scientific scenes in the same visual language. Minimal soft shading and subtle texture only; no watercolor washes, heavy paper grain or 3D clay rendering. Preserve scientific counts, boundaries, directions and spatial relationships while simplifying shapes. Consistent recurring subjects, line weight and color roles. Landscape composition with the TOP 40% empty for HTML dialogue and ALL essential objects in the LOWER 60%. No text, labels, speech bubbles or inner panel border in the image. No faces or human features on biological structures or objects.
```

## 확인하고 사용할 스타일 참조

아래 파일은 스킬 안에 보존한 승인 시안이다. 생성자는 담당 장면과 가까운 실제 파일을 열어 보고 이미지 도구에 **그림체 참조**로 전달한다. 참조의 장면·출연자·소품을 이번 컷에 추가하지 않는다. 반복 대상의 외형을 유지할 이전 컷도 있다면 두 참조의 역할을 구별한다. 작업자에게는 필요한 참조의 절대 경로만 전달한다.

- [인물](../assets/style/flat-people.png): 둥근 윤곽선·표정·옷의 면색.
- [생물 구조](../assets/style/flat-structure.png): 외피와 내부 요소를 구별하는 형태·색.
- [과정](../assets/style/flat-process.png): 막·통로·입자의 관계를 읽기 쉽게 표현하는 방식.
- [비유 사물](../assets/style/flat-objects.png): 인물 없이 소품의 상태와 관계를 보여 주는 방식.

시안은 과학적 근거나 완성 컷이 아니다. 구조·개수·연결·작동 상태는 매번 원본과 콘티로 검증한다. 시안의 DNA 고리 모양이나 소품 배치를 표준 구조로 복제하지 않는다. 시안의 여백도 복제하지 않고 각 생성 결과에서 상단 40% 확보와 실제 말풍선 가림을 확인한다.

## 이전 실행 재사용

`extract --reuse`는 이전 `style`도 가져온다. 콘티 작성 단계에서 현재 공통 그림체로 갱신하고 `prompts`를 다시 실행한다. 스타일 변경은 프롬프트 지문과 이미지 재사용·검토를 무효화하므로 이전 수채화풍 이미지를 새 플랫 컷에 섞지 않는다. 기존 발행 만화는 별도 재생성 요청이 있을 때 새 RUN에서 갱신한다.
