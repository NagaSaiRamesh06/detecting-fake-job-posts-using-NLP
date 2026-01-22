import subprocess
import sys

with open('test_result.txt', 'w') as f:
    subprocess.run([sys.executable, 'test_jwt.py'], stdout=f, stderr=subprocess.STDOUT, text=True)
