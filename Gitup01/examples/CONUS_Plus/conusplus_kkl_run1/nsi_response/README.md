# examples/CONUS_Plus/conusplus_kkl_run1/nsi_response

本目录属于当前最新实验整理；文件按方法、输入、代码、结果或来源记录归属，具体限制见总入口。

- [benchmark_nsi.py](<benchmark_nsi.py>)
- [extract_nsi_references.py](<extract_nsi_references.py>)
- [nsi_model.py](<nsi_model.py>)
- [prepare_predictions.py](<prepare_predictions.py>)
- [publish_nsi.py](<publish_nsi.py>)
- [sm_model.py](<sm_model.py>)

[最新实验入口](<../../../../docs/experiments/LATEST_EXPERIMENTS.md>)

[run_nsi_benchmark.ps1](run_nsi_benchmark.ps1)是保留旧报告入口名称的本地包装器，调用父目录run_benchmark.py；显式接收-OutputDir、-Python和-Stage，不包含机器专用解释器或外部依赖路径。
