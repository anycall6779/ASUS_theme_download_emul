# ASUS ROG Elysia Theme — Download & Extraction Scripts

ASUS ROG × 붕괴3rd 엘리시아 테마의 **공식 배포 링크 조회, 원본 다운로드, 무결성 검사 및 리소스 추출**에 사용한 Python 스크립트 모음입니다.

이 문서는 **`original_source/`의 다섯 파일만** 설명합니다. 이 코드는 ASUS가 공개한 애플리케이션 원본 소스가 아니라, 테마 확보 과정에서 작성한 조사·다운로드·재현 스크립트입니다.

> **지원 범위:** 현재 코드는 엘리시아 테마 `th01082025001`을 기준으로 작성되었습니다. 모든 ASUS 테마의 다운로드나 복호화를 지원하는 범용 도구가 아닙니다. 원본 확보와 갤럭시 등 다른 기기에서의 테마 적용은 별개의 작업입니다.

## 목차

- [파일 구성](#파일-구성)
- [요구 사항](#요구-사항)
- [빠른 시작: 원본 다운로드 및 검증](#빠른-시작-원본-다운로드-및-검증)
- [선택 사항: 리소스 추출](#선택-사항-리소스-추출)
- [딥링크에서 테마 ID를 찾은 방법](#딥링크에서-테마-id를-찾은-방법)
- [공식 다운로드 주소를 찾은 방법](#공식-다운로드-주소를-찾은-방법)
- [코드별 동작과 실행 조건](#코드별-동작과-실행-조건)
- [최초 조사 스크립트 실행 순서](#최초-조사-스크립트-실행-순서)
- [검증 결과와 한계](#검증-결과와-한계)
- [문제 해결](#문제-해결)

## 파일 구성

```text
.
├── readme.md
└── original_source/
    ├── initial.py
    ├── downloads.py
    ├── get_original.py
    ├── decrypt_modules.py
    └── acquire_verify.py
```

| 파일 | 역할 | 사용 권장 방식 |
|---|---|---|
| [`initial.py`](original_source/initial.py) | 공식 링크 GET/HEAD 및 PC/Android User-Agent 비교, 응답 헤더·본문·DNS 결과 저장 | 딥링크 조회 및 당시 조사 흐름 확인 |
| [`downloads.py`](original_source/downloads.py) | 정적 분석용 APK, JADX 및 참고 웹 응답 다운로드 | 분석 준비 과정 참고용 |
| [`get_original.py`](original_source/get_original.py) | 이미 저장된 카탈로그에서 엘리시아 항목을 찾아 원본 ZIP 다운로드·추출 | 최초 다운로드 코드 보존본 |
| [`decrypt_modules.py`](original_source/decrypt_modules.py) | 추출된 모듈의 AES 외피를 복호화하고 내부 리소스 추출 | 최초 추출 코드 보존본 |
| [`acquire_verify.py`](original_source/acquire_verify.py) | 카탈로그 조회부터 원본 검증·선택적 복호화까지 독립 실행 | **일반 사용자에게 권장하는 진입점** |

`initial.py`, `downloads.py`, `get_original.py`, `decrypt_modules.py`는 당시 작업용 상대 경로를 그대로 사용하는 스크립트입니다. CLI 옵션이나 기존 파일 보호 기능이 없는 부분도 있습니다. 새로 실행할 때는 아래 실행 조건을 먼저 확인하세요.

`acquire_verify.py`는 나머지 네 파일을 호출하는 래퍼가 아니라, 동일 확보 과정을 별도로 정리한 **독립 재현 스크립트**입니다.

## 요구 사항

- Python **3.11 이상**을 기준으로 검증
- HTTPS 인터넷 접속
- 기본 다운로드·검증만 할 경우 Python 표준 라이브러리만 필요
- 선택적 복호화: `pycryptodome`
- 최초 조사 스크립트 중 `initial.py`, `downloads.py`, `get_original.py`: `requests`

이하 명령은 `readme.md`와 `original_source/`가 있는 **저장소 루트**에서 실행합니다. 출력 상대 경로는 스크립트 위치가 아니라 **명령을 실행한 현재 작업 디렉터리**를 기준으로 계산됩니다.

Windows에서는 `python`, 환경에 따라 `py -3` 또는 `python3`를 사용하면 됩니다.

> 기본 실행에는 ROG Phone, 에뮬레이터, ADB, 관리자 권한 또는 ASUS 계정이 필요하지 않습니다. 코드는 APK를 Android에 설치하거나 실행하지 않습니다.

## 빠른 시작: 원본 다운로드 및 검증

```bash
python original_source/acquire_verify.py --out Elysia_Download_01
```

별도 패키지 설치 없이 다음 과정을 수행합니다.

1. ASUS 공식 CDN의 `theme_list.json.gz` 다운로드
2. gzip 해제 및 JSON 파싱
3. `sku_id == th01082025001`인 테마 항목 검색
4. 패키지명이 `com.asus.themes.th01082025001`인지 확인
5. 카탈로그의 다운로드 상대 경로를 코드에 고정한 예상 경로와 비교
6. 원본 파일 다운로드
7. 알려진 정확한 크기와 SHA-256 비교
8. ZIP CRC, 내부 `sku-id`, 선언 모듈 존재 확인
9. 원본과 별도 추출본, HTTP 응답 정보, 목록 및 해시 저장

성공 시 다음과 같은 핵심 메시지가 출력됩니다.

```text
VERIFIED original: th01082025001.zip | 49499531 bytes | SHA256 6f4c68788e5fceccaced1d519d8c9575492a3e83fb7a17e74a1c2fa01743aad0
Declared modules present: 17/17
```

### 출력 폴더

```text
Elysia_Download_01/
├── original/
│   ├── th01082025001.zip
│   └── th01082025001.zip.http.json
├── extracted/
│   ├── AndroidManifest.xml
│   ├── assets/
│   ├── META-INF/
│   └── ...
├── evidence/
│   ├── theme_list.json.gz
│   └── theme_list.json.gz.http.json
├── analysis/
│   ├── catalog_entry.json
│   └── archive_inventory.json
└── SHA256SUMS.txt
```

- `original/`의 ZIP은 HTTP 응답에서 받은 원본 바이트를 그대로 저장합니다.
- `extracted/`는 원본 ZIP에서 꺼낸 별도 파일입니다. 이 단계의 내부 테마 모듈은 아직 원래의 암호화 상태입니다.
- `.http.json`에는 URL, 최종 응답 URL, 상태 코드, 응답 헤더, UTC 시각, 크기 및 SHA-256이 저장됩니다.
- `archive_inventory.json`에는 파일 경로, 크기, ZIP 암호화 플래그 및 CRC가 기록됩니다.
- 다운로드·원본 검증만 해도 외부 ZIP 추출까지 수행합니다. 복호화는 `--decrypt`를 지정해야 실행합니다.

### CLI 옵션

```bash
python original_source/acquire_verify.py --help
```

| 옵션 | 설명 |
|---|---|
| `--out DIRECTORY` | 결과 저장 폴더. 기본값은 `ASUS_ROG_Elysia_Reproduction` |
| `--decrypt` | 원본 검증 후 AES 모듈 복호화와 추출을 추가 실행 |

출력 폴더는 존재하지 않거나 비어 있어야 합니다. 기존 파일이 있으면 오류로 중단합니다. 재실행 시 새 폴더명을 지정하세요.

**이 스크립트에는 `--id`, 이름 검색, 딥링크 입력 옵션이 없습니다.** 테마 ID·다운로드 경로·크기·해시가 엘리시아 원본으로 고정되어 있습니다. 서버에서 파일이 업데이트되면 해시 불일치로 중단하며, 변경된 파일을 기존 원본과 동일하다고 인정하지 않습니다.

다운로드 파일은 크기·해시 검사 전에 저장되므로, 오류가 발생했을 때 파일이 남아 있다는 사실만으로 성공했다고 판단하면 안 됩니다. 최종 성공 메시지와 종료 코드를 확인하세요.

## 선택 사항: 리소스 추출

```bash
python -m pip install pycryptodome
python original_source/acquire_verify.py --out Elysia_Extracted_01 --decrypt
```

복호화 결과는 원본을 덮어쓰지 않고 다음 위치에 추가 저장됩니다.

```text
Elysia_Extracted_01/extracted/
├── assets/                  원본에서 꺼낸 암호화 모듈
├── decrypted_modules/       AES 외피를 제거한 파생 모듈
└── module_resources/        추출 가능한 내부 파일
```

모듈별 파일 목록, 파생 모듈 SHA-256 및 미추출 암호화 엔트리 수는 `analysis/module_inventory.json`에 기록됩니다.

### 복호화 범위

원본 `assets/manifest.json`의 `encryption-key`가 `1`인지 확인하고, 분석한 ASUS Themes 앱의 처리 방식을 재현합니다.

```text
방식: AES-CBC
패딩: PKCS#7 방식의 16바이트 블록 패딩
키: MD5(b'asus1234asus1234')의 16바이트 digest
IV: b'asus#1234'를 뒤쪽 NUL 바이트로 16바이트까지 채운 값
```

앱 쪽 표현은 `AES/CBC/PKCS5Padding`이며, Python에서는 `Crypto.Util.Padding.unpad(..., 16)`을 사용합니다.

이 값은 분석한 ASUS Themes `10.0.0.24_230329`의 `y1.d.h/i/k/q` 및 `y1.w.n(null)` 처리에 근거합니다. **다른 암호화 버전에도 통하는 일반적인 키 복구 기능은 없습니다.** 관련 앱 코드는 버전별로 클래스명·구현이 달라질 수 있으며, 이 저장소의 다섯 스크립트가 해당 역분석을 자동 수행하는 것은 아닙니다.

내부 ZIP 자체에 별도 암호가 있는 엔트리는 건너뛰고 암호화 상태의 파생 모듈을 보존합니다. 이번 파일에서는 레거시 런처가 이에 해당하며, 추가 v2 런처는 정상 추출됩니다.

## 딥링크에서 테마 ID를 찾은 방법

### 1. 공식 제품 페이지의 다운로드 링크 확인

[ASUS 공식 제품 페이지](https://rog.asus.com/protection-and-gadgets/cases-and-protection/rog-hi3-elysia-special-collection/)의 Download Now 링크는 다음 주소였습니다.

```text
https://rog.gg/ROGxHonkai3
```

### 2. 리디렉션을 따라가지 않고 첫 HTTP 응답 확인

`initial.py`는 아래처럼 요청합니다.

```python
r = s.request(
    method,
    u,
    headers={'User-Agent': ua},
    allow_redirects=False,
    timeout=30,
)
```

핵심은 **`allow_redirects=False`로 `Location` 헤더를 직접 보존하는 것**입니다. 당시 응답은 다음과 같았습니다.

```http
HTTP/1.1 302 Found
Location: asusthemes://themes/detail?id=th01082025001
```

| URI 부분 | 의미 |
|---|---|
| `asusthemes://` | ASUS Themes 앱이 처리하는 사용자 정의 URI 스킴 |
| `themes/detail` | 특정 테마 상세 화면 |
| `id=th01082025001` | 엘리시아 테마 ID |

`initial.py`는 이 응답을 저장할 뿐, **ID를 자동 파싱하거나 전체 리디렉션 체인을 따라가지는 않습니다.** 저장된 `initial_http.json`의 `headers.Location`에서 ID를 확인한 후 후속 코드에 반영했습니다.

같은 단축 링크에 대해 GET/HEAD와 PC/Android User-Agent를 비교했고, 당시 네 조합 모두 같은 ID를 반환했습니다. Android User-Agent는 요청 비교용 문자열이며 실제 기기를 인증하거나 에뮬레이션한 것이 아닙니다.

### 3. 빈 웹페이지와 다운로드 실패를 구분

최종 목적지는 `https://` 페이지가 아니라 앱 딥링크입니다. 따라서 URI를 처리할 ASUS 앱이 없는 환경에서 페이지가 표시되지 않는다는 이유만으로 배포 서버가 종료됐다고 볼 수 없습니다.

또 다른 링크인 `https://rog.gg/ROGxHonkai3Elysia`는 테마 파일이 아니라 제품 소개 페이지로 이동했습니다. 두 링크를 구분해 조사했습니다.

### 직접 헤더를 확인하는 보조 명령

Windows PowerShell:

```powershell
curl.exe -I --max-time 25 'https://rog.gg/ROGxHonkai3'
```

Linux/macOS:

```bash
curl -I --max-time 25 'https://rog.gg/ROGxHonkai3'
```

이 확인에서는 `-L` 없이 첫 `Location`을 읽으면 됩니다. `asusthemes://`를 HTTP 다운로드 주소처럼 따라갈 필요는 없습니다.

## 공식 다운로드 주소를 찾은 방법

### 1. ASUS Themes APK의 배포 경로 확인

스토어 앱 패키지는 다음과 같습니다.

```text
com.asus.themeapp
```

분석에 사용한 APK 버전은 `10.0.0.24_230329`였습니다. `downloads.py`는 APK와 JADX 등 분석 준비 파일을 다운로드하는 역할만 합니다. 실제 서명 검사와 JADX 정적 분석은 별도 도구로 수행했으며, 이 스크립트에 자동 분석 기능은 없습니다.

당시 정적 분석으로 확인한 경로:

```text
CDN 기본 주소:
https://dlcdnamaxthemedata.asus.com/Rel/App/

카탈로그 상대 경로:
ThemeData/ThemeApp/theme_list.json.gz
```

[공식 카탈로그](https://dlcdnamaxthemedata.asus.com/Rel/App/ThemeData/ThemeApp/theme_list.json.gz)는 gzip 압축 JSON입니다. `acquire_verify.py`는 이 경로를 알고 있는 상태에서 직접 다운로드합니다.

### 2. 카탈로그에서 딥링크 ID 검색

`get_original.py`가 사용하는 조회 조건:

```python
e = next(x for x in j['data'] if x['sku_id'] == 'th01082025001')
```

해당 항목의 핵심 필드:

```json
{
  "sku_id": "th01082025001",
  "package_name": "com.asus.themes.th01082025001",
  "name": "Honkai 3rd Impact-Elysia (ROG Exclusive skin)",
  "price": false,
  "download_url": "ThemeData/com.asus.themes.th01082025001/th01082025001.zip"
}
```

`com.asus.themeapp`은 스토어 앱이고, `com.asus.themes.th01082025001`이 테마 패키지입니다.

### 3. 카탈로그의 경로를 기본 주소와 결합

```python
u = 'https://dlcdnamaxthemedata.asus.com/Rel/App/' + e['download_url']
```

결과:

```text
https://dlcdnamaxthemedata.asus.com/Rel/App/ThemeData/com.asus.themes.th01082025001/th01082025001.zip
```

[공식 원본 ZIP](https://dlcdnamaxthemedata.asus.com/Rel/App/ThemeData/com.asus.themes.th01082025001/th01082025001.zip)은 당시 HTTP 200으로 다운로드됐습니다. 인증 정보를 사용하거나 기기 제한을 우회한 것이 아니라, 앱이 참조하는 공개 CDN 경로에서 받은 것입니다.

## 코드별 동작과 실행 조건

### `initial.py` — 최초 HTTP 조사

```bash
python original_source/initial.py
```

필요 패키지: `requests`.

고정 출력 루트:

```text
outputs/ASUS_ROG_Elysia_Original/
```

- `original`, `extracted`, `evidence`, `analysis` 폴더 생성
- 단축 링크 2개에 GET/HEAD × PC/Android UA 조합 요청
- 공식 제품 페이지와 Uptodown 참고 페이지는 GET 요청
- 각 응답 본문을 `evidence/*.body`에 저장
- 요청 URL, 상태 코드, 헤더, 수신 바이트 수 또는 오류를 `evidence/initial_http.json`에 저장
- `socket.getaddrinfo('rog.gg', 443)` 결과를 `evidence/dns.json`에 저장 시도

단일 요청 오류는 기록하고 다음 요청으로 진행합니다. 따라서 **프로세스가 끝났다는 것만으로 모든 URL 접근에 성공했다고 판단하면 안 됩니다.** 같은 경로로 재실행하면 기존 로그와 응답 파일을 덮어씁니다.

### `downloads.py` — 분석 준비 파일 확보

```bash
python original_source/downloads.py
```

필요 패키지: `requests`. 실행 전 `work/`와 `outputs/ASUS_ROG_Elysia_Original/evidence/`가 있어야 합니다.

최대 4개 작업을 병렬로 실행해 다음 자료를 저장합니다.

| 대상 | 저장 위치 |
|---|---|
| Uptodown 다운로드 JavaScript | `work/uptodown_download_js.txt` |
| APKMirror 페이지 응답 | `work/apkmirror.txt` |
| APKPure의 ASUS Themes APK 요청 응답 | `work/themeapp.apk` |
| JADX 1.5.6 배포 ZIP | `work/jadx.zip` |

요청 메타데이터는 `evidence/*_request.json`에 저장합니다.

**주의 사항:**

- HTTP 오류 상태도 응답 본문을 저장합니다. `.apk`나 `.zip` 확장자만 보고 정상 파일이라고 판단하지 마세요.
- `raise_for_status()`, APK 서명 검증, JADX 실행 또는 설치 기능은 없습니다.
- APKPure 요청은 `version=latest`입니다. 현재 내려오는 파일이 당시 분석한 버전과 동일하다고 보장하지 않습니다.
- Uptodown JavaScript 등 일부 주소는 당시 버전의 고정 주소라 나중에 변경·삭제될 수 있습니다.
- 개별 작업 오류를 출력하고 계속 진행하므로 각 HTTP 상태와 파일 형식을 별도로 확인해야 합니다.
- 기존 파일을 덮어쓸 수 있습니다.

### `get_original.py` — 최초 원본 다운로드

```bash
python original_source/get_original.py
```

필요 패키지: `requests`.

선행 파일:

```text
outputs/ASUS_ROG_Elysia_Original/evidence/theme_list.json.gz
```

`initial.py`와 `downloads.py`는 **이 카탈로그를 다운로드하지 않습니다.** 아래 최초 조사 실행 순서에 카탈로그를 준비하는 보조 명령을 명시했습니다.

동작:

1. 저장된 카탈로그를 gzip 해제하고 JSON 파싱
2. 엘리시아 `sku_id` 항목 조회
3. `analysis/elysia_catalog_entry.json` 저장
4. `download_url`로 원본 요청, HTTP 오류 시 중단
5. 원본 ZIP과 응답 헤더·크기·SHA-256 저장
6. ZIP 엔트리 목록과 CRC 검사 결과 출력
7. 추출 경로가 추출 루트 밖으로 나가지 않는지 확인 후 추출

이 스크립트는 SHA-256을 **계산만 하며 고정된 정답 해시와 비교하지 않습니다.** 또한 `testzip()` 결과를 출력하지만 그 반환값이 오류 파일명인지 별도 분기로 중단하지는 않습니다. 크기·해시·내부 ID·선언 모듈 검증을 엄격하게 재현하려면 `acquire_verify.py`를 사용하세요.

재실행하면 원본과 분석 결과를 덮어쓸 수 있습니다.

### `decrypt_modules.py` — 최초 복호화·추출

```bash
python original_source/decrypt_modules.py
```

필요 패키지: `pycryptodome`.

선행 입력:

```text
outputs/ASUS_ROG_Elysia_Original/extracted/assets/
```

고정 AES 키·IV로 `.apk`, `.zip` 모듈을 복호화해 파생 모듈을 저장합니다. 내부 ZIP에 암호화 엔트리가 **하나라도 있으면 해당 모듈 전체의 내용 추출과 CRC 검사를 건너뜁니다.** 나머지는 CRC 검사 후 추출하며 목록을 `analysis/decrypted_module_inventory.json`에 저장합니다.

`acquire_verify.py`의 `unpack()`은 이와 달리 엔트리별로 암호화 여부를 보고 추출 가능한 엔트리를 처리합니다. 두 구현의 세부 동작과 JSON 구조가 완전히 같지는 않습니다.

기존 파생 파일은 덮어쓸 수 있고, 복호화 실패 시 예외로 중단합니다. 보고서의 `crc_tested=false`이면 `bad_crc=null`이어도 **CRC 검사 통과를 뜻하지 않습니다.**

### `acquire_verify.py` — 독립 재현용 권장 코드

위 빠른 시작에 설명한 독립 실행 파일입니다. 최초 스크립트의 카탈로그 선행 파일 없이 실행할 수 있고, 기존 출력 폴더를 보호하며, 고정 크기·해시·내부 ID·모듈 존재를 검사합니다.

다만 이 파일에도 다음 기능은 없습니다.

- 임의 테마 ID 입력 또는 테마 이름 검색
- 딥링크 조회 및 자동 ID 연결
- APK 서명 검사 자동화
- 다운로드 재개 및 자동 재시도
- 별도 ZIP 암호 복구
- 명시적인 다운로드 용량 제한
- Android 설치, 테마 적용 또는 다른 제조사 포맷 변환

`fetch()`는 응답 전체를 메모리로 읽어 저장하므로 대용량 임의 파일을 처리하는 스트리밍 다운로더가 아닙니다. 예외 발생 시 `ERROR: ...`를 stderr에 출력하고 종료 코드 1을 반환합니다. 정상 종료는 0입니다.

## 최초 조사 스크립트 실행 순서

이 절은 처음 사용한 네 스크립트의 실행 의존성을 설명하기 위한 것입니다. **원본을 다시 받는 목적이라면 위의 `acquire_verify.py` 한 번 실행으로 충분합니다.** 두 경로를 같은 출력 폴더에서 이어 실행하지 마세요.

각 명령은 비어 있는 별도 작업 복사본의 저장소 루트에서 실행합니다.

### 1. 의존성 설치 및 작업 폴더 생성

```bash
python -m pip install requests pycryptodome
python -c "from pathlib import Path; Path('work').mkdir(exist_ok=True)"
```

### 2. 딥링크 응답 수집

```bash
python original_source/initial.py
```

`outputs/ASUS_ROG_Elysia_Original/evidence/initial_http.json`에서 `shortA` 요청의 `headers.Location`을 확인합니다.

### 3. 선택적으로 분석 준비 파일 다운로드

```bash
python original_source/downloads.py
```

이 단계는 이미 알려진 CDN 경로로 원본을 받는 데 필수는 아닙니다. APK·JADX 확보 과정까지 재현하려는 경우에만 수행합니다. 서명 검사·디컴파일은 별도 도구 작업입니다.

### 4. 원본 다운로드 스크립트에 필요한 카탈로그 준비

다음은 최초 작업 당시 별도로 수행했던 카탈로그 다운로드를 재현하는 **보조 명령**입니다. `get_original.py`에 내장된 동작은 아닙니다.

```bash
python -c "from pathlib import Path; import urllib.request; p=Path('outputs/ASUS_ROG_Elysia_Original/evidence/theme_list.json.gz'); p.parent.mkdir(parents=True, exist_ok=True); r=urllib.request.urlopen('https://dlcdnamaxthemedata.asus.com/Rel/App/ThemeData/ThemeApp/theme_list.json.gz', timeout=120); p.write_bytes(r.read()); r.close()"
```

### 5. 원본 다운로드 및 외부 ZIP 추출

```bash
python original_source/get_original.py
```

### 6. 선택적으로 내부 모듈 복호화

```bash
python original_source/decrypt_modules.py
```

이 경로는 역사적 작업 스크립트를 그대로 사용하는 방식이므로, 자동 고정 해시 비교와 기존 파일 보호는 제공하지 않습니다.

## 검증 결과와 한계

### 확인한 원본

2026-11-05에 확보·검증한 파일 기준입니다. 미래의 서버 상태를 보장하는 값은 아닙니다.

| 항목 | 결과 |
|---|---|
| 원본 파일명 | `th01082025001.zip` |
| 테마 ID | `th01082025001` |
| 테마 패키지 | `com.asus.themes.th01082025001` |
| 정확한 크기 | **49,499,531바이트** |
| 외부 ZIP 엔트리 | 41개 |
| 선언 모듈 존재 | 17/17 |
| 추가 v2 런처 포함 모듈 파일 수 | 18개 |

SHA-256:

```text
6f4c68788e5fceccaced1d519d8c9575492a3e83fb7a17e74a1c2fa01743aad0
```

원본 ZIP CRC 검사와 빈 폴더에서의 재다운로드 해시 일치를 확인했습니다. 이 문서 작성 시 새 라이브 네트워크 검사를 추가 수행한 것은 아니며, 위 결과는 기존 확보·재현 작업의 기록입니다.

### 주요 추출 리소스

`extracted/module_resources/`를 기준으로 다음 구성을 확인했습니다.

| 구성 | 확인한 파일 |
|---|---|
| 잠금화면 | `com.android.systemui.lockscreen/res/raw/asus_lockscreen_wallpaper_video.mp4` |
| 수신 화면 | `com.asus.asusincallui/res/raw/asus_incallui_video.mp4` |
| 충전 애니메이션 | `com.android.systemui.charging/res/drawable-nodpi-v4/asus_rog_charging_loop_000.webp`부터 `059.webp`까지 60프레임 |
| AniMe Vision | `com.asus.miniled/res/raw/`의 GIF 3종 |
| 보조 디스플레이 | `com.asus.seconddisplay/res/raw/asus_sd_screen_on.gif` |
| 효과음 | `com.asus.sound/res/raw/`의 OGG 6종 |
| AOD | `com.asus.alwayson/`의 배경 및 상태 아이콘 |
| 런처 | `com.asus.v2.launcher/`의 아이콘·배경·메타데이터 89개 엔트리 |

`com.asus.livewallpaper` 모듈 자체에는 WebP 배경 이미지 2개가 들어 있었습니다. 이 사실을 잠금화면 동영상과 혼동하여, 별도의 홈 화면 MP4까지 확보했다고 주장하지 않습니다.

### 남아 있는 암호화

레거시 `com.asus.launcher.zip`의 내부 89개 엔트리는 별도 ZIP 암호가 남아 있어 내용 CRC 검사·추출을 완료하지 않았습니다. 해당 파일은 원본과 파생 모듈에 그대로 보존됩니다. 추가 v2 런처의 89개 엔트리는 정상 추출했습니다.

이는 공식 원본 ZIP의 일부 파일이 누락됐다는 뜻이 아니라, 보존한 내부 데이터 일부를 아직 평문으로 꺼내지 못했다는 의미입니다.

### 서명 검증은 별도 작업

최초 확보 시 Android SDK `apksigner`로 원본 패키지의 v1/v2/v3 서명을 검증했습니다. 스토어 APK와 테마 패키지의 인증서 SHA-256은 다음 값으로 일치했습니다.

```text
9af9497bec4a32a8aa069dc20b0e773a866b8055d2af6bfca77e234a3a2b2193
```

**이 서명 검증은 다섯 Python 코드에 포함되어 있지 않습니다.** 도구가 설치된 환경에서는 별도로 다음과 같이 확인할 수 있습니다.

```bash
apksigner verify --verbose --print-certs Elysia_Download_01/original/th01082025001.zip
```

Windows SDK 설치 방식에 따라 `apksigner.bat`를 사용해야 할 수 있습니다. 서명자 표시 이름만으로 신뢰성을 판단하지 말고 공식 출처·카탈로그·내부 ID·인증서 지문을 함께 확인하세요.

### 기기 호환성

- 실제 ROG Phone에서 적용·재생하는 테스트는 수행하지 않았습니다.
- Galaxy S25 Ultra에서 ASUS 테마 전체를 적용하는 기능은 제공하지 않습니다.
- 충전 화면·AOD·수신 화면·AniMe Vision은 ASUS 시스템 앱이나 지원 하드웨어에 의존할 수 있습니다.
- 다른 테마가 공개 CDN에서 인증 없이 제공되거나 같은 포맷·암호화를 사용한다고 보장하지 않습니다.
- 유료 구매나 인증을 우회하는 기능은 없습니다.

## 문제 해결

| 증상 | 확인할 사항 |
|---|---|
| `Output directory must be empty` | `acquire_verify.py`의 기존 출력 보호 동작. 새 폴더명을 지정하세요. |
| `No module named requests` | 최초 조사 스크립트를 실행한다면 `python -m pip install requests`가 필요합니다. 기본 `acquire_verify.py`에는 필요하지 않습니다. |
| `No module named Crypto` | 복호화 실행 시 `python -m pip install pycryptodome`을 사용하세요. |
| 카탈로그 `FileNotFoundError` | `get_original.py` 실행 전 카탈로그를 준비했는지 확인하거나 독립 재현 코드를 사용하세요. |
| `StopIteration` | 카탈로그에 고정 ID가 없습니다. 목록 변경·배포 종료·형식 변경 여부를 확인하세요. |
| `Original has changed` | 크기 또는 고정 SHA-256이 불일치합니다. 새 버전인지 검토하기 전 동일 원본으로 취급하지 마세요. |
| `Catalog download path changed` | 공식 카탈로그의 상대 경로가 예상 경로와 달라졌습니다. 코드 상수를 임의로 바꾸기 전에 출처와 파일을 검토하세요. |
| `BadZipFile` | HTML 오류 응답, 불완전 다운로드 또는 다른 포맷일 수 있습니다. HTTP 기록과 파일을 확인하세요. |
| 패딩·AES 오류 | 모듈 손상 또는 다른 암호화 방식일 수 있습니다. `encryption-key=1` 지원 범위를 확인하세요. |
| 403/404·DNS·TLS 오류 | 서버 접근, 네트워크 또는 배포 경로가 달라졌을 수 있습니다. 이 코드에는 인증·배포 종료 우회 기능이 없습니다. |

다운로드한 APK·ZIP을 신뢰하거나 실행하기 전에 응답·형식·해시·서명을 확인하세요. GitHub에 게시할 때는 Python 소스와 이 문서를 중심으로 구성하고, APK·상용 리소스·개인 작업 경로가 포함된 로컬 로그는 별도로 검토하세요. 이 스크립트 공개가 ASUS·HoYoverse 리소스의 재배포 권한을 의미하지는 않습니다.
