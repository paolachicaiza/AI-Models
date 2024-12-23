def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return uptime_seconds

def get_app_version():
    with open('app.version', 'r') as f:
        version = f.readline()
    return version