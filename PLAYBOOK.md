# 實驗操作手冊(PM 用)

角色代號:**PM** = 你,**A** = 協作者 A,**B** = 協作者 B。
`<you>` 換成你的 GitHub 帳號。每個 ⭐ 是報告要截圖/存檔的證據點。

整體配置(一次涵蓋 A/E/O 等級要求):

| 實驗 | 衝突類型 | A 的 PR | B 的 PR | 額外證據 |
|---|---|---|---|---|
| E1 | 同檔同行(硬衝突) | Merge commit | 解衝突後 **Squash** | `git rerere` 自動重用解法 |
| E2 | 同檔不同行 | **Rebase & merge** | rebase 後 **Rebase & merge** | CI 擋下的 PR(3.10 失敗)+ `git range-diff` |
| E3 | 不同檔案 | **Squash** | **Fast-forward**(PM 推送,SHA 不變) | pre-push 腳本擋非 FF |

---

## 0. 建置(PM)

```bash
# 1) 解壓後進入資料夾
cd activity-log
git init -b main && git add . && git commit -m "chore: initial project with CI"

# 2) 在 GitHub 建立 private repo「activity-log」(網頁或 gh 皆可)
gh repo create activity-log --private --source . --push
#   或:git remote add origin git@github.com:<you>/activity-log.git && git push -u origin main

# 3) 本機安裝 hook + rerere(在第一次 push 之後再裝)
./scripts/install-hooks.sh
```

到 **Actions** 頁籤確認第一次執行成功 ⭐(截圖:lint → test(3.10/3.11/3.12) → build → ci-passed 全綠)。

**邀請協作者**:Settings → Collaborators → Add people → A、B,權限 Write。

**合併方式**:Settings → General → Pull Requests → 勾選 ✅ Allow merge commits ✅ Allow squash merging ✅ Allow rebase merging。

**分支保護**:Settings → Branches → Add classic branch protection rule(或 Rulesets),Branch name pattern `main`:

- ✅ Require a pull request before merging(Required approvals 設 1,由 PM 審核)
- ✅ Require status checks to pass → 搜尋並加入 **`ci-passed`**
  - ✅ Require branches to be up to date before merging(讓「需要先更新分支」的情況出現,報告可討論 CI 對合併時機的影響)
- ⬜ Require linear history(**不要勾**)
- ⬜ Do not allow bypassing the above settings(**不要勾**:E3 的 fast-forward 需要 PM 以管理者身分推送)
- 不勾 Allow force pushes / Allow deletions

⭐ 截圖整個保護規則頁面。

**協作者端**(請 A、B 各做一次):

```bash
git clone git@github.com:<you>/activity-log.git && cd activity-log
./scripts/install-hooks.sh
```

---

## E1 — 同檔同行(硬衝突)

兩人都改 `activity_log/core.py` 的 **`APP_NAME` 那一行**。

**A**:
```bash
git switch -c e1/rename-a
# 把 APP_NAME = "Activity Log" 改成:
#   APP_NAME = "Team Activity Log"
git commit -am "feat(e1): rename app to Team Activity Log"
git push -u origin e1/rename-a     # 開 PR,標題前綴 [E1-A]
```

**B**(同時做,從同一個 main 分出):
```bash
git switch -c e1/rename-b
#   APP_NAME = "Activity Tracker"
git commit -am "feat(e1): rename app to Activity Tracker"
git push -u origin e1/rename-b     # 開 PR [E1-B]
```

**PM**:兩個 PR 的 CI 都綠 ⭐。先把 **[E1-A] 用 “Create a merge commit”** 合併 ⭐。
此時 [E1-B] 顯示 *This branch has conflicts* ⭐(截圖)。

**B 解衝突**(示範 rerere):
```bash
git fetch origin
git merge origin/main            # CONFLICT (content): activity_log/core.py ⭐ 存下輸出
```
雙方協議最終名稱,例如保留 A 的名字並併入 B 的意圖:
```python
APP_NAME = "Team Activity Tracker"
```
```bash
git add activity_log/core.py
git commit --no-edit             # 輸出會有 "Recorded resolution for 'activity_log/core.py'"
git rerere diff                  # ⭐ 進階工具證據

# rerere 重播:回到合併前,改用 rebase 再做一次,看它自動套用解法
git reset --hard HEAD~1
git rebase origin/main           # ⭐ 會看到 "Resolved 'activity_log/core.py' using previous resolution."
git add activity_log/core.py && git rebase --continue
git push --force-with-lease
```

**PM**:CI 綠後,[E1-B] 用 **“Squash and merge”** ⭐。

⭐ 報告用:衝突標記原文(`<<<<<<< ======= >>>>>>>`)、最終解法、`./scripts/history.sh 10`。

---

## E2 — 同檔不同行 + CI 擋下 PR

**A**(檔案底部加函式,**故意**用 Python 3.11 才有的 `datetime.UTC`):
```bash
git switch main && git pull && git switch -c e2/streak-a
```
在 `activity_log/core.py` 最後面加入:
```python
def longest_streak(entries: Iterable[Entry]) -> int:
    """Longest run of consecutive days with at least one entry."""
    days = sorted({e.day for e in entries})
    best = run = 0
    prev = None
    for d in days:
        run = run + 1 if prev and (d - prev).days == 1 else 1
        best = max(best, run)
        prev = d
    return best


def today_utc() -> date:
    from datetime import UTC, datetime  # 3.11+ only -> breaks the 3.10 matrix leg

    return datetime.now(UTC).date()
```
在 `tests/test_core.py`:檔案**最上方**的 import 改成
```python
from datetime import date, timedelta

import pytest

from activity_log import Entry, banner, by_activity, parse_line, total_minutes
from activity_log.core import longest_streak, today_utc
```
檔案**最下方**加:
```python
def test_longest_streak():
    d = date(2026, 10, 1)
    entries = [Entry(d + timedelta(days=i), "run", 10) for i in (0, 1, 2, 5)]
    assert longest_streak(entries) == 3


def test_today_utc_is_a_date():
    assert isinstance(today_utc(), date)
```
推送前本機先跑 `ruff check . && ruff format --check . && pytest`(lint 失敗會讓 CI 在 test 之前就紅,就看不到 3.10 單獨失敗的效果)。
```bash
git commit -am "feat(e2): longest_streak + today_utc"
git push -u origin e2/streak-a     # 開 PR [E2-A]
```
➡ CI:**test (3.10) 失敗**、3.11/3.12 通過、ci-passed 紅 → Merge 按鈕被擋 ⭐⭐(這是「被擋下的 PR」證據,截圖 Checks 頁與灰掉的 merge 按鈕)。

A 修正(改用 3.10 相容寫法)再推一個 commit:
```python
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).date()
```
```bash
git commit -am "fix(e2): use timezone.utc for Python 3.10"
git push                            # CI 轉綠 ⭐
```

**B**(同時做,改檔案**上方**的 `parse_line`,讓活動名稱統一小寫):
```bash
git switch main && git pull && git switch -c e2/normalize-b
```
`parse_line` 裡把 `return Entry(date.fromisoformat(day_s), activity, minutes)` 改為
```python
    return Entry(date.fromisoformat(day_s), activity.lower(), minutes)
```
測試加在 `test_parse_line_rejects_bad_input` **和 `test_totals` 之間**(不要加在檔尾,否則會跟 A 的新增撞在一起):
```python
def test_parse_line_lowercases_activity():
    assert parse_line("2026-10-26,Run,30").activity == "run"
```
```bash
git commit -am "feat(e2): normalise activity names to lowercase"
git push -u origin e2/normalize-b   # 開 PR [E2-B]
```

**PM**:先把 [E2-B] 用 **“Rebase and merge”** ⭐。
[E2-A] 會顯示 *This branch is out-of-date*(因為勾了 up-to-date)⭐。不同行 → rebase 時 git 自動合併,**無衝突**(已實測)。重點是:即使沒衝突,也必須先更新分支、CI 重跑一次才能合併。
> 想額外示範「低風險衝突」:讓 B 也把測試加在檔尾,rebase 時會在 `tests/test_core.py` 結尾出現兩邊都保留即可的衝突。

**A 更新分支 + range-diff**:
```bash
git fetch origin
git tag e2-before-rebase            # 記住 rebase 前
git rebase origin/main
git range-diff origin/main e2-before-rebase HEAD   # ⭐ 證明 patch 內容沒變、只換了基底
git push --force-with-lease         # CI 重跑 ⭐(記下多等了幾分鐘)
```
**PM**:CI 綠 → [E2-A] **“Rebase and merge”** ⭐。注意 GitHub 會**重寫 SHA**(committer 變 GitHub),對照 PR 頁的 commit SHA 和 main 上的 SHA ⭐。

---

## E3 — 不同檔案 + Fast-forward

**A**:改 `README.md`(加一段「Usage example」)
```bash
git switch main && git pull && git switch -c e3/docs-a
git commit -am "docs(e3): add usage example"; git push -u origin e3/docs-a   # [E3-A]
```
**B**:改 `data/log.csv`(加兩筆資料)
```bash
git switch main && git pull && git switch -c e3/data-b
git commit -am "data(e3): add two entries"; git push -u origin e3/data-b     # [E3-B]
```

**PM**:[E3-A] 用 **“Squash and merge”** ⭐。

**Fast-forward(真正的 FF,SHA 完全保留)**,由 PM 執行:
```bash
# B 先把分支更新到最新 main 之上(不同檔案 → 必定無衝突)
#   B: git fetch origin && git rebase origin/main && git push --force-with-lease
# 等 [E3-B] CI 綠 ⭐

git fetch origin
git switch -c ff-check origin/e3/data-b
git merge-base --is-ancestor origin/main HEAD && echo "可 fast-forward"   # ⭐

# 先示範 hook 擋下(沒有 ALLOW_MAIN_PUSH)
git push origin HEAD:main                     # ⭐ "direct push to main is not allowed"

# 正式 FF 推送(hook 仍會驗證是 FF、沒有 merge commit)
ALLOW_MAIN_PUSH=1 git push origin HEAD:main   # ⭐ 輸出 "abc123..def456  HEAD -> main"(兩個點 = FF)
```
GitHub 會自動把 [E3-B] 標記為 **Merged** ⭐,且 main 上的 SHA 與 PR 分支的 SHA **一模一樣** ⭐(對照 E2 的 rebase & merge 會改 SHA)。

> 補充證據(選做):在本機故意做一個非 FF 狀況(例如 `git commit --amend` 後推送),
> 截 `non-fast-forward push to main blocked` 的畫面 ⭐。

---

## 收尾:蒐集歷史

```bash
./scripts/history.sh 40 > history-full.txt
git log origin/main --graph --oneline --first-parent -n 30 > history-first-parent.txt
```
把 `history-full.txt` 與每個 PR 連結、Actions 連結貼給我,我幫你寫報告(執行摘要、E1–E3、比較表、政策建議)。

---

## 證據清單(打勾用)

- [ ] 第一次 CI 全綠截圖 + Actions 連結
- [ ] 分支保護設定截圖
- [ ] E1:兩個 PR 連結、衝突畫面、衝突標記原文、最終解法、rerere 輸出、graph
- [ ] E2:被擋下的 PR(3.10 紅、merge 按鈕灰)、修正後綠、out-of-date 畫面、range-diff 輸出、SHA 前後對照、graph
- [ ] E3:squash PR、FF 推送輸出、PR 自動 Merged 畫面、hook 擋下畫面、SHA 對照、graph
- [ ] 每個 PR 的 CI 執行時間(Actions 頁的 Duration),用來分析 CI 對合併時機的影響
