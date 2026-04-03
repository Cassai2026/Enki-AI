import subprocess

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
profile_name = "Default"

subprocess.Popen([chrome_path, f'--profile-directory={profile_name}'])

