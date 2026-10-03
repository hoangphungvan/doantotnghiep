"""Sinh CV tong hop co kiem soat de mo rong tap gan nhan CV-JD."""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Optional

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import config
from src.extraction.entity_extractor import extract_supported_certifications


GENERATOR_VERSION = "synthetic_cv_generator_v1"
DEFAULT_CLUSTER_FILE = Path(config.DATA_PROCESSED_DIR) / "jd_clusters.csv"
RELATION_LABELS = {
    "strong_match": 3,
    "partial_match": 2,
    "related_hard_negative": 1,
    "unrelated": 0,
}
RELATION_ORDER = tuple(RELATION_LABELS)
CATEGORY_NAMES = (
    "Software Development",
    "Data AI Analytics",
    "IT Infrastructure Security",
    "QA Testing",
    "Design Creative",
    "Sales Marketing",
    "CNC Automation",
)
CATEGORY_KEYWORDS = {
    "Software Development": (
        "developer", "software", "backend", "frontend", "fullstack",
        "java", "python", "javascript", "react", "android", "ios",
        "mobile", "flutter", "web", "spring", "node",
    ),
    "Data AI Analytics": (
        "data", "machine learning", "ai ", "analyst", "analytics",
        "business analyst", "business intelligence", "power bi", "sql",
    ),
    "IT Infrastructure Security": (
        "system", "network", "devops", "cloud", "security", "linux",
        "infrastructure", "it support", "helpdesk", "voip", "cisco",
    ),
    "QA Testing": (
        "tester", "testing", "quality assurance", "qa", "qc", "test case",
    ),
    "Design Creative": (
        "design", "designer", "photoshop", "illustrator", "figma", "3d",
        "unity", "maya", "video", "multimedia", "ui/ux", "ux", "vfx",
    ),
    "Sales Marketing": (
        "sales", "business development", "marketing", "telesales",
        "kinh doanh", "digital marketing", "account", "presales",
    ),
    "CNC Automation": (
        "cnc", "automation", "mastercam", "cad/cam", "cơ khí", "cơ khi",
    ),
}
ADJACENT_CATEGORIES = {
    "Software Development": ("QA Testing", "Data AI Analytics"),
    "Data AI Analytics": ("Software Development", "Sales Marketing"),
    "IT Infrastructure Security": ("Software Development", "QA Testing"),
    "QA Testing": ("Software Development", "IT Infrastructure Security"),
    "Design Creative": ("Software Development", "Sales Marketing"),
    "Sales Marketing": ("Data AI Analytics", "Design Creative"),
    "CNC Automation": ("IT Infrastructure Security", "Software Development"),
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_cluster_names(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {
        row.get("jd_id", ""): row.get("cluster_name", "")
        for row in read_csv_rows(path)
    }


def parse_experience_months(value: str) -> Optional[int]:
    text = (value or "").strip().casefold()
    if not text or "không yêu cầu" in text or "khong yeu cau" in text:
        return None
    numbers = [int(item) for item in re.findall(r"\d+", text)]
    if not numbers:
        return None
    number = max(numbers)
    return number if "tháng" in text or "thang" in text else number * 12


def infer_level(row: dict[str, str]) -> str:
    title = (row.get("job_title") or "").casefold()
    if re.search(r"intern|thực tập|thuc tap|trainee", title):
        return "Intern"
    if re.search(r"fresher|mới tốt nghiệp|moi tot nghiep", title):
        return "Fresher"
    if re.search(r"junior|\bjr\b", title):
        return "Junior"
    if re.search(
        r"senior|\bsr\b|lead|trưởng nhóm|truong nhom|manager|director|head|principal|architect",
        title,
    ):
        return "Senior/Lead"
    months = parse_experience_months(row.get("experience_required", ""))
    if months is None:
        return "Unspecified"
    if months <= 24:
        return "Junior"
    if months <= 48:
        return "Middle"
    return "Senior"


def infer_category(row: dict[str, str], cluster_name: str = "") -> str:
    text = " ".join(
        (row.get("job_title", ""), row.get("technical_skills", ""), cluster_name)
    ).casefold()
    for category in ("CNC Automation", "QA Testing", "Design Creative"):
        if any(keyword in text for keyword in CATEGORY_KEYWORDS[category]):
            return category
    scores = {
        category: sum(keyword in text for keyword in keywords)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    return max(scores, key=scores.get) if max(scores.values()) else "Software Development"


def clean_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def parse_json_response(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fence = chr(96) * 3
    fenced = re.search(fence + r"(?:json)?\s*([\s\S]*?)" + fence, text, re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        text = match.group(0)
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response must be a JSON object")
    return parsed


def normalize_profile(profile: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    result = dict(profile)
    result["headline"] = str(result.get("headline") or fallback["headline"]).strip()
    result["summary"] = str(result.get("summary") or "").strip()
    result["years_of_experience"] = result.get(
        "years_of_experience", fallback["years_of_experience"]
    )
    for field in (
        "roles", "hard_skills", "soft_skills", "education",
        "field_of_education", "industry_sector", "certifications",
    ):
        result[field] = clean_list(result.get(field))
    result["certifications"] = extract_supported_certifications(
        " ".join(result["certifications"])
    )
    result["experience"] = result.get("experience", [])
    result["projects"] = result.get("projects", [])
    if not isinstance(result["experience"], list):
        result["experience"] = []
    if not isinstance(result["projects"], list):
        result["projects"] = []
    return result


def render_cv(profile: dict[str, Any], candidate_id: str) -> str:
    lines = [
        f"HO SO UNG VIEN: {candidate_id}",
        f"TIEU DE: {profile.get('headline', '')}",
        "",
        "TOM TAT NGHE NGHIEP",
        profile.get("summary", ""),
        "",
        "KY NANG CHUYEN MON",
        "- " + ", ".join(profile.get("hard_skills", [])),
        "",
        "KY NANG MEM",
        "- " + ", ".join(profile.get("soft_skills", [])),
        "",
        "KINH NGHIEM LAM VIEC",
    ]
    for item in profile.get("experience", []):
        if isinstance(item, dict):
            title = item.get("title", "Vi tri cong viec")
            company = item.get("company", "Synthetic Company")
            duration = item.get("duration", "")
            detail = item.get("description", "")
            lines.append(f"- {title} | {company} | {duration}")
            if detail:
                lines.append(f"  {detail}")
        else:
            lines.append(f"- {item}")
    lines.extend(["", "DU AN"])
    for item in profile.get("projects", []):
        if isinstance(item, dict):
            name = item.get("name", "Du an ca nhan")
            detail = item.get("description", "")
            skills = ", ".join(clean_list(item.get("skills")))
            lines.append(f"- {name}: {detail}")
            if skills:
                lines.append(f"  Cong nghe: {skills}")
        else:
            lines.append(f"- {item}")
    lines.extend([
        "", "HOC VAN",
        "- " + ", ".join(profile.get("education", [])),
        "- Chuyen nganh: " + ", ".join(profile.get("field_of_education", [])),
        "", "CHUNG CHI",
        "- " + (", ".join(profile.get("certifications", [])) or "Khong co"),
    ])
    return "\n".join(lines).strip() + "\n"


def build_fallback(row: dict[str, str], category: str, level: str, relation: str) -> dict[str, Any]:
    skills = [
        item.strip(" []'\"")
        for item in (row.get("technical_skills") or "").split(",")
        if item.strip(" []'\"")
    ]
    role = row.get("job_title", "IT Professional")
    return {
        "headline": role,
        "summary": f"Ung vien tong hop cho nhom {category}, muc {level}.",
        "years_of_experience": parse_experience_months(row.get("experience_required", "")) or 0,
        "roles": [role],
        "hard_skills": skills[:8],
        "soft_skills": ["Teamwork", "Problem solving"],
        "education": ["Bachelor degree"],
        "field_of_education": ["Information Technology"],
        "industry_sector": ["Information Technology"],
        "certifications": [],
        "experience": [],
        "projects": [],
        "relation_context": relation,
    }


def build_prompt(
    row: dict[str, str],
    category: str,
    level: str,
    relation: str,
    target_category: str,
    candidate_id: str,
) -> str:
    label = RELATION_LABELS[relation]
    skills = (row.get("technical_skills") or "")[:2500]
    requirements = (row.get("requirements_text") or "")[:3000]
    return f"""
Ban la chuyen gia tao du lieu CV tong hop cho nghien cuu xep hang CV-JD.
Hay tao mot candidate profile va CV text bang tieng Viet. Chi tra ve JSON thuan,
khong markdown, khong giai thich ngoai JSON.

Muc dich mau:
- candidate_id: {candidate_id}
- relation_hint: {relation}
- grade_hint: {label}
- category JD goc: {category}
- level JD goc: {level}
- category cua candidate can tao: {target_category}

Quy tac:
1. Day la du lieu tong hop, khong dung ten, email, so dien thoai hay thong tin
   cua nguoi that. Dung candidate_id lam ten hien thi.
2. Khong sao chep nguyen van JD. Khong tao ky nang ngoai ly cho category.
3. strong_match: cung role/category, level gan, co phan lon ky nang cot loi.
4. partial_match: cung hoac gan role, nhung thieu mot so ky nang/kinh nghiem.
5. related_hard_negative: cung nganh rong nhung khac role hoac stack chinh.
6. unrelated: category khac ro rang voi JD.
7. Chung chi chi duoc chon tu danh muc hop le; neu khong chac chan thi de rong.
8. So nam kinh nghiem phai phu hop voi level.
9. Khong dung relation_hint de tu khang dinh nhan ground truth trong CV.

JD tham chieu:
- title: {row.get("job_title", "")}
- technical_skills: {skills}
- experience_required: {row.get("experience_required", "")}
- requirements: {requirements}

JSON bat buoc:
{{
  "profile": {{
    "headline": "...",
    "summary": "...",
    "years_of_experience": 0,
    "roles": ["..."],
    "hard_skills": ["..."],
    "soft_skills": ["..."],
    "education": ["..."],
    "field_of_education": ["..."],
    "industry_sector": ["..."],
    "certifications": ["..."],
    "experience": [
      {{"title": "...", "company": "Synthetic Company", "duration": "...", "description": "..."}}
    ],
    "projects": [
      {{"name": "...", "description": "...", "skills": ["..."]}}
    ]
  }},
  "cv_text": "CV day du, co tieu de va cac muc ro rang"
}}
""".strip()


def select_jds(
    rows: list[dict[str, str]],
    cluster_names: dict[str, str],
    count: int,
    seed: int,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    enriched = []
    for original in rows:
        row = dict(original)
        cluster = cluster_names.get(row.get("jd_id", ""), "")
        row["_category"] = infer_category(row, cluster)
        row["_level"] = infer_level(row)
        buckets[(row["_category"], row["_level"])].append(row)
        enriched.append(row)
    category_pools: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (category, _level), bucket in buckets.items():
        rng.shuffle(bucket)
        category_pools[category].extend(bucket)
    for pool in category_pools.values():
        rng.shuffle(pool)

    selected = []
    # Round-robin theo category de batch nho van co do phu nghe nghiep.
    while len(selected) < count and category_pools:
        progressed = False
        for category in CATEGORY_NAMES:
            pool = category_pools.get(category, [])
            if pool:
                selected.append(pool.pop())
                progressed = True
                if len(selected) >= count:
                    break
            if not pool:
                category_pools.pop(category, None)
        if not progressed:
            break
    if len(selected) < count:
        selected.extend(rng.choices(enriched, k=count - len(selected)))
    return selected


def choose_target_category(source_category: str, relation: str, index: int) -> str:
    if relation in ("strong_match", "partial_match"):
        return source_category
    if relation == "related_hard_negative":
        return ADJACENT_CATEGORIES[source_category][index % 2]
    alternatives = [item for item in CATEGORY_NAMES if item != source_category]
    return alternatives[index % len(alternatives)]


def call_generator(
    client: OpenAI,
    model: str,
    prompt: str,
    temperature: float,
    retries: int,
    retry_wait: float,
) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ban la AI tao du lieu co cau truc. Luon tra JSON hop le.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=3500,
            )
            return parse_json_response(response.choices[0].message.content or "")
        except Exception as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(retry_wait)
    raise RuntimeError(f"LLM generation failed after {retries} attempts: {last_error[:300]}")


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def generate(args: argparse.Namespace) -> int:
    jd_path = Path(args.jd_file)
    cluster_path = Path(args.cluster_file)
    output_dir = Path(args.output_dir)
    if not jd_path.exists():
        raise FileNotFoundError(f"Khong tim thay file JD: {jd_path}")

    rows = read_csv_rows(jd_path)
    cluster_names = load_cluster_names(cluster_path)
    selected = select_jds(rows, cluster_names, args.count, args.seed)
    if not selected:
        raise RuntimeError("Khong chon duoc JD nao de sinh CV")

    plan = []
    for index, row in enumerate(selected):
        relation = RELATION_ORDER[index % len(RELATION_ORDER)]
        category = row["_category"]
        plan.append({
            "candidate_id": f"gen_cv_{args.start_index + index:04d}",
            "source_jd_id": row.get("jd_id", ""),
            "source_job_title": row.get("job_title", ""),
            "source_category": category,
            "source_level": row["_level"],
            "target_category": choose_target_category(category, relation, index),
            "relation_hint": relation,
            "grade_hint": RELATION_LABELS[relation],
        })

    print(f"[INFO] JD source: {len(rows)}")
    print(f"[INFO] CV generation plan: {len(plan)}")
    print("[INFO] Relation distribution:", dict(Counter(item["relation_hint"] for item in plan)))
    print("[INFO] Category distribution:", dict(Counter(item["source_category"] for item in plan)))

    if args.dry_run:
        for item in plan[: min(20, len(plan))]:
            print(
                f"{item['candidate_id']} | {item['relation_hint']} | "
                f"grade_hint={item['grade_hint']} | {item['source_jd_id']} | "
                f"{item['source_category']} -> {item['target_category']}"
            )
        return 0

    if not config.LLM_API_KEY:
        raise RuntimeError(
            "Thieu LLM_API_KEY/GROQ_API_KEY. Hay cau hinh .env hoac dung --dry-run."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.jsonl"
    error_path = output_dir / "errors.jsonl"
    client = OpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        timeout=180.0,
    )
    success = 0
    with manifest_path.open("a", encoding="utf-8") as manifest:
        errors = error_path.open("a", encoding="utf-8")
        try:
            for index, item in enumerate(plan):
                candidate_id = item["candidate_id"]
                json_path = output_dir / f"{candidate_id}.json"
                text_path = output_dir / f"{candidate_id}.txt"
                if not args.force and (json_path.exists() or text_path.exists()):
                    print(f"[SKIP] Da ton tai: {candidate_id}")
                    continue
                row = next(
                    row for row in selected
                    if row.get("jd_id", "") == item["source_jd_id"]
                    and row["_category"] == item["source_category"]
                )
                fallback = build_fallback(
                    row, item["target_category"], item["source_level"], item["relation_hint"]
                )
                prompt = build_prompt(
                    row,
                    item["source_category"],
                    item["source_level"],
                    item["relation_hint"],
                    item["target_category"],
                    candidate_id,
                )
                try:
                    result = call_generator(
                        client, args.model, prompt, args.temperature,
                        args.retries, args.retry_wait,
                    )
                    profile = normalize_profile(result.get("profile", {}), fallback)
                    cv_text = str(result.get("cv_text") or "").strip()
                    if not cv_text:
                        cv_text = render_cv(profile, candidate_id)
                    if len(cv_text) < 200:
                        raise ValueError("Generated CV is too short")

                    record = {
                        **item,
                        "generator_version": GENERATOR_VERSION,
                        "llm_model": args.model,
                        "profile": profile,
                        "cv_text": cv_text,
                    }
                    write_json(json_path, record)
                    text_path.write_text(cv_text + "\n", encoding="utf-8")
                    manifest.write(json.dumps({
                        key: value for key, value in record.items()
                        if key not in {"profile", "cv_text"}
                    }, ensure_ascii=False) + "\n")
                    manifest.flush()
                    success += 1
                    print(f"[OK] {candidate_id} <- {item['source_jd_id']}")
                except Exception as exc:
                    errors.write(json.dumps({**item, "error": str(exc)}, ensure_ascii=False) + "\n")
                    errors.flush()
                    print(f"[ERROR] {candidate_id}: {exc}")
                if index < len(plan) - 1:
                    time.sleep(args.delay_seconds)
        finally:
            errors.close()

    print(f"[DONE] Generated CVs: {success}/{len(plan)}")
    print(f"[INFO] Output: {output_dir}")
    print(f"[INFO] Manifest: {manifest_path}")
    return 0 if success else 1


def build_fallback(
    row: dict[str, str],
    category: str,
    level: str,
    relation: str,
) -> dict[str, Any]:
    skills = [
        item.strip(" []'\"")
        for item in (row.get("technical_skills") or "").split(",")
        if item.strip(" []'\"")
    ]
    role = row.get("job_title", "IT Professional")
    return {
        "headline": role,
        "summary": f"Ung vien tong hop cho nhom {category}, muc {level}.",
        "years_of_experience": parse_experience_months(row.get("experience_required", "")) or 0,
        "roles": [role],
        "hard_skills": skills[:8],
        "soft_skills": ["Teamwork", "Problem solving"],
        "education": ["Bachelor degree"],
        "field_of_education": ["Information Technology"],
        "industry_sector": ["Information Technology"],
        "certifications": [],
        "experience": [],
        "projects": [],
        "relation_context": relation,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sinh CV tong hop co kiem soat tu tap JD IT."
    )
    parser.add_argument("--jd-file", default=config.VIETJOBS_IT_CSV)
    parser.add_argument("--cluster-file", default=str(DEFAULT_CLUSTER_FILE))
    parser.add_argument("--output-dir", default=config.SYNTHETIC_CV_DIR)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model", default=config.LLM_MODEL)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-wait", type=float, default=10.0)
    parser.add_argument("--delay-seconds", type=float, default=2.5)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    if arguments.count <= 0:
        raise SystemExit("--count phai lon hon 0")
    raise SystemExit(generate(arguments))
