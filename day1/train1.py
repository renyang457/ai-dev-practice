"""Day 1 练习：五个常用装饰器

验收标准
- 五个装饰器全部带 functools.wraps（被装饰函数的 __name__ 保持不变）
- retry 最后一次失败用裸 raise，保留原异常类型和 traceback
- cache 参数不可哈希时跳过缓存，且函数只执行一次
- log 在调用前记录时间戳，函数抛异常时也有输出
- require 拒绝时给出可读信息（谁、要什么权限、当前是什么）

原始版本备份在 archive/train1_原始_20261111.py
"""
import functools
import time
from datetime import datetime


# ------------------------------------------------------------------ timer
def timer(func):
    """打印函数名和执行耗时（保留 4 位小数）。"""

    @functools.wraps(func)
    def inner(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            # 放在 finally 里：函数抛异常时也能打印耗时，
            # 否则出错的调用在日志里完全没有耗时记录
            cost = time.perf_counter() - start
            print(f"[timer] {func.__name__} 耗时 {cost:.4f}s")

    return inner


# ------------------------------------------------------------------ retry
def retry(times, delay):
    """抛异常时重试：总共尝试 times 次，每次间隔 delay 秒。

    最后一次失败必须把原异常抛出去，不能吞掉。
    """

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == times - 1:
                        raise  # 裸 raise：保留原类型与 traceback，不多一层
                    print(f"[retry] {func.__name__} 第 {i + 1} 次失败：{e}，{delay}s 后重试")
                    time.sleep(delay)

        return inner

    return decorator


# ------------------------------------------------------------------ cache
def cache(func):
    """用 dict 存“参数 → 结果”；参数不可哈希时跳过缓存。"""

    store = {}  # 定义时创建，每个被装饰函数各自独立

    @functools.wraps(func)
    def inner(*args, **kwargs):
        # kwargs 必须进 key，否则 f(x=1,y=2) 和 f(y=2,x=1) 会共用一个 key
        key = (args, frozenset(kwargs.items()))
        try:
            hash(key)  # 只把这一行放进 try
        except TypeError:
            return func(*args, **kwargs)  # 不可哈希：直接执行，不缓存
        if key in store:
            return store[key]
        result = func(*args, **kwargs)
        store[key] = result
        return result

    return inner


# -------------------------------------------------------------------- log
def log(func):
    """打印调用时间、函数名、实参、返回值；抛异常时也打印。"""

    @functools.wraps(func)
    def inner(*args, **kwargs):
        called_at = datetime.now()  # 进函数就取时间，晚了就不是“调用时间”了
        print(f"[log] {called_at:%Y-%m-%d %H:%M:%S} -> {func.__name__} "
              f"args={args} kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f"[log] {called_at:%H:%M:%S} <- {func.__name__} "
                  f"抛 {type(e).__name__}: {e}")
            raise
        print(f"[log] {called_at:%H:%M:%S} <- {func.__name__} = {result!r}")
        return result

    return inner


# ----------------------------------------------------------------- require
CURRENT_USER = {"name": "张三", "role": "user"}


def require(role):
    """带参权限校验：当前用户角色不是 role 时抛 PermissionError。"""

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            current = CURRENT_USER.get("role")
            if current != role:
                raise PermissionError(
                    f"{func.__name__} 需要 {role} 权限，当前角色是 {current}"
                )
            return func(*args, **kwargs)

        return inner

    return decorator


# ------------------------------------------------------------------- 演示
if __name__ == "__main__":
    print("========== timer ==========")

    @timer
    def sum_squares(n):
        return sum(i * i for i in range(n))

    print("结果:", sum_squares(200_000))

    print("\n========== retry ==========")
    attempts = {"n": 0}

    @retry(times=3, delay=0.2)
    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ValueError(f"第 {attempts['n']} 次失败")
        return 42

    print("结果:", flaky(), "| 实际调用次数:", attempts["n"])

    # 失败路径：必须真的抛出 RuntimeError
    @retry(times=2, delay=0.05)
    def always_fail():
        raise RuntimeError("炸了")

    try:
        always_fail()
    except RuntimeError as e:
        print("失败路径正确抛出:", e)

    print("\n========== cache ==========")
    calls = {"n": 0}

    @cache
    def double(x):
        calls["n"] += 1
        return x * 2

    double(7)
    double(7)
    print("同参数调用两次，函数体执行次数:", calls["n"])

    @cache
    def sub(x, y):
        return x - y

    print("sub(x=10,y=1) =", sub(x=10, y=1), "| sub(x=1,y=10) =", sub(x=1, y=10))
    print("传 list 不报错:", cache(lambda v: len(v))([1, 2, 3]))
    print("__name__ 保留:", double.__name__)

    print("\n========== log ==========")

    @log
    def add(a, b=0):
        return a + b

    add(1, b=2)
    try:
        add(1, b="x")
    except TypeError as e:
        print("(异常已向上抛出:", e, ")")

    print("\n========== require ==========")

    @require(role="user")
    def read_data(x):
        return f"数据内容 {x}"

    print("角色匹配:", read_data(1))
    CURRENT_USER["role"] = "admin"
    try:
        read_data(2)
    except PermissionError as e:
        print("角色不匹配:", e)
    finally:
        CURRENT_USER["role"] = "user"
