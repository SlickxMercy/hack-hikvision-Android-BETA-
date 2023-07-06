import os
import re
import sys
import socket
import threading
import requests
from datetime import datetime
import random

def parse_ip_range(ip_range):
    start_ip, end_ip = ip_range.split('-')
    return start_ip.strip(), end_ip.strip()

def scan_ips(ip_ranges):
    ips = []
    for ip_range in ip_ranges:
        start_ip, end_ip = parse_ip_range(ip_range)
        start_ip_split = list(map(int, start_ip.split('.')))
        end_ip_split = list(map(int, end_ip.split('.')))
        for i in range(start_ip_split[0], end_ip_split[0]+1):
            for j in range(start_ip_split[1], end_ip_split[1]+1):
                for k in range(start_ip_split[2], end_ip_split[2]+1):
                    for l in range(start_ip_split[3], end_ip_split[3]+1):
                        ip = f"{i}.{j}.{k}.{l}"
                        ips.append(ip)
    random.shuffle(ips)
    return ips

def test_ip(ip, port):
    url = f"http://{ip}:{port}/doc/page/login.asp?"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def find_cameras(ip_ranges, port):
    ips = scan_ips(ip_ranges)
    total_ips = len(ips)
    scanned_ips = 0
    saved_ips = 0

    class CameraScanner(threading.Thread):
        def __init__(self, ip_list):
            threading.Thread.__init__(self)
            self.ip_list = ip_list

        def run(self):
            nonlocal scanned_ips, saved_ips
            for ip in self.ip_list:
                if test_ip(ip, port):
                    with open("host.txt", "a+") as f:
                        existing_ips = set(f.read().splitlines())
                        if ip not in existing_ips:
                            f.write(f"{ip}\n")
                            saved_ips += 1
                scanned_ips += 1
                progress = (scanned_ips / total_ips) * 100
                print(f"\rProgress: {progress:.2f}% | Saved IPs: {saved_ips}", end='', flush=True)

    threads = []
    num_threads = 500
    chunk_size = len(ips) // num_threads
    for i in range(num_threads):
        thread_ips = ips[i*chunk_size:(i+1)*chunk_size]
        thread = CameraScanner(thread_ips)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\nScan completed.")

if __name__ == '__main__':
    ip_ranges = input("Enter the IP address ranges (separated by commas): ").split(',')
    port = input("Enter the port to scan: ")
    find_cameras(ip_ranges, int(port))
