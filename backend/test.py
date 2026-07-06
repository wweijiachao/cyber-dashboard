import psutil as pu

a = pu.cpu_percent(interval=1)

print(a)
