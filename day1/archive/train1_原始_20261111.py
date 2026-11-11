# # 装饰器的三层结构
# def time1(num): # num为装饰器参数
#     def decorator(func): # func为被装饰的函数
#         def inner(*args, **kwargs): # inner内接收被装饰函数的参数
#             print("这是装饰器功能")
#             return func(*args, **kwargs) # 返回装饰后函数的执行结果
#         return inner # 返回内层函数
#     return decorator  # 返回装饰器
# @time1(3) #3为装饰器参数
# def func(x):
#     return "func"
# func(1)
# @timer	打印函数名和执行耗时（保留 4 位小数）
import functools
import time
def timer(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        start = time.time()
        res=func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}耗时{end - start:.4f}")
        return res
    return inner

@timer
def print_func():

    return print_func.__name__
print(print_func())
# @retry(times, delay)	抛异常时重试 times 次，每次间隔 delay 秒；最后一次失败必须把异常抛出去，不能吞掉
import time
def retry(times,delay):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            for i in range(times):
                try:
                    res=func(*args, **kwargs)
                except Exception as e:
                    if i == times - 1:
                        raise e
                    time.sleep(delay)
                else:
                    return res
        return inner
    return decorator
@retry(3,2)
def func():
    print("func")
func()
# @cache	用 dict 存"参数 → 结果"，同参数第二次直接返回不执行；参数不可哈希时跳过缓存、不报错
def cache(func):
    cache_dict={}
    def inner(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        try:
            hash(key)
        except TypeError:
            return func(*args, **kwargs)
        if key in cache_dict :
            return cache_dict[key]
        res = func(*args, **kwargs)
        cache_dict[key] = res
        return res
    return inner
list1=[1,2,3,4,5]
@cache
def func(x):
    return x*2
print(func(list1))
# @log	打印调用时间、函数名、实参、返回值
import functools
from datetime import datetime


def log(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        time1=datetime.now()
        res=func(*args, **kwargs)
        print(f"调用时间{time1:%Y-%m-%d %H:%M:%S},函数名{func.__name__},实参{args},{kwargs},返回值{res}")
        return res
    return inner
@log
def func():
    print("func")
func()
# @require(role)	带参权限校验，全局 CURRENT_USER = {"name":"张三","role":"user"}，不匹配抛 PermissionError
import functools

CURRENT_USER = {"name":"张三","role":"user"}
def require(role):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if role == CURRENT_USER["role"]:
                return func(*args, **kwargs)
            raise PermissionError
        return inner
    return decorator
@require(role="user")
def func():
    print(CURRENT_USER)
func()


