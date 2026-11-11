# 然后写 log_analyze.py，必须用生成器逐行读，禁止 readlines()、禁止 f.read()。
import collections
with open("access.log",mode="r",encoding="utf-8") as f:
    data = []
    for line in f:
        data.append(line)
# 请求数 Top 10 IP，用 collections.Counter，降序输出 IP 和次数
def ip_top():
    ip_top=collections.Counter([line.split()[0] for line in data])
    for ip,count in ip_top.most_common(10):
        yield ip,count
# 状态码分布	每个状态码的条数和占比（保留两位小数）
def http_num():
    http_num=collections.Counter([line.split()[-2] for line in data])
    for http,num in http_num.most_common():
        yield http,num,num/sum(http_num.values())
# 5xx 比例	单独算，超过 1% 打印一行警告
def rate_5xx():
    http_5xx=collections.Counter([line.split()[-2] for line in data if line.split()[-2][0]=="5"])
    num=sum([num for num in http_5xx.values()])
    if num/100000 > 0.01:
        print("5xx超过1%")
        yield num/100000
# QPS峰值 按分钟聚合，找出请求数最多的那一分钟及其数值
def qps_min():
    times=[line.split()[3] for line in data]
    min_time=collections.Counter([min_time.strip("[]").rsplit(":",1)[0] for min_time in times])
    for min_time,num in min_time.most_common(1):
        yield min_time,num
if __name__=="__main__":
    ip_top=ip_top()
    for ip,count in ip_top:
        print(ip,count)
    http_num=http_num()
    for http,num,rate in http_num:
        print(f"{http} {num} {rate*100:.2f}%")
    rate_5xx=rate_5xx()
    for rate in rate_5xx:
        print(f"5xx为{rate*100:.2f}%")
    qps_min=qps_min()
    for min_time,num in qps_min:
        print(min_time,num)
