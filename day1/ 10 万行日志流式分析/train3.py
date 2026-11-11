import random, datetime

ips = [f"10.0.{random.randint(0,3)}.{random.randint(1,254)}" for _ in range(200)]
codes = [200]*70 + [301]*8 + [404]*15 + [500]*5 + [502]*2
t0 = datetime.datetime(2026, 11, 11, 0, 0, 0)

with open("access.log", "w", encoding="utf-8") as f:
    for i in range(100000):
        t = t0 + datetime.timedelta(seconds=i * 0.8)
        f.write(f'{random.choice(ips)} - - [{t:%d/%b/%Y:%H:%M:%S}] '
                f'"GET /api/v1/items/{random.randint(1,999)} HTTP/1.1" '
                f'{random.choice(codes)} {random.randint(120,9800)}\n')