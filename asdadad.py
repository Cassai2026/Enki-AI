import subprocess

# Try to run Chrome using the full path
try:
    subprocess.run(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"])
except Exception as e:
    print(f"Error launching Chrome: {e}")