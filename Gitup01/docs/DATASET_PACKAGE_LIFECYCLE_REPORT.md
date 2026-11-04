# Task 09 — Dataset Package Lifecycle and Distribution

2026-11-04；branch `refactor/07-gitup01-20261104`；HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。保留既有/并行修改；无commit/push/分支变化。
已读Task09、规则/顺序、两级.gitignore、实际registry/catalog/ResourceCatalog/management/export/
registry_io、package-data、build/verify工具和生命周期测试。

## 变更和正式所有权

唯一dataset_registry继续拥有生命周期；CsI2021三文件逐项记录sha256、runtime_required、
归属路径及package_version=2.0.0。YAML/NPZ为physical resources，Physics MD为随包documentation。
现有export_package自动包含三文件及manifest哈希；管理audit新增可选owned-file哈希检查。
没有新建第二套安装/导出系统。原有并行candidate文件ownership保留，文件内容未编辑，
且不成为canonical Loader依赖；保护记录只固定其当前完整性，不宣称其科学或运行绑定通过。

.gitignore在项目根添加精确父目录/三文件例外；git check-ignore -v --no-index显示三份文件
命中!例外，而同目录private-data.bin仍命中父级data/**规则。未解除整个data目录忽略。
NPZ仅约15KB，无仓库LFS策略，未引入LFS。

新增 [package_build.py](../tools/package_build.py) setuptools build_py hook和
[MANIFEST.in](../MANIFEST.in)。构建时从唯一data权威复制已登记active正式三文件到wheel的
cevns_pyeft/_data/data/experiments路径；sdist直接携带原data文件和构建hook，不在源码维护第二份数值。
foundation.paths.resource_root在源码/editable使用原data根，在wheel使用bundled根；无绝对路径fallback。

## 实际分发验证

`outputs/onboarding/task09/distribution01/`保留wheel、sdist、build/install/editable/outside日志和results.json。
离线pip wheel、setuptools.build_meta.build_sdist、pip --target安装实际成功。

- wheel包含全部三文件，sdist包含全部三文件，逐项清点通过。
- normal install后从外部cwd使用python -I加载默认CsI2021，无外部data；small总379.8315235321747。
- editable --target隔离安装后，以site.addsitedir从外部cwd运行得到相同值。
- bundled Physics MD存在可读，计算资源只有package_input/package_arrays。
- 资源清单validate_resource_manifest --dataset CsI2021 PASS；management.audit PASS。
- 缺失/损坏包拒绝由Task04/06篡改测试和本任务export完整性测试保护，不读MD补数据。

[test_dataset_package_distribution.py](../tests/test_dataset_package_distribution.py)验证三文件own/hash/
runtime角色、export以及窄ignore。生命周期全组首次为26 passed/1 failed，失败真实定位到
卸载CsI2021后其他实验Fast模块导入kernels.builder，后者在模块级读取CsI2021默认值。
将这两个历史名称改为按需读取，算法不变；该问题不能靠把已卸载输入藏在通用默认值中解决。
后续重跑结果在此追加。测试只在隔离副本卸载/安装/回滚，不操作生产dataset。

保护清单只更新本轮授权变更/新增模块及正式输入；没有重算冻结reference或其他实验数值。
候选文件只登记完整性，未编辑或作为新运行依赖。外部已有lazy-init/README差异单独审计。
所有修改有backup/task09-lifecycle-20261104起始字节副本，之前任务恢复点不覆盖。

没有改变物理公式、数组、容差或科学状态。下一步按实际active registry逐个迁移其余dataset；
Task10不能把archive/CONUS/ROOTTime/demo自动列入范围。

最终：24项非耗时事务/分发测试通过；CsI2021真实卸载/重装/逆向回滚修复后单独通过，
CsI2017/Ar2020真实事务在首次全组已通过。全局Skill-pack保护/结构检查PASS；7文档141链接PASS。
并行lazy detector/statistics init已检查为导入延迟，无物理常数修改，记录其保护哈希；候选三文件
内容仍未编辑。Task08暂缺的run报告目标现已由原写入方生成，链接复核通过。

[进度](ONBOARDING_TASKS_02_10_PROGRESS.md)
