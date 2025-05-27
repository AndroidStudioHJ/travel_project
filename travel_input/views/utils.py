import os
import openai
import requests
from django.conf import settings

def summarize_text_with_openai(text):
    """
    OpenAI API를 사용해 입력 텍스트를 한국어로 3줄로 요약합니다.
    환경변수 OPENAI_API_KEY 필요.
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        return 'OpenAI API 키가 설정되어 있지 않습니다.'
    openai.api_key = api_key
    prompt = (
        "아래 내용을 한국어로 3줄로 요약해줘. "
        "각 줄은 줄바꿈(\\n)으로 구분해서 출력해줘. "
        "반드시 3줄로 만들어줘.\n"
        f"{text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"요약 실패: {e}"

def naver_search_blog(query, display=3):
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {
        "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        print("네이버 응답:", response.status_code, response.text)
        if response.status_code == 200:
            return response.json().get('items', [])
    except Exception as e:
        print("네이버 API 예외:", e)
    return []

def summarize_with_openai(text):
    try:
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "아래 내용을 한국어로 간단하게 여행 팁으로 요약해줘."},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception:
        return text 