import psutil
import subprocess
import time


script_path = "../InitCli.py"
proc = subprocess.Popen(["python3", script_path])
p = psutil.Process(proc.pid)

try:
    while proc.poll() is None:
        mem = p.memory_info().rss / (1024 ** 2)
        print(f"Memória usada: {mem:.2f} MB")
        time.sleep(1)
finally:
    proc.terminate()
