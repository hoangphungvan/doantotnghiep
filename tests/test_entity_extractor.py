"""
Self-check phần không cần LLM của entity_extractor: tách preferred_skills và cache có phiên bản prompt.
Chạy: python tests/test_entity_extractor.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.extraction import entity_extractor as ee

raw = '{"hard_skills": ["Java", "SQL"], "role": ["Backend"], "preferred_skills": ["ReactJS", "Docker"], "junk": ["x"]}'
e = ee._parse_entities(raw)
assert e["hard_skills"] == ["Java", "SQL"] and e[ee.PREFERRED_KEY] == ["ReactJS", "Docker"]
assert set(config.ENTITY_TYPES) <= set(e) and "junk" not in e                 # đủ 6 loại, bỏ khóa lạ
assert ee._parse_entities("không phải JSON")[ee.PREFERRED_KEY] == []           # lỗi parse vẫn đúng cấu trúc
assert ee._parse_entities('<think>{x}</think>{"role": ["BA"]}')["role"] == ["BA"]

ee._entity_cache = {}                                                         # cache giả, không ghi ra đĩa
ee._entity_cache["abc"] = {"role": ["cũ"]}                                     # khóa kiểu cũ (prompt cũ) không được dùng lại
assert ee.get_cached_entity("abc") is None
ee.set_cached_entity("abc", {"role": ["mới"]}, save=False)
assert ee.get_cached_entity("abc") == {"role": ["mới"]} and f"{ee.ENTITY_PROMPT_VERSION}:abc" in ee._entity_cache
print("all entity_extractor self-checks passed")
