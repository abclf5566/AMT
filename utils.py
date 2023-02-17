import time

def wait_until(timestamp):
    """等待到指定时间戳"""
    while time.time() < timestamp:
        time.sleep(1)
