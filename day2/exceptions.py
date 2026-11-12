import time
from contextlib import contextmanager


class AppError(Exception):
    code = "APP_ERROR"

    def __init__(self, message, detail=None):
        self.message = message
        self.detail = detail or {}
        super().__init__(message)
# 必填配置缺失、类型转换失败
class ConfigError(AppError):
    code = "CONFIG_ERROR"
class DataError(AppError):
    code = "DATA_ERROR"
class DbError(AppError):
    code = "DB_ERROR"
class DbConnError(DbError):
    code = "DB_CONN_ERROR"
# # 类版 Timer	进入记开始时间，退出打印耗时；with 块内抛异常时，异常仍要往外传，但耗时要打出来
# # 生成器版 @contextmanager	同样功能，用 yield 把 try/finally 夹起来；yield 前是进入、后是退出
# class Timer:
#     def __enter__(self):
#         self.start=time.time()
#         return self
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         print(f"time:{time.time()-self.start}")
#         if exc_type is not None:
#             print(f"出现异常：{exc_type},异常信息：{exc_val}")
#         return False
# with Timer() as t: time.sleep(5)
# # 生成器版 @contextmanager	同样功能，用 yield 把 try/finally 夹起来；yield 前是进入、后是退出
# @contextmanager
# def timer():
#     start=time.time()
#     try:
#         yield start
#     finally:
#         print(f"time:{time.time()-start}")


