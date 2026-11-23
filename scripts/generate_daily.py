#!/usr/bin/env python3
"""Generate a source-grounded Chinese Europe tech/business briefing and append it safely."""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "editions.json"
API_URL = "https://api.openai.com/v1/responses"
MODEL = os.getenv("OPENAI_MODEL", "gpt-6.2-sol")
TODAY = os.getenv("EDITION_DATE") or datetime.now(ZoneInfo("Europe/Warsaw")).date().isoformat()

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "intro": {"type": "string"},
        "articles": {
            "type": "array", "minItems": 5, "maxItems": 5,
            "items": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "category": {"type": "string"},
                    "published_at": {"type": "string"},
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "key_takeaway": {"type": "string"},
                    "industry_analysis": {"type": "string"},
                    "europe_impact": {"type": "string"},
                    "watch_signal": {"type": "string"},
                    "source_name": {"type": "string"},
                    "source_url": {"type": "string"},
                    "secondary_source_name": {"type": ["string", "null"]},
                    "secondary_source_url": {"type": ["string", "null"]},
                    "image_url": {"type": ["string", "null"]},
                    "image_alt": {"type": ["string", "null"]},
                    "image_caption": {"type": ["string", "null"]},
                    "image_source_name": {"type": ["string", "null"]},
                    "image_source_url": {"type": ["string", "null"]}
                },
                "required": [
                    "category", "published_at", "title", "summary",
                    "key_takeaway", "industry_analysis", "europe_impact",
                    "watch_signal", "source_name", "source_url",
                    "secondary_source_name", "secondary_source_url",
                    "image_url", "image_alt", "image_caption",
                    "image_source_name", "image_source_url"
                ]
            }
        }
    },
    "required": ["title", "intro", "articles"]
}

INSTRUCTIONS = """
你是欧洲科技与商业研究编辑。请通过 web_search 搜索并核实指定日期的新闻，
生成中文《欧洲科技商业日报》。日期按 Europe/Warsaw 当地日期。只选最重要的5条，
优先过去24小时发布、且与欧洲市场有实质关联的事件；不足时可用近期仍在发展的
重要事件，但必须保留真实发布日期。覆盖消费电子/手机/平板/PC/穿戴/音频、
AI与科技/机器人/Physical AI/半导体供应链、全球商业财经、国际与地缘政治。
主动扫描行业，不要只围绕固定品牌；重点留意Apple、Samsung、Huawei、Xiaomi、
Honor、Transsion、OPPO/OnePlus、Google、Meta、Microsoft、Nvidia、欧洲本土厂商、
运营商、零售渠道及监管机构，但绝不为了覆盖品牌凑数。
每条都必须有可打开的原始报道或官方来源 URL。不要编造事件、日期、数字、引语、
来源或网址；无法独立确认的内容不要入选。尽量用官方公告/监管文件/公司公告/
Reuters/FT/Bloomberg/主流专业媒体交叉核验。将事实与分析分开；明确区分已生效、
提案、计划、传闻和预测。不要把市场份额上升误写成销量增长。不能验证的图片字段
全部填 null；只有找到确切图片文件直链并能确认它与新闻相关时才填写 image_url。
图片来源 URL 必须真实。不要使用搜索结果缩略图猜测图片地址。
每条中文内容要有实质信息和分析，不写空泛套话：
summary说明事实、数字、时间、涉及主体和事件状态；
key_takeaway提炼商业信号；
industry_analysis分析产业链/竞争格局/战略意义；
europe_impact说明欧洲国家、渠道、定价、合规或供应链影响，联系消费电子生态；
watch_signal给出后续可验证指标/事件。
标题简洁准确。文章分类用以下之一或相近中文分类：消费电子、AI与科技、
商业与财经、国际与地缘政治、半导体、能源与商业。
输出严格符合给定 JSON Schema，不要在 JSON 外输出说明。
"""

def fail(message):
    print("ERROR:", message, file=sys.stderr)
    raise SystemExit(1)

def extract_output_text(response):
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks = []
    for item in response.get("output", []):
        for part in item.get("content", []):
            if part.get("type") in ("output_text", "text") and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    return "\n".join(chunks)

def main():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        fail("Missing GitHub Actions secret OPENAI_API_KEY. Add it in Settings > Secrets and variables > Actions.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", TODAY):
        fail(f"Invalid edition date: {TODAY}")

    existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    editions = existing.get("editions", [])
    if any(e.get("date") == TODAY for e in editions):
        print(f"Edition {TODAY} already exists; refusing to overwrite history.")
        return

    payload = {
        "model": MODEL,
        "instructions": INSTRUCTIONS,
        "input": (
            f"请为 {TODAY}（Europe/Warsaw）制作日报。使用 web_search 检索最新新闻，"
            "优先过去24小时。先核验来源和发布日期，再筛选最重要5条。"
        ),
        "tools": [{"type": "web_search", "search_context_size": "high"}],
        "tool_choice": "auto",
        "max_output_tokens": 12000,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "europe_daily_briefing",
                "strict": True,
                "schema": SCHEMA
            }
        }
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as res:
            response = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fail(f"OpenAI API HTTP {exc.code}: {detail[:3000]}")
    except Exception as exc:
        fail(f"OpenAI API request failed: {exc}")

    if response.get("status") not in (None, "completed"):
        fail(f"OpenAI response status is {response.get('status')}: {response.get('incomplete_details')}")
    output = extract_output_text(response)
    if not output:
        fail("Model returned no structured output.")
    try:
        edition = json.loads(output)
    except json.JSONDecodeError as exc:
        fail(f"Model output is not valid JSON: {exc}")

    articles = edition.get("articles")
    if not isinstance(articles, list) or len(articles) != 5:
        fail("Expected exactly five articles.")
    required_text = [
        "category", "published_at", "title", "summary", "key_takeaway",
        "industry_analysis", "europe_impact", "watch_signal", "source_name", "source_url"
    ]
    for i, article in enumerate(articles, 1):
        for field in required_text:
            if not isinstance(article.get(field), str) or not article[field].strip():
                fail(f"Article {i} missing required field: {field}")
        if not re.match(r"^https://", article["source_url"]):
            fail(f"Article {i} has no HTTPS source URL.")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", article["published_at"]):
            fail(f"Article {i} has invalid publication date.")
        for field in ("image_url", "image_source_url"):
            value = article.get(field)
            if value is not None and not value.startswith("https://"):
                article[field] = None
        if article.get("image_url") and not article.get("image_source_url"):
            article["image_url"] = None
            article["image_alt"] = None
            article["image_caption"] = None
            article["image_source_name"] = None

    new_edition = {
        "date": TODAY,
        "title": edition.get("title") or f"欧洲科技商业日报｜{TODAY}",
        "intro": edition.get("intro", ""),
        "articles": articles
    }
    editions.insert(0, new_edition)
    existing["schema_version"] = existing.get("schema_version", 1)
    existing["updated_at"] = datetime.now(ZoneInfo("Europe/Warsaw")).isoformat(timespec="seconds")
    existing["editions"] = editions
    DATA_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validated and appended {TODAY}: {len(articles)} articles; total archive editions: {len(editions)}")

if __name__ == "__main__":
    main()
