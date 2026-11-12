# 然后写 log_analyze.py，必须用生成器逐行读，禁止 readlines()、禁止 f.read()。
# 请求数 Top 10 IP	用 collections.Counter，降序输出 IP 和次数
# 状态码分布	每个状态码的条数和占比（保留两位小数）
# 5xx 比例	单独算，超过 1% 打印一行警告
# QPS 峰值	按分钟聚合，找出请求数最多的那一分钟及其数值
import collections
import hashlib
import os
import sys

from day2.db import save_result

# 默认日志与本文件同目录，这样从任何工作目录启动都能找到
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PATH = os.path.join(BASE_DIR, "access.log")

path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
if not os.path.exists(path):
    sys.exit(f"路径不存在: {path}")


def read_data(path):
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 9:
                continue
            yield parts


def collect(lines):
    ip_top = collections.Counter()
    http_top = collections.Counter()
    qps_top = collections.Counter()
    http_5xx = 0
    for line in lines:
        # 统计ip
        ip_top[line[0]] += 1
        # 统计状态码
        http_top[line[-2]] += 1
        # 统计5xx状态码个数
        if line[-2][0] == "5":
            http_5xx += 1
        # 统计每分钟的请求数
        qps_top[line[3].strip("[]").rsplit(":", 1)[0]] += 1
    return ip_top, http_top, qps_top, http_5xx


# 分块算 md5：日志可能很大，不能整个读进内存
def file_md5(path):
    h = hashlib.md5()
    with open(path, mode="rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # 汇总数据
    ip_top, http_top, qps_top, http_5xx = collect(read_data(path))
    ip_dict = ip_top.most_common(10)
    http_dict = http_top.most_common()
    qps_dict = qps_top.most_common(1)
    total = http_top.total()
    # 格式化输出
    for ip, num1 in ip_dict:
        print(f"IP为{ip},次数{num1}")
    for http, num2 in http_dict:
        print(f"状态码{http},条数{num2},占比{num2/total:.2%}")
    if http_5xx / total > 0.01:
        print("5xx比例超过1%，请关注")
    print(f"5xx比例为{http_5xx/total:.2%}")
    for qps, num3 in qps_dict:
        print(f"QPS峰值为{qps},请求数{num3}")

    # 落库：只存报告里出现的口径（Top10 IP、全部状态码、QPS 峰值），不把 1334 个分钟全塞进去
    stats = {
        "ip": dict(ip_dict),
        "status": dict(http_dict),
        "qps": dict(qps_dict),
    }
    file_id = save_result(file_md5(path), os.path.basename(path), total, http_5xx, stats)
    print(f"已写入数据库 file_id={file_id}")


if __name__ == "__main__":
    main()
