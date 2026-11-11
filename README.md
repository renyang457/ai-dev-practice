# 实习准备 · 每日代码

2027 届求职准备期的手写练习。每天一个主题，按天归档，全部代码自己敲，不用 AI 生成。

目标岗位：AI 应用开发 / 智能体开发（Python 主线）。

## 目录

| 日期 | 主题 | 产出 |
|---|---|---|
| 11/11（D1） | 闭包与装饰器 · 生成器与流式处理 · Docker 容器化 | `train1.py`<br>`docker-demo/log_analyze.py`<br>`docker-demo/Dockerfile` |

## 每日内容

### D1（11/11）

**装饰器** `train1.py` —— 五个装饰器，覆盖无参和带参三层闭包两种形态：

- `timer`：`perf_counter` + `try/finally`，异常路径也记录耗时
- `retry`：耗尽后裸 `raise`，traceback 指向真实出错行，不多包一层帧
- `cache`：键由「位置参数 + 排序后的关键字参数」构成，不可哈希时降级直跑
- `log`：入口出口双行，`!r` 格式化，异常分支打印后裸 `raise`
- `require`：参数化装饰器，比对 `CURRENT_USER["role"]`

17 项边界用例全部通过（异常路径、重试耗尽、缓存命中、不可哈希入参、元信息保留）。

**流式日志分析** `docker-demo/log_analyze.py` —— 10 万行 nginx 日志四维度统计：

```
read_data(path)  生成器逐行 split
      ↓
collect(rows)    单次遍历喂 3 个 Counter 和 5xx 计数
      ↓
main()           只负责格式化
```

四个指标必须一轮算完，因为生成器只能遍历一次。这也是函数边界从「谁读文件」改成「谁排版」的原因。

| 版本 | 数据量 | 峰值内存 | 常驻 |
|---|---|---|---|
| 全量读入列表 | 10 万行 | 25.91 MB | 26 MB |
| 流式 | 10 万行 | 6.99 MB | 567 KB |
| 流式 | 40 万行 | 0.55 MB | 7.1 MB |

**容器化** `docker-demo/` —— 代码进镜像、日志靠 `-v` 挂载，镜像 177MB。

## 环境

Windows 11 + WSL2、Python 3.12、Docker Desktop 29.2.1。

## 说明

`*.log` 不入库（8MB 测试数据，可用 `train3.py` 重新生成）。
