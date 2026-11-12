# 数据处理
import os

from day2.exceptions import ConfigError

#
def get(key, default=None):
    value = os.getenv(key, default)
    if value is None:
        raise ConfigError(f"环境变量 '{key}' 未设置 ")
    return value
# int() 失败时抛 ConfigError，报错信息里带上原值
def get_int(key, default=None):
    try:
        value = get(key, default)
        value = int(value)
    except ValueError:
        raise ConfigError(f"无法将环境变量 '{key}' 转换为整数，当前为 '{value}'")
    return value
# 接受1 / 0 / true / false / yes / no（不分大小写），其他值报错
def get_bool(key, default=None):
    value = get(key, default)
    if value.lower() in ("1", "true", "yes"):
        return True
    elif value.lower() in ("0", "false", "no"):
        return False
    else:
        raise ConfigError(f"环境变量 '{key}' 不符合")
# load()	一次性校验 DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME，缺哪个一次全报出来
def load():
    # 列出应当有的环境变量
    REQUIRED = ("DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME")
    # 储存缺少的环境变量
    missing = []
    # 遍历应当有的环境变量，检查每个环境变量是否存在
    for k in REQUIRED:
        value=os.getenv(k)
        if not value:
            missing.append(k)
    if missing:
        raise ConfigError(f"缺失环境变量: {', '.join(missing)}")

    return {
        "host": get("DB_HOST"),
        "port": get_int("DB_PORT"),  # 转换在这一层做，出来就是 int
        "user": get("DB_USER"),
        "password": get("DB_PASSWORD"),
        "dbname": get("DB_NAME"),
    }

if __name__ == "__main__":
    print(load())







