# 사용자 직접 작업 가이드 (Stage 1 v2)

> **목적**: Custom bot 페이퍼 트레이딩 + 라이브 운영 전 사용자가 직접 수행해야 하는 계정/키/인프라 설정
> **블로킹 여부**: **아니오**. Claude의 V2-01 ~ V2-04 구현과 **병행 진행 가능**. V2-05 integration test 시점까지만 준비되면 됨 (수일 여유).
> **작성일**: 2026-04-24
> **실측 기반** (cycle 1 #16 재발 방지): 업비트 Help Center + 공식 docs 실측. 미확인 정보는 명시.

---

## 한눈에 보기 — 전체 사용자 작업 요약

| # | 작업 | 소요 (추정) | Claude 블로킹 | 비고 |
|---|------|:-----------:|:-------------:|------|
| 1 | 업비트 계정 + 본인인증 + 2FA | 수 시간~1일 | V2-05 필요 | 2FA 필수 (공식 확인) |
| 2 | K뱅크 계좌 + 업비트 연동 | 30분~1일 | V2-07 필요 | K뱅크 독점 (공식 확인) |
| 3 | Open API 키 발급 (페이퍼 권한 2개) | 10분 | V2-05 필요 | PC 웹 전용 |
| 4 | Keychain 저장 (Access/Secret) | 5분 | V2-05 필요 | `security` 명령 |
| 5 | 고정 IP 확보 | 즉시 확인 or 수일 | V2-06 필요 | 동적 IP면 대응 필요 |
| 6 | Discord 서버 + webhook URL | 10분 | V2-04 권장 | 알림용 |
| 7 | Claude에게 완료 보고 | 1분 | - | Keychain 저장 확인 + IP 공유 |

**Claude 작업 일정**:
- V2-02 (3~5일): market_data + state + logger — **병행 가능**
- V2-03 (3~5일): strategy + order — **병행 가능**
- V2-04 (2~3일): scheduler + main + notifier — Discord webhook 권장 (mock 가능)
- **V2-05 (3~5일): integration test — API 키 필수 (블로킹)**
- V2-06 (2~4주): 페이퍼 트레이딩 — 전부 완료 필수

**권장 순서**: 오늘~수일 내 1+2+3+4 완료 → Claude V2-04 즈음 6 완료 → V2-05 전 5 확인 → 7 보고.

---

## 체크리스트 (순서대로 진행)

- [ ] **1단계**: 업비트 계정 생성 + 본인인증 + 2FA 설정
- [ ] **2단계**: 케이뱅크(K뱅크) 계좌 개설 + 업비트 연동
- [ ] **3단계**: 업비트 Open API 키 발급 (페이퍼 단계 권한만)
- [ ] **4단계**: Access/Secret Key → macOS Keychain 저장
- [ ] **5단계**: 고정 IP 확보 (동적 IP면 대응 방안 검토)
- [ ] **6단계**: Discord 서버 + webhook URL 발급
- [ ] **7단계**: Claude에게 완료 보고 (준비된 정보 전달)

---

## 1단계 — 업비트 계정 + 본인인증 + 2FA

### 1.1 회원가입

- URL: https://upbit.com/signup
- 이메일 + 비밀번호로 기본 가입

### 1.2 본인인증

- 휴대폰 본인 인증 (통신사 or PASS 앱)
- 신분증 확인 (주민등록증/운전면허증/여권 중 하나)

### 1.3 2채널 인증 (2FA) 설정 **필수**

- 업비트 공식에 따라 API Key 발급은 **2채널 인증 완료 후** 가능
- 옵션:
  - 카카오페이 인증 (권장, 간편)
  - OTP 앱 (Google Authenticator 등)

### 1.4 소요 시간

- **공식 안내 없음** (실측 못함). 일반적으로 수 시간 ~ 영업일 기준 1일 예상
- 주말/공휴일 지연 가능

---

## 2단계 — K뱅크 계좌 + 업비트 연동

### 2.1 K뱅크 독점 정책 (공식 확인)

업비트 고객센터 공식 답변:
> "케이뱅크 입출금 계좌만 인증 가능하며 다른 은행 계좌로는 인증 불가합니다."

→ 카카오뱅크 / 국민은행 / 신한은행 등 **전부 불가**.

### 2.2 K뱅크 계좌 개설

- K뱅크 앱 다운로드 (Android / iOS)
- 앱 내 "계좌 개설" → 신분증 + 본인인증
- 소요: 보통 10~30분 (앱 내 완료)

### 2.3 업비트 K뱅크 연동

- 업비트 웹/앱에서 "원화 입출금" 메뉴
- K뱅크 계좌 실명확인 인증
- 1원 송금 인증 등의 확인 절차

### 2.4 소액 입금 (선택)

- 페이퍼 단계는 실제 입금 불필요
- 10만원 라이브 전환 시점에 K뱅크 → 업비트 입금 수행
- 지금 미리 할 필요 없음

---

## 3단계 — Open API 키 발급

### 3.1 선결 조건 (공식 확인)

- ✓ 회원가입 완료
- ✓ 본인인증 완료
- ✓ **2채널 인증 (2FA) 설정 완료**
- ✓ **PC 웹 접속** (모바일 앱 불가)

### 3.2 발급 경로

1. PC 웹 브라우저로 https://upbit.com 로그인
2. 우측 상단 프로필 → **마이 페이지**
3. 좌측 메뉴 → **Open API 관리**
4. "Open API 사용 신청" 또는 "새 키 발급" 클릭
5. 공식 docs 참조: https://docs.upbit.com/kr/docs/api-key

### 3.3 권한 선택 (페이퍼 단계, 2개만)

실측된 권한 종류 (5개):

| 권한 | 페이퍼 단계 | 비고 |
|------|:-----------:|------|
| **잔고 조회** | ✓ | 자산 확인용 |
| **주문 조회** | ✓ | 내 주문 상태 확인용 |
| 주문하기 | ✗ | 페이퍼는 실제 주문 안 함 |
| 출금 조회 | ✗ | 봇 운영에 불필요 |
| **출금하기** | ✗ (**절대 금지**) | 보안 위험 — 봇에 절대 부여 X |

**라이브 전환 시 (10만원 투입 단계)**:
- "주문하기" 권한 **추가** (시장가/지정가 매수·매도)
- "출금하기"는 **영구 금지** 유지

### 3.4 허용 IP 등록 (필수)

- **최소 1개 이상 등록 필수** (공식 확인)
- API Key 하나당 최대 10개 IP
- 계정당 최대 10개 API Key (총 100 IP 조합)

**현재 IP 확인 방법**:
```bash
curl ifconfig.me
```

결과로 나온 IPv4 주소 (예: `211.xx.xx.xx`)를 허용 IP 란에 등록.

### 3.5 Access Key + Secret Key 저장

발급 완료 화면에서:
- **Access Key**: 화면에 표시 (공식 형식 미공개 — 발급 후 직접 확인)
- **Secret Key**: **최초 화면에서만 확인 가능** (공식 확인). 화면 떠나면 **재조회 불가** → 즉시 복사 + 안전한 곳 저장

**⚠️ 긴급 주의**:
- Secret Key 분실 시 해당 키 삭제 후 새 키 발급 필요
- Secret Key 유출 주의 (화면 녹화 금지, 스크린샷 공유 금지, GitHub 실수 commit 금지)

---

## 4단계 — macOS Keychain 저장

### 4.1 저장 명령 (Terminal)

```bash
security add-generic-password -s "upbit-api-access" -a "coin-bot" -w "<ACCESS_KEY_발급받은값>"
security add-generic-password -s "upbit-api-secret" -a "coin-bot" -w "<SECRET_KEY_발급받은값>"
```

`<ACCESS_KEY_발급받은값>` / `<SECRET_KEY_발급받은값>` 자리에 실제 키 값 치환.

### 4.2 저장 확인

```bash
security find-generic-password -s "upbit-api-access" -a "coin-bot" -w
security find-generic-password -s "upbit-api-secret" -a "coin-bot" -w
```

각 명령 결과로 저장한 키 값이 출력되면 성공.

### 4.3 삭제 (필요 시)

```bash
security delete-generic-password -s "upbit-api-access" -a "coin-bot"
security delete-generic-password -s "upbit-api-secret" -a "coin-bot"
```

---

## 5단계 — 고정 IP 확보

### 5.1 동적 IP vs 고정 IP 확인

현재 IP가 고정인지 확인:
- 집 인터넷 공유기 설정 페이지 (보통 `192.168.0.1` or `192.168.1.1`) → WAN IP 확인
- 며칠 간격으로 `curl ifconfig.me` 실행 → 값 변경 여부 관찰
- 대부분 한국 가정 인터넷 = **동적 IP**

### 5.2 동적 IP인 경우 대응 방안

| 방안 | 장단점 |
|------|--------|
| **통신사 고정 IP 서비스** | 월 약 5,000~10,000원. 가장 안정적 |
| **VPN 고정 IP (유료)** | Mullvad/NordVPN 등 static IP 옵션. 업비트에서 VPN 차단할 가능성 존재 (실측 필요) |
| **클라우드 서버** (AWS Lightsail 등) | 고정 IP 무료. 봇 호스팅 별개. 월 $3.5부터. v1 박제 "macOS 24/7"과 충돌 |
| **업비트 IP 주기 갱신** | IP 바뀔 때마다 수동으로 업비트 허용 IP 수정. 24/7 자동 운영과 맞지 않음 |

### 5.3 권장

- 1순위: 통신사 고정 IP 서비스
- 2순위: macOS 24/7 대신 클라우드 서버로 호스팅 변경 (v1 decisions-final.md 재박제 필요)

**현 상태 확인만 먼저** 하고, 동적 IP면 나중에 결정해도 V2-05 단계까지는 문제 없음.

---

## 6단계 — Discord 서버 + webhook URL 발급

### 6.1 Discord 계정 + 앱 준비

- https://discord.com 가입 (무료)
- 데스크톱 앱 또는 웹 모두 가능

### 6.2 Discord 서버 생성 (개인용)

1. 좌측 사이드바 맨 아래 `+` 버튼 클릭
2. **"직접 만들기"** 선택
3. **"나와 친구를 위한 서버"** 선택
4. 서버 이름: `coin-bot` (원하는 이름)
5. 서버 아이콘 업로드 (선택)
6. "만들기" 클릭

### 6.3 알림 채널 생성

1. 좌측 채널 목록 상단 `+` → **텍스트 채널**
2. 채널 이름: `bot-alerts` (또는 `알림`)
3. "채널 만들기" 클릭

### 6.4 webhook URL 발급

1. 방금 만든 `#bot-alerts` 채널 옆 **톱니바퀴 (채널 편집)** 클릭
2. 좌측 메뉴 → **연동 (Integrations)**
3. **"웹후크 만들기"** 또는 **"Webhooks → 새 웹후크"** 클릭
4. webhook 이름: `coin-bot` (기본값 유지 가능)
5. 프로필 사진: 원하는 이미지 설정 (선택)
6. **"웹후크 URL 복사"** 클릭 — 클립보드에 복사됨
7. URL 형식: `https://discord.com/api/webhooks/<숫자-id>/<랜덤-토큰>` (약 120자)

**⚠️ webhook URL = 비밀**: 유출 시 누구나 해당 채널에 메시지 게시 가능. 관리 주의.

### 6.5 Keychain 저장

```bash
security add-generic-password -s "discord-webhook" -a "coin-bot" -w "<WEBHOOK_URL>"
```

`<WEBHOOK_URL>` 자리에 복사한 전체 URL 붙여넣기.

### 6.6 테스트 메시지 전송

Terminal에서:

```bash
WEBHOOK_URL=$(security find-generic-password -s "discord-webhook" -a "coin-bot" -w)
curl -H "Content-Type: application/json" \
  -d '{"content":"🤖 coin-bot 테스트 메시지"}' \
  "$WEBHOOK_URL"
```

Discord `#bot-alerts` 채널에 "🤖 coin-bot 테스트 메시지" 출력되면 성공. 출력 안 되면 webhook URL 재확인.

### 6.7 모바일 알림 설정 (권장)

- Discord 모바일 앱 설치 (iOS/Android)
- 로그인 → `coin-bot` 서버 진입
- `#bot-alerts` 채널 설정 → **"알림 설정"** → **"모든 메시지"** 선택
- 밤중에도 체결/에러 알림 즉시 확인 가능

### 6.8 webhook 용량 제한 (참고)

- Discord 공식 rate limit 수치는 응답 헤더 (`X-RateLimit-*`) 기반 **동적**. 고정 숫자는 공식 docs에 명시 안 됨. 정확한 수치는 실제 사용 시 헤더 확인 (정정 2026-04-24: 이전 버전 "초당 5회" 수치 실측 근거 없어 제거)
- 본 봇 알림은 하루 수회 (일봉 시그널 + 주문 체결) = 여유 예상
- 과도한 알림 방지: 에러는 10분 간격 디바운스 (V2-04 notifier 설계에 반영 예정)
- webhook rate limit 도달 시 429 응답 + `Retry-After` 헤더 따라 대기 구현 필요

---

## 7단계 — Claude에게 완료 보고

### 7.1 알려줄 것

다음 정보를 Claude 대화에 공유:

1. **완료 단계 체크**: 어느 단계까지 완료했는지 (1~6 중)
2. **IP 상태**: 고정 IP 확보 여부
3. **현재 IP 주소**: `curl ifconfig.me` 결과 (업비트 허용 IP와 일치 확인용)
4. **주의사항 확인**: Secret Key 저장 완료 + 출금 권한 미부여 확인
5. **Discord 테스트**: webhook 테스트 메시지 성공 여부

### 7.2 공유 금지 (보안)

- ❌ Access Key 전체 값
- ❌ Secret Key 전체 값
- ❌ Discord webhook URL 전체 값

이들은 Keychain에만 저장하고, Claude에게는 **Keychain 저장 완료 확인**만 알려주면 됩니다.

### 7.3 단계별 블로킹 여부

| Claude 작업 | 사용자 필요 단계 | 블로킹? |
|-------------|------------------|---------|
| V2-01 (engine/ + venv + config) | 없음 | ✗ 병행 가능 |
| V2-02 (market_data + state + logger) | 없음 (market_data는 public API) | ✗ 병행 가능 |
| V2-03 (strategy + order 모듈) | 없음 (mock 기반 test) | ✗ 병행 가능 |
| V2-04 (scheduler + main + notifier) | 6단계 Discord webhook 권장 | △ 권장 (필수 X, mock 가능) |
| V2-05 (integration test) | 3~4단계 API 키 **필수** | ✓ **블로킹** |
| V2-06 (페이퍼 트레이딩 시작) | 1~5단계 **전부 완료 필수** | ✓ **블로킹** |
| V2-07 (10만원 라이브) | K뱅크 입금 + 주문하기 권한 추가 | ✓ **블로킹** |

**권장 일정**:
- 오늘 ~ 수일 내: 1~4단계 (업비트 계정 + API 키 발급)
- 수일 내 여유: 5~6단계 (고정 IP + Discord)
- Claude는 V2-01 ~ V2-04 병행 진행 (약 2주 예상)
- V2-05 시점 (~2주 후) 준비 완료되면 무리 없음

---

## 세법 고지

### 가상자산 소득세 (2025 시행)

- 연간 가상자산 양도차익 **250만원 초과분에 22% 과세**
- 50만원 한정 라이브로 단기 250만원 초과 어렵지만 장기 누적 주의
- 모든 거래 내역은 봇 DB에 영구 저장됨 (CLAUDE.md 박제). 연말 신고 시 활용

### 세금 신고 의무

- 매년 5월 종합소득세 신고 시 가상자산 소득 별도 구분
- 자세한 내용은 국세청 상담 (126) or 세무사 상담 권장

---

## 미확인 정보 (사용자가 실제 화면에서 확인 필요)

실측으로 확정 못한 항목 (공식 공개 정보 없음):

1. **KYC 소요 시간**: 공식 안내 없음. 실제 신청 후 알림 대기
2. **Access/Secret Key 형식**: 공식 미공개. 발급 시 화면에서 확인
3. **자동매매 봇 운영 약관**: 공식 Open API 약관 전문 확인 못함. 사용자가 업비트 약관 페이지 직접 검토 권장
4. **2FA 구체 방식**: 카카오페이 vs OTP 앱 선택 가능 여부 실측 못함

이들은 실제 절차 중 확인하고 Claude에게 알려주시면 가이드 보강하겠습니다.

---

## 참고 URL

- [업비트 공식 docs - API Key 발급](https://docs.upbit.com/kr/docs/api-key)
- [업비트 Help Center - 케이뱅크 독점](https://support.upbit.com/hc/ko/articles/4407462429081)
- [업비트 Help Center - 원화 입금](https://support.upbit.com/hc/ko/articles/900006733926)
- [업비트 Open API 관리 (로그인 필요)](https://www.upbit.com/mypage/open_api_management)
- [Discord Webhook 공식 가이드](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

---

End of user setup guide. Generated 2026-04-24.
