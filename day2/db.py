import hashlib

import pymysql

from day2.config import load
from day2.exceptions import DbConnError, DbError


# 建立数据库连接
def connect():
    cfg = load()
    try:
        conn = pymysql.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["dbname"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.err.OperationalError as e:
        raise DbConnError(f"连不上 {cfg['host']}:{cfg['port']}") from e
    return conn


# 保存一次分析结果：一个事务里写 log_file + log_stat；md5 相同视为同一份日志，直接返回旧 id
def save_result(md5, file_name, total, count_5xx, stats):
    conn = connect()
    try:
        with conn.cursor() as cur:
            # 0. 幂等：这份日志进来过就不要再插
            cur.execute("select id from log_file where file_md5 = %s", (md5,))
            row = cur.fetchone()
            if row:
                return row["id"]

            # 1. 写 log_file，拿自增 id
            cur.execute(
                "insert into log_file (file_name, total, count_5xx, file_md5) "
                "values (%s, %s, %s, %s)",
                (file_name, total, count_5xx, md5),
            )
            file_id = cur.lastrowid

            # 2. 批量写 log_stat：外层是类型，内层是 键 -> 次数
            rows = [
                (file_id, stat_type, key, value)
                for stat_type, counter in stats.items()
                for key, value in counter.items()
            ]
            if rows:
                cur.executemany(
                    "insert into log_stat (log_file_id, stat_type, stat_key, stat_value) "
                    "values (%s, %s, %s, %s)",
                    rows,
                )

        conn.commit()
        return file_id

    except pymysql.err.IntegrityError as e:
        conn.rollback()
        raise DbError(
            "保存统计结果失败：数据冲突",
            {"md5": md5, "reason": str(e)},
        ) from e
    except pymysql.err.OperationalError as e:
        conn.rollback()
        raise DbError(
            "保存统计结果失败：数据库错误",
            {"md5": md5, "reason": str(e)},
        ) from e
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# 按类型取前 top 名，用来验证数据真写进去了
def query_summary(top=3):
    conn = connect()
    try:
        with conn.cursor() as cur:
            out = {}
            for stat_type in ("ip", "status", "qps"):
                cur.execute(
                    "select stat_key, sum(stat_value) as cnt from log_stat "
                    "where stat_type = %s group by stat_key "
                    "order by cnt desc limit %s",
                    (stat_type, top),
                )
                out[stat_type] = cur.fetchall()
            return out
    finally:
        conn.close()


if __name__ == "__main__":
    md5 = hashlib.md5(b"test-log").hexdigest()
    stats = {
        "ip": {"1.1.1.1": 100, "2.2.2.2": 30},
        "status": {"200": 120, "500": 10},
    }
    first = save_result(md5, "test.log", 130, 10, stats)
    second = save_result(md5, "test.log", 130, 10, stats)
    print("第一次 file_id:", first)
    print("第二次 file_id:", second)
    print("幂等:", first == second)
    print("server:", connect().get_server_info())
    print("汇总:", query_summary())
