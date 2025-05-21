# 모두투어 여행 프로젝트

## 프로젝트 소개
이 프로젝트는 여행 계획, 이미지 개선, 블로그 기능을 제공하는 웹 애플리케이션입니다.

## 기술 스택
- Python 3.12
- Django 5.0.2
- OpenCV
- PyTorch
- NAFNet (이미지 개선 모델)

## 설치 방법

### 1. Python 설치
- Python 3.12 버전을 설치합니다.
- 설치 시 "Add Python to PATH" 옵션을 체크합니다.
- [Python 다운로드 페이지](https://www.python.org/downloads/)

### 2. 프로젝트 복사
```bash
# 프로젝트를 원하는 위치에 복사합니다.
git clone [프로젝트_저장소_URL]
cd travel_project_shkim_may28
```

### 3. 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows의 경우:
venv\Scripts\activate
# Linux/Mac의 경우:
source venv/bin/activate
```

### 4. 필요한 패키지 설치
```bash
# requirements.txt에 명시된 패키지들을 설치합니다.
pip install -r requirements.txt
```

### 5. 환경 변수 설정
- 프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다.
- 다음 환경 변수들을 설정합니다:
```
DJANGO_SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
```

### 6. 서버 실행
```bash
# 개발 서버 실행
python manage.py runserver
```
- 서버가 실행되면 `http://127.0.0.1:8000`에서 접속할 수 있습니다.

## 주요 기능
1. 여행 계획
   - 일정 관리
   - 예산 계획
   - 숙소 예약

2. 이미지 개선
   - NAFNet 모델을 사용한 이미지 품질 개선
   - 노이즈 제거
   - 선명도 개선

3. 블로그
   - 여행 후기 작성
   - 이미지 업로드
   - 댓글 기능

## 프로젝트 구조
```
travel_project_shkim_may28/
├── accounts/          # 사용자 계정 관리
├── blog/             # 블로그 기능
├── image_enhance/    # 이미지 개선 기능
├── map/              # 지도 기능
├── travel_input/     # 여행 계획 입력
├── templates/        # HTML 템플릿
├── static/          # 정적 파일
└── media/           # 업로드된 파일
```

## 주의사항
1. 가상환경이 활성화된 상태에서만 서버를 실행해야 합니다.
2. 이미지 개선 기능을 사용하기 위해서는 NAFNet 모델 파일이 필요합니다.
3. 환경 변수는 반드시 `.env` 파일에 설정해야 합니다.

## 문제 해결
- 가상환경 활성화가 안 되는 경우:
  ```bash
  # Windows
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- 패키지 설치 중 오류가 발생하는 경우:
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 