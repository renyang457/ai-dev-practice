# 实习准备 · 每日代码

2027 届求职准备期的手写练习。每天一个主题，按天归档，全部代码自己敲，不用 AI 生成。

目标岗位：AI 应用开发 / 智能体开发（Python 主线）。

## 目录

| 日期 | 主题 | 产出 |
|---|---|---|
| 11/11（D1） | 闭包与装饰器 · 生成器与流式处理 · Docker 容器化 | `day1/archive/train1.py`<br>`day1/log_analysis/log_analyze.py`<br>`day1/log_analysis/Dockerfile` |
| 11/12（D2） | 异常体系 · 上下文管理器 · 配置加载 · MySQL 落库 | `day2/exceptions.py`<br>`day2/config.py`<br>`day2/db.py`<br>`day2/schema.sql` |

## 每日内容

### D1（11/11）

**装饰器** `day1/archive/train1.py` —— 五个装饰器，覆盖无参和带参三层闭包两种形态：

- `timer`：`perf_counter` + `try/finally`，异常路径也记录耗时
- `retry`：耗尽后裸 `raise`，traceback 指向真实出错行，不多包一层帧
- `cache`：键由「位置参数 + 排序后的关键字参数」构成，不可哈希时降级直跑
- `log`：入口出口双行，`!r` 格式化，异常分支打印后裸 `raise`
- `require`：参数化装饰器，比对 `CURRENT_USER["role"]`

17 项边界用例全部通过（异常路径、重试耗尽、缓存命中、不可哈希入参、元信息保留）。

**流式日志分析** `day1/log_analysis/log_analyze.py` —— 10 万行 nginx 日志四维度统计：

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

**容器化** `day1/log_analysis/` —— 代码进镜像、日志靠 `-v` 挂载，镜像 177MB。

```powershell
docker build -t log-analyze:1.2 .
docker run --rm -v "${PWD}/access.log:/data/access.log" log-analyze:1.2 /data/access.log
```

### D2（11/12）

**异常体系** `day2/exceptions.py` —— 四层继承树，`except AppError` 能接住第三层：

```
Exception → AppError(code/message/detail) → ConfigError  CONFIG_ERROR
                                         → DataError    DATA_ERROR
                                         → DbError      DB_ERROR → DbConnError  DB_CONN_ERROR
```

`code` 挂在类上（种类固定），`message` 由调用方传（每次不同），子类不重写 `__init__`。
`raise ... from e` 保留原因链，traceback 里能看到 `The above exception was the direct cause of ...`。

**上下文管理器** 两版 `Timer`——类版 `__enter__`/`__exit__`，生成器版 `@contextmanager` + `try/finally`。
实测：`__exit__` 返回 `True` 会把异常静默吞掉，调用方以为成功；返回 `False` 才正常抛出。

**配置加载** `day2/config.py` —— `get` / `get_int` / `get_bool` / `load`。
环境变量全是字符串，类型转换在 `load()` 入口一次做完；缺键时先收集再抛，**一次列全**而不是只报第一个。

**MySQL 落库** `day2/schema.sql` + `day2/db.py`

| 表 | 作用 |
|---|---|
| `log_file` | 一次分析一行，`file_md5 char(32)` 唯一键 |
| `log_stat` | 维度行，外键指向 `log_file.id`，`ON DELETE CASCADE` |

`save_result(md5, file_name, total, count_5xx, stats)` 先查后插实现幂等；插入两表在一个事务里，失败 `rollback`。
实测：同一份日志跑两次，`log_file` 1 行、`log_stat` 16 行不变；注入非法 `stat_value` 后两张表都不留脏行。

启动数据库容器（密码自己定，不要提交到仓库）：

```powershell
docker run -d --name mysql-d2 `
  -e MYSQL_ROOT_PASSWORD=<你的密码> `
  -e MYSQL_DATABASE=logdb `
  -p 3307:3306 mysql:8.0.45
docker exec -i mysql-d2 mysql -uroot -p<你的密码> logdb < day2/schema.sql
```

宿主机 3306 已被本机 MySQL80 服务占用，所以映射到 **3307**，`DB_PORT` 也要填 3307。

运行日志分析并落库（环境变量必须与容器一致）：

```powershell
$env:DB_HOST="127.0.0.1"; $env:DB_PORT="3307"; $env:DB_USER="root"
$env:DB_PASSWORD="<你的密码>"; $env:DB_NAME="logdb"
.venv\Scripts\python.exe -m day1.log_analysis.log_analyze
```

## 环境

Windows 11 + WSL2、Python 3.12、Docker Desktop 29.2.1、MySQL 8.0.45（容器）。

## 说明

- `*.log` 不入库（8MB 测试数据，需要时重新生成即可）。
- 数据库密码只通过环境变量注入，不写进任何被跟踪的文件。
- 目录名用下划线不用连字符：`log_analysis` 才能 `python -m day1.log_analysis.log_analyze` 导入。
