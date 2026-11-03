# 仓库结构与 README 维护

<!-- workflow-metadata: orchestration, not Skill frontmatter -->
```json
{
  "workflow_id": "cevns.repository_maintenance",
  "skills": [],
  "handoffs": ["cevns.runtime_maintenance"]
}
```

由[唯一任务路由表](../../router/routes.yaml)选择本流程，适用于文件架构维护、批量删减/移动后的 README 和导航同步，以及 Git 变更的文档影响核对。它复用[文件生命周期规则](../../../_shared/policies/file-lifecycle.md)，不创建新实验或新的物理批准。

## 使用者可直接选择的维护入口

| 说法或模式 | 实际工作与停止点 |
|---|---|
| 检查维护 / 生成维护清单 | 只读提取 Git 差异或快照差异，汇总受影响目录、README、旧路径引用和失效链接 |
| 同步 README / 大幅删减后整理说明 | 在已授权文件范围内修正人工用途说明和导航，再对明确选择的 README 同步自动目录区 |
| 维护验收 | 检查自动目录区、当前链接、残留引用及必要的程序/资源验证，报告仍需人工核对的内容 |

用户已经明确要求同步或验收时直接执行相应工作，不重复询问模式；意图仅为检查时保持只读。实际删除文件需要明确的文件范围；本流程不会因为发现“可能多余”就自动删除源码、数据、README 或历史材料。

## 1. 固定比较基线，保留当前工作

先确认项目根、Git 根、当前提交与脏工作区范围。Git 可用时以明确提交为基线；默认 `HEAD`，分支提交后的累计维护可显式指定更早的提交。计划工具把该提交到当前 index/worktree 的差异与未跟踪文件合并，并记录解析后的 commit SHA。

大幅删减前保存当前清单，未跟踪和未提交内容按本次范围备份；已有提交无法单独恢复未跟踪文件。只使用本次明确的删减范围，保留无关工作。Git 分支、提交、恢复与推送按用户已有授权处理；本工具不执行 Git 写入，也不自动 reset/clean。

没有 `.git` 时明确说明无法读取提交历史，保存文件快照作为之后比较的基线。不要自动初始化 Git，也不要把“基线建立后没有变化”写成“此前大幅删除已核实”。

## 2. 一次生成影响清单，按目录分组处理

从项目根执行，报告写本次获准的 outputs 或用户指定目录：

```powershell
python -B tools/readme_maintenance.py plan --base HEAD --out outputs/readme-plan.json
```

如果要比较指定提交，把 `HEAD` 换成实际 revision。Git 模式同时覆盖 staged、unstaged 与未跟踪文件；移动识别以 Git 的 rename detection 为依据。

无 Git 时，在删减前后分别执行：

```powershell
python -B tools/readme_maintenance.py snapshot --out outputs/readme-before.json
python -B tools/readme_maintenance.py plan --snapshot-base outputs/readme-before.json --out outputs/readme-plan.json
```

`snapshot` 记录当前活动文件的路径、大小和 SHA256；只在旧/新文件各有唯一相同哈希时标记移动，其他情况保留新增/删除，避免猜测。报告默认不覆盖已有文件；需要复用报告路径时显式指定 `--overwrite-report`。

计划将每个变更映射到原/当前最近的 README，并合并上级导航；删除或移动时只对活动 Markdown 执行一次旧路径反向引用扫描。原目录整体消失时更新仍存在的父级入口，不能机械重建刚删掉的目录。JSON 保存逐文件记录，面向用户按目录概括，避免重复处理同一 README。

计划状态为 REVIEW_REQUIRED 只代表找出了维护对象，不代表说明已同步。没有找到所属 README 的新增文件、被删除 README 的替代入口、旧路径残留和失效链接都必须在本次范围内说明处理结果。

## 3. 人工说明与自动目录区分别同步

先根据真实用途更新人工段落：删除旧条目、改名/移动的入口与命令、替代文件、当前消费者和能力边界。反向扫描命中的历史说明可能需要保留，逐项分类，不对整份 README 做盲目文本替换。

目录的当前文件清单可接入以下自动维护区：

```text
<!-- readme-inventory:start -->
仅此区域由工具按当前直接子项重新生成
<!-- readme-inventory:end -->
```

只对本次明确选择的 README 执行：

```powershell
python -B tools/readme_maintenance.py sync --readmes tools/README.md configs/README.md
```

第一次执行会追加自动区；之后只替换这一对标记之间的内容，自动增删目录清单行，保留标记外的人工说明。目录项优先链接子目录 README。工具先验证全部目标和标记，再保存改动前的 README 到 `backup/readme-sync-<唯一ID>/`，并追加备份清单。它不创建缺失 README、不删除文件、不移动目录，也不改写历史报告或冻结证据。

多个标记区或标记不配对时拒绝同步；不能通过覆盖整份 README 来绕过。若该 README 属于保护清单，只登记本次获准修改的真实哈希与准确路径，保留其他保护项。

## 4. 验收并结合 Git 复查

```powershell
python -B tools/readme_maintenance.py check --readmes tools/README.md configs/README.md
python -B tools/validate_docs.py --files README.md tools/README.md configs/README.md
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py
```

列表替换为本次实际目标。`check` 检查所选 README 的自动区是否等于当前目录、Markdown 链接是否有效；未接入自动区会显示 NOT_MANAGED，不能冒充清单已同步。纯人工 README 可使用链接检查和变更清单核对，无需为所有目录强加生成区。

再用同一 Git 基线重新生成维护计划，核对旧路径命中是否已正确处理。按本次语义变化运行相关 import/接口测试、资源审计或工作流检查；数据集退出活动清单、统计定义改变等交给对应 archive/resource/runtime/physics 路由，不用删文档来掩盖功能变化。

最后查看 `git diff --stat` 与具体 README diff，把文件删除/移动、配套文档和必要消费者更新作为同一可审查单元。提交仅在用户授权时执行；不要将无关修改顺带加入提交。大批量改动可先按独立目录分组复核，最后统一运行相关检查。

## 完成条件与产物

- 变更清单对应到当前目录说明，人工用途描述与实际文件一致；新增项有明确归属。
- 当前入口没有本次引入的失效链接；删除/移动后的残留引用已修复或有保留历史的说明。
- 所采用的自动目录区与文件系统一致，相关消费者、注册、资源和保护记录同步。
- 记录比较提交/快照、实际修改的 README、检查命令与结果、未完成事项及回滚位置。

保存维护计划 JSON、最终检查结果和必要的 Git diff 摘要到本次输出位置。静态检查不能证明人工段落语义完整，也不能保证今后任意外部手工删文件后立即同步；每次结构变更都应运行本流程。没有文件监听器，工具不会自动提交 Git 或授予科学批准。
