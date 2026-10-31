# 收藏檔案 · Collection Archive

私人藏品數碼目錄 —— 錢幣、紙幣、郵票、手錶、化石、礦石。

**公開站**：`index.html` · **管理台**：`admin.html`

---

## 收錄規則（程式強制，非人手勾選）

| 真偽狀態 | 代碼 | 公開？ |
|---|---|---|
| ✅ 真品（目視可確認） | `genuine` | 會公開 |
| ⏳ 待確認（需額外認證） | `pending` | 會公開，標「待確認」、隱藏價格 |
| ❌ 仿真／假貨 | `replica` | **永遠私人** |
| 🌿 天然未處理 | `natural` | 會公開 |
| ⚗️ 有處理（染色／加熱／填充） | `treated` | 會公開，會註明方式 |
| ❌ 拼接／人造 | `composite` | **永遠私人** |

`data/public.json` 只由 `admin.html` 以**欄位白名單**匯出，
`gate_check.py` 每次發佈前再驗一次：私人狀態、私人欄位、base64 內嵌相片一律擋。

## 檔案結構

```
index.html            公開目錄（SPA，hash 路由）
admin.html            管理台（本機編輯 + 一鍵發佈上線）
data/public.json      公開資料（白名單匯出）
data/schema.json      六大分類欄位定義
data/vault.enc.json   AES-GCM-256 加密完整備份（含私人筆記／買入價／序號）
photos/               相片（最長邊 1600 px WebP）
gate_check.py         真偽閘門檢查
manifest.webmanifest  PWA
sw.js                 Service Worker（離線可用）
```

## 管理台用法

1. iPhone Safari 開 `admin.html` → 分享 → 加入主畫面
2. 「＋ 新增物件」→ 揀分類 → 影相 → 填規格（密度會自動計）
3. 🔒 真偽判定：揀錯都唔怕，私人狀態唔會漏出公開檔
4. 「👁 公開預覽」睇清楚邊件會公開、邊件擋住
5. 「📤 發佈上線」→ 上載相片 → public.json → 加密 vault

### 一次性設定（發佈需要）
GitHub → Settings → Developer settings → Personal access tokens →
**Fine-grained tokens** → Generate new token：

- Repository access：Only select repositories → `collection`
- Permissions → Contents：**Read and write**
- 生成後貼入「📤 發佈上線」頁

Token 只存喺你部電話嘅 `localStorage`，唔會上載。

## 本機測試

```bash
cd collection-site
python -m http.server 8899
# 開 http://localhost:8899/index.html
#     http://localhost:8899/admin.html
python gate_check.py
```

⚠️ 唔可以用 `file://` 開 —— WebCrypto（`crypto.subtle`）同 fetch 都會被瀏覽器封鎖。

## 資料安全

- 本機：`localStorage`（你部電話，已有鎖屏保護）
- 雲端：`data/vault.enc.json` 用 AES-GCM-256 + PBKDF2-SHA256（310,000 次迭代）加密
- **忘記 vault 密碼 = 解唔開雲端備份**（本機資料仍在），請寫落密碼管理器
- 定期用「💾 備份」下載 JSON 放去另一處

## 出處

錢幣資料來自 2026-10-31 已核實報告，每一項規格／價格均標明來源；
未能確認嘅一律寫「待確認」，**唔作估算**。
真偽由收藏者本人判定，**AI 唔會定真偽，亦唔會認錢文**。
