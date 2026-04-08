"""Deterministic SEO scoring engine powered by BeautifulSoup."""

from __future__ import annotations

import re
from typing import Dict, List

from bs4 import BeautifulSoup

try:
    from .models import SeoScoreBreakdown
except ImportError:  # pragma: no cover
    from models import SeoScoreBreakdown


def _safe_text(soup: BeautifulSoup) -> str:
    return " ".join(soup.stripped_strings).lower()


def _count_keyword(text: str, keyword: str) -> int:
    pattern = rf"\b{re.escape(keyword.lower())}\b"
    return len(re.findall(pattern, text))


def evaluate_seo_html(html: str, keyword: str) -> SeoScoreBreakdown:
    """Evaluate SEO quality and return a deterministic 0-100 score."""
    soup = BeautifulSoup(html, "html.parser")
    issues: List[str] = []
    component_scores: Dict[str, float] = {
        "title": 0.0,
        "meta_description": 0.0,
        "headings": 0.0,
        "alt_attributes": 0.0,
        "keyword_usage": 0.0,
        "semantic_html": 0.0,
        "html_validity": 0.0,
    }

    # 1) Title scoring (max 20)
    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        title_text = title_tag.get_text(strip=True)
        title_len = len(title_text)
        if 10 <= title_len <= 60:
            component_scores["title"] = 20.0
        elif 6 <= title_len <= 75:
            component_scores["title"] = 12.0
            issues.append("Title exists but length is suboptimal (recommended 10-60).")
        else:
            component_scores["title"] = 6.0
            issues.append("Title length is poor for SEO.")
    else:
        issues.append("Missing <title> tag.")

    # 2) Meta description (max 20)
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc.get("content", "").strip()
        desc_len = len(desc)
        if 50 <= desc_len <= 160:
            component_scores["meta_description"] = 20.0
        elif 30 <= desc_len <= 180:
            component_scores["meta_description"] = 12.0
            issues.append("Meta description exists but length is suboptimal (recommended 50-160).")
        else:
            component_scores["meta_description"] = 6.0
            issues.append("Meta description length is poor for SEO.")
    else:
        issues.append("Missing meta description tag.")

    # 3) Heading hierarchy (max 20)
    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    if len(h1_tags) == 1:
        heading_score = 12.0
        if h2_tags:
            heading_score += 8.0
        else:
            issues.append("No <h2> subheadings found.")
        component_scores["headings"] = heading_score
    elif len(h1_tags) == 0:
        issues.append("Missing <h1> heading.")
    else:
        component_scores["headings"] = 6.0
        issues.append("Multiple <h1> tags found; use one primary heading.")

    # 4) Image alt attributes (max 15)
    images = soup.find_all("img")
    if not images:
        component_scores["alt_attributes"] = 15.0
    else:
        with_alt = 0
        for img in images:
            alt_text = (img.get("alt") or "").strip()
            if alt_text:
                with_alt += 1
        ratio = with_alt / len(images)
        component_scores["alt_attributes"] = round(15.0 * ratio, 2)
        if ratio < 1.0:
            issues.append("Some images are missing descriptive alt text.")

    # 5) Keyword usage (max 15)
    all_text = _safe_text(soup)
    keyword_count = _count_keyword(all_text, keyword)
    if keyword_count == 0:
        issues.append(f"Keyword '{keyword}' does not appear in page content.")
    elif 1 <= keyword_count <= 5:
        component_scores["keyword_usage"] = 15.0
    elif 6 <= keyword_count <= 8:
        component_scores["keyword_usage"] = 10.0
        issues.append("Keyword appears too frequently; possible keyword stuffing.")
    else:
        component_scores["keyword_usage"] = 4.0
        issues.append("Severe keyword stuffing detected.")

    # 6) Semantic HTML (max 5)
    semantic_tags = ["main", "article", "section", "nav", "header", "footer"]
    present = sum(1 for name in semantic_tags if soup.find(name) is not None)
    component_scores["semantic_html"] = round(5.0 * (present / len(semantic_tags)), 2)
    if present < 2:
        issues.append("Limited semantic HTML usage (main/article/section/nav/header/footer).")

    # 7) Basic validity checks (max 5)
    has_html = soup.find("html") is not None
    has_body = soup.find("body") is not None
    if has_html and has_body:
        component_scores["html_validity"] = 5.0
        is_valid_html = True
    else:
        component_scores["html_validity"] = 0.0
        is_valid_html = False
        issues.append("HTML structure is invalid: missing <html> or <body>.")

    total = round(sum(component_scores.values()), 2)
    normalized = round(total / 100.0, 4)

    return SeoScoreBreakdown(
        total_score=total,
        normalized_score=normalized,
        component_scores=component_scores,
        issues=issues,
        is_valid_html=is_valid_html,
    )
