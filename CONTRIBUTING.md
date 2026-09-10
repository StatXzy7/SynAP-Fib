# 日常维护

以后在 SynAP-Fib 新目录修改论文和代码。原 `SFibAI-B/` 与 `paper-plan/` 保留作来源，避免同时在两个位置维护同一稿件。仍在原目录运行的实验继续使用其既有快照。

每次修改前，工作树干净时运行 `git pull --ff-only`。中文写作改 `paper/zh/`，英文稿改 `paper/en/`，共享文献和图片只维护 `paper/en/`；当前代码改 `code/`。

修改完成后，从仓库根目录执行：

```powershell
python tools/verify_repository.py
powershell -ExecutionPolicy Bypass -File tools/build_paper.ps1
git status --short
git diff
git add -- paper/ code/ docs/ README.md CONTRIBUTING.md AGENTS.md tools/ .gitignore .gitattributes .github/
git diff --cached --stat
git diff --cached --check
git commit -m "docs: revise manuscript methods"
git push
```

按实际修改调整提交路径和说明；只改代码时不必编译论文，但应运行与代码改动相关的测试。新增数据或模型产物不应加入提交。冻结代码目录保持不变。

较大改动可用 `git switch -c paper/methods-revision` 建分支，完成后推送并通过 PR 审查。投稿时用明确的 tag 固定论文和代码同一版本；当前仅建立导入基线，未标记为投稿或实验完成版本。

GitHub Actions 在 push/PR 时做 UTF-8、Python 语法、论文引用路径和冻结快照完整性检查。这不运行训练，也不替代实验审查或论文事实审查。

GitHub 不会自动同步本地改动；每次 commit 后需要 push。本次没有设置自动提交、后台上传或定时任务。
