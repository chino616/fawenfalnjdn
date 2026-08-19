# Workflow 运行产物

每个数据集使用：

```text
runs/<dataset_id>/
```

标准报告：

```text
00_INPUT_INVENTORY.md
00_IMPLEMENTATION_MANIFEST.md
01_DATASET.md
02_DETECTOR_TARGET.md
03_SOURCE.md
04_THEORY_RESPONSE.md
05_KINEMATICS_CROSS_SECTION.md
06_DETECTOR_RESPONSE.md
07_SLOW_COUNTS.md
08_FAST_COUNTS.md
09_STATISTICS.md
10_VALIDATION_REGISTRY.md
```

阶段顺序是先 `02_DETECTOR_TARGET.md`，后 `03_SOURCE.md`。Target
阶段是文本核对报告，不创建 target 代码、target CSV 或 target 测试。

每份报告只描述一个模块，并包含：

```text
输入来源
用户文档中的具体定义
CsI 局部参考
模块分类
创建/修改/禁止修改的文件
公开 API
测试
结果
Gate
```
