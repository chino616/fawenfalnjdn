# release：构建和隔离安装的输出位置

本目录由 [build_wheel.py](../../tools/build_wheel.py) 和 [verify_wheel.py](../../tools/verify_wheel.py) 固定写入。它与源码/data 分开，用于检查打包后实际导入的是安装包，而非被项目根目录掩盖的源码。

## 文件由谁产生

| 产物 | 生成步骤 |
|---|---|
| `*.whl`、`build.log` | `build_wheel.py` 执行离线 `pip wheel --no-build-isolation --no-deps --no-index` |
| `final-validation/`、`install.log` | 同一脚本把 wheel 装入项目内独立 target，避免安装到用户全局环境 |
| [wheel.json](wheel.json) | 记录 wheel 路径、SHA256 和安装 target；下一验证步骤直接读取它 |
| `outside_cwd.json`、`outside_cwd.log` | `verify_wheel.py` 从外部 cwd、用 `python -I` 验证三实验预测并保存结果 |
| `build-temp/` | 构建时的 TEMP/TMP；可能只在实际构建后出现 |

当前目录保留的是历史日志与描述，所记录绝对路径可能属于旧 checkout，不能据此认为 wheel 或安装目录在当前副本中存在。

## 管理与重新生成

从项目根目录依次执行 `python tools/build_wheel.py`、`python tools/verify_wheel.py`。后者当前会创建项目旁 `CONUS-Backup/_migration/wheel_outside_cwd` 作为工作目录，并使用显式当前资源根；这个路径名不表示激活 CONUS。

重新执行会更新固定日志和 JSON，保留旧验收时应先保存独立运行记录。不要手改 `wheel.json` 的哈希或把缺失安装目录伪装成已验证。新增发行产物应由对应工具生成并说明消费者；新的构建策略在 `tools/` 实现，不在输出目录复制一份构建逻辑。

---

[上一级](../README.md) · [项目总览](../../README.md)
