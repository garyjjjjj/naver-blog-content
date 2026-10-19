# 개발·수정 관리

원고와 이미지는 저장소의 `posts/`, 관리 프로그램은 `app/`에서 관리합니다. 뮤즈가 글의 구성·문체·분량·이미지 배치를 결정합니다.

## 수정 순서

1. 저장소 최신 상태를 가져오고 `app/` 파일만 수정합니다.
2. 아래 테스트를 실행하고 필요한 검증 결과를 `CHANGELOG.md`에 기록합니다.
3. 동작·연결 상태가 바뀌면 `docs/STATUS.md`와 사용 안내도 수정합니다.
4. `git diff --check`와 변경 파일 목록을 검토하고 코드·문서만 커밋합니다.
5. 공개 발행 기능은 실제 발행/수정/이미지 결과 대조 시험 전까지 활성화하지 않습니다.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r app/requirements.txt
.venv/Scripts/python -m unittest discover -s app/tests -v
```

DPAPI와 Windows 실행 관련 테스트가 있어 Windows에서 검증합니다. 네이버 계정이나 실제 게시글을 변경하는 테스트는 현재 테스트 모음에 없습니다.

## 실행 파일 만들기

```powershell
.venv/Scripts/python -m pip install pyinstaller==6.22.3
$source = (Resolve-Path app).Path
.venv/Scripts/python -m PyInstaller --noconfirm --onedir --windowed --name BlogManager --distpath build --workpath .build --specpath .build --paths $source --add-data "$source/web;web" --add-data "$source/config.json;." --add-data "$source/setup-autostart.ps1;." "$source/manager.py"
```

`app/install-local.ps1 -BuildDir build/BlogManager`로 바탕화면에 설치할 수 있습니다. 브라우저는 설치된 Google Chrome을 우선 사용합니다. 실행 중 파일은 덮어쓰지 말고 해당 관리자와 로그인 하위 프로세스를 정상 종료한 뒤 갱신합니다. 설치와 부팅 등록은 각각 Windows 로컬 설정을 바꿉니다.

`config.json`은 공개 가능한 기본 설정이며, 실제 설정·인증 상태는 사용자 로컬 데이터 폴더에서 관리합니다. GitHub 업로드는 명시한 소스 파일만 허용합니다. 바탕화면 폴더 전체나 AppData 폴더를 업로드하지 않습니다.
