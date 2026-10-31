# -*- coding: utf-8 -*-
"""真偽閘門自動檢查 —— 任何一次發佈前／CI 都要跑。

用法：python gate_check.py
通過 exit 0，發現問題 exit 1（可以掛入 GitHub Actions 做 pre-deploy gate）。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(ROOT, "data", "public.json")
SCH = os.path.join(ROOT, "data", "schema.json")

# 永遠唔可以出現在公開檔嘅真偽狀態
BANNED_AUTH = {"replica", "composite"}
# 永遠唔可以出現在公開檔嘅欄位（白名單以外全部算漏）
PRIVATE_FIELDS = ["notes_private", "purchase_price", "acquired_from", "location",
                  "serial_no", "valuation_private", "case_no"]

fails, warns = [], []

if not os.path.exists(PUB):
    print("[GATE] FAIL 找唔到 data/public.json")
    sys.exit(1)

doc = json.load(open(PUB, encoding="utf-8"))
items = doc.get("items", [])
schema = {}
if os.path.exists(SCH):
    schema = json.load(open(SCH, encoding="utf-8"))

# 1. 逐件檢查真偽狀態
for it in items:
    a = it.get("authenticity")
    if a in BANNED_AUTH:
        fails.append("公開檔含私人藏品：%s（%s）狀態=%s" % (it.get("id"), it.get("name"), a))
    if not a:
        warns.append("未標真偽狀態：%s（%s）" % (it.get("id"), it.get("name")))

# 2. 私人欄位洩漏
for it in items:
    for f in PRIVATE_FIELDS:
        if f in it:
            fails.append("私人欄位洩漏：%s.%s = %r" % (it.get("id"), f, it[f]))
    sp = it.get("spec") or {}
    for f in PRIVATE_FIELDS:
        if f in sp:
            fails.append("私人欄位洩漏（spec）：%s.spec.%s" % (it.get("id"), f))

# 3. 相片檔案存在？
missing = []
for it in items:
    for ph in it.get("photos", []) or []:
        if str(ph).startswith("data:"):
            fails.append("公開檔含 base64 內嵌相片（未上載成檔案）：%s" % it.get("id"))
            continue
        if not os.path.exists(os.path.join(ROOT, "photos", ph)):
            missing.append("%s → photos/%s" % (it.get("id"), ph))
if missing:
    fails.append("相片檔缺失：" + "; ".join(missing))

# 4. 分類合法性 + 公開資格
ok_auth = {}
for c in schema.get("categories", []):
    ok_auth[c["key"]] = set(c.get("auth_ok", []))
for it in items:
    cat = it.get("category")
    if cat not in ok_auth:
        warns.append("未知分類：%s（%s）" % (it.get("id"), cat))
    elif it.get("authenticity") not in ok_auth[cat]:
        fails.append("分類 %s 唔接受狀態 %s：%s（%s）"
                     % (cat, it.get("authenticity"), it.get("id"), it.get("name")))

# 5. meta 計數一致
if doc.get("meta", {}).get("count") not in (None, len(items)):
    fails.append("meta.count=%s 但實際 %d 件" % (doc["meta"]["count"], len(items)))

print("=== 真偽閘門檢查 ===")
print("公開藏品：%d 件" % len(items))
print("私人擋住：%d 類狀態禁止公開 → %s" % (len(BANNED_AUTH), ", ".join(sorted(BANNED_AUTH))))
for w in warns:
    print("  [WARN]", w)
for f in fails:
    print("  [FAIL]", f)
if fails:
    print("\n結果：❌ 唔准發佈（%d 項問題）" % len(fails))
    sys.exit(1)
print("\n結果：✅ 通過 —— 零私人藏品、零私人欄位漏出")
