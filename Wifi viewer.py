import subprocess
profiles = subprocess.check_output('netsh wlan show profiles', shell=True).decode('utf-8').split('\n')
names = [line.split(":")[1].strip()
        for line in profiles if "All User Profile" in line]
results = []
for name in names:
    profile_info = subprocess.check_output(
        f'netsh wlan show profile "{name}" key=clear', shell=True).decode('utf-8').split('\n')
    results.append(profile_info)
print("\n" + "\n".join(results))