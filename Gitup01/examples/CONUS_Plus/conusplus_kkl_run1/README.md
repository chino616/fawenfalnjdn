# CONUS+最新SM / NSI运行入口

sm_response/保存原SM物理装配和前向/数值核对；nsi_response/共享该装配，单独进行矢量NSI系数核、拟合和图表。conusplus_paths.py只定位本地文件并核对输入；LOCAL_INPUTS.json为当前采用输入指纹，原始执行源码在一份压缩证据中保留。

从Gitup01根目录运行，Python需numpy、scipy、matplotlib、jsonschema；只有重新提取PDF时才需要pdfplumber。每次输出目录必须全新：

```powershell
python -B examples/CONUS_Plus/conusplus_kkl_run1/run_benchmark.py --method sm --output-dir outputs/CONUS_Plus/conusplus_kkl_run1/SM_REPEAT_NEW
python -B examples/CONUS_Plus/conusplus_kkl_run1/run_benchmark.py --method nsi --output-dir outputs/CONUS_Plus/conusplus_kkl_run1/NSI_REPEAT_NEW
```

--stage predictions/validate/report可限制工作；NSI的validate会为当前代码身份重新编译缓存，再核对已复制的Slow参考。上述命令调用当前项目引擎，不需要原.experiment-auto-runs目录。迁入的旧缓存是历史执行证据。

[最新分析入口](../../../docs/experiments/LATEST_EXPERIMENTS.md) · [处理方式](../../../docs/experiments/CONUS_Plus/datasets/conusplus_kkl_run1/METHODS.md)
