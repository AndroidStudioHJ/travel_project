#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

# --- 1) 검색 URL 생성 ---
def build_search_url(query: str) -> str:
    base = "https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_jum&query="
    return base + quote_plus(query)

# --- 2) HTML 가져오기 ---
def fetch_html(url: str, user_agent: str = None) -> bytes:
    headers = {
        "User-Agent": user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
        return res.read()

# --- 3) 포스트 파싱 ---
def parse_posts(html: bytes) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for item in soup.select("ul.lst_view li.bx"):
        a_title = item.select_one("a.title_link")
        if not a_title:
            continue
        title = a_title.get_text(strip=True)
        link = a_title["href"]
        a_desc = item.select_one("a.dsc_link")
        summary = a_desc.get_text(strip=True) if a_desc else ""
        span_date = item.select_one("span.sub")
        date = span_date.get_text(strip=True) if span_date else ""
        
        # 블로그 본문 가져오기
        try:
            blog_html = fetch_html(link)
            blog_soup = BeautifulSoup(blog_html, "html.parser")
            
            # iframe URL 가져오기
            iframe = blog_soup.select_one("iframe#mainFrame")
            if iframe and iframe.get("src"):
                iframe_url = "https://blog.naver.com" + iframe["src"]
                iframe_html = fetch_html(iframe_url)
                iframe_soup = BeautifulSoup(iframe_html, "html.parser")
                
                # 본문 내용 추출
                content_div = iframe_soup.select_one("div.se-main-container")
                if content_div:
                    # 불필요한 요소 제거
                    for element in content_div.select("script, style, .se-section-link"):
                        element.decompose()
                    
                    # 본문 텍스트 추출
                    full_text = content_div.get_text(strip=True)
                else:
                    full_text = summary
            else:
                full_text = summary
        except Exception as e:
            print(f"Error fetching blog content: {e}")
            full_text = summary
        
        posts.append({
            "date": date,
            "title": title,
            "link": link,
            "summary": summary,
            "content": full_text
        })
    return posts

# --- 4) 룰 기반 감성 분석 ---
POSITIVE_KEYWORDS = {
    "좋았", "즐거웠", "행복", "추천", "감동", "최고", "멋졌",
    "만족", "기뻤", "유익", "재미있", "편안", "힐링", "환상",
    "대박", "감탄", "사랑했", "인상적", "즐겼", "훌륭했",
    "깔끔", "청결", "안전했", "풍성", "특별했"
}

NEGATIVE_KEYWORDS = {
    "아쉬웠", "불편", "힘들", "실망", "별로", "싫었",
    "짜증", "지루했", "부족", "답답", "고장", "불만",
    "불친절", "버거웠", "어려웠", "곤란했", "후회", "슬펐",
    "혼잡", "위험", "피곤", "비싸"
}

def rule_sentiment(text: str) -> tuple[str, int, int]:
    positive_count = 0
    negative_count = 0
    
    # 긍정 단어 빈도 계산
    for word in POSITIVE_KEYWORDS:
        count = text.count(word)
        positive_count += count
            
    # 부정 단어 빈도 계산
    for word in NEGATIVE_KEYWORDS:
        count = text.count(word)
        negative_count += count
            
    # 빈도 기반 감성 판단
    if positive_count == negative_count:
        return "neutral", positive_count, negative_count
    elif positive_count > negative_count:
        return "positive", positive_count, negative_count
    else:
        return "negative", positive_count, negative_count

def split_by_sentiment(posts: list[dict]):
    positive = []
    negative = []
    neutral = []
    
    for post in posts:
        sentiment, pos_count, neg_count = rule_sentiment(post["content"])
        post["positive_count"] = pos_count
        post["negative_count"] = neg_count
        
        if sentiment == "positive":
            positive.append(post)
        elif sentiment == "negative":
            negative.append(post)
        else:
            neutral.append(post)
            
    return positive, negative, neutral 