# # yield 基础：写一个 countdown(n)，用 next() 逐个取值，观察 StopIteration
# def countdown():
#     n=5
#     while n>0:
#         yield n
#         n-=1
# g=countdown()
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))
# print(next(g))
# 内存差异：分别用列表推导和生成器表达式处理 100 万个数，用 sys.getsizeof 打印两者大小，记下差多少倍
import sys


l=[i for i in range(1000000)]
print(sys.getsizeof(l))
g=(i for i in range(10000000))
print(sys.getsizeof(g))
# yield from：写一个 chain(*iterables)，用 yield from 把多个可迭代对象串起来
def chain(*iterables):
    for i in iterables:
        yield from i
g=chain('ABC', 'DEF')
print(next(g))
print(next(g))
print(next(g))
print(next(g))


