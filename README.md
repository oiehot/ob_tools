# OB Tools

![](./images/20231209_ob_tools_screenshot.png "OBTools Screenshot")

블렌더를 깊게 이해하고 편리하게 사용하기 위해 만든 Add-on입니다.

주요 기능

* 재귀적 자동 오퍼레이터 클래스 등록.
* 원버튼 파이썬 스크립트 및 Add-on 리로드.
* JSON 형태 웨이트 저장 및 로드.
* 웨이트 페인트를 편하게 하기 위한 모드 스위칭.
* 프로토타입 모델링 편의를 위한 재질 Copy&Paste

...등이 있습니다.

## 설치

1) Preferences > Get Extensions > Add Local Repository

```yaml
Name: OIEHOT Blender Repo
Custom Directory: True, d:/blender
Source: User
Module: oiehot
```

2) 블렌더 익스텐션 저장소 디렉토리로 클론.

```sh
git clone https://github.com/oiehot/ob_tools.git d:/blender/ob_tools
```

3) Preferences > Get Extensions > Refresh Local

4) Installed 에 OB Tools 이 있는 확인하기.

5) Preferences > Add-ons > OB Tools 켜기.

6) 오른쪽 사이드 바에서 OB 탭이 있는지 확인하기.