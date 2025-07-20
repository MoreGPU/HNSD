import subprocess
import re

from ping3 import ping
import netifaces
import speedtest

import asyncio

from hnsd.core.structures import (
    SpeedTestResult,
    PingTestResult,
    WifiTestResult,
    IPAddress,
    Metric,
    Unit
)

def get_default_gateway():
    return netifaces.gateways()['default'][netifaces.AF_INET][0]

def do_ping_test(address: IPAddress, num_pings: int = 10) -> PingTestResult:
    pings = [ping(address.value) for _ in range(num_pings)]
    avg_ping = sum(pings) / len(pings)
    return PingTestResult(
        ping=Metric(value=avg_ping, unit=Unit.SECONDS)
    )

def do_speed_test() -> SpeedTestResult:
    s = speedtest.Speedtest()
    s.download()
    s.upload()
    results = s.results.dict()
    
    download = results.get("download")
    upload = results.get("upload")
    ping = results.get("ping")
    
    return SpeedTestResult(
        download=Metric(value=download, unit=Unit.MBPS),
        upload=Metric(value=upload, unit=Unit.MBPS),
        ping=Metric(value=ping, unit=Unit.MILLISECONDS)
    )
    
def do_wifi_test() -> WifiTestResult:
    cmd = ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"]
    output = subprocess.check_output(cmd).decode()
    
    def extract(key):
        match = re.search(rf"{key}: (-?\d+)", output)
        return int(match.group(1)) if match else None

    rssi = extract("agrCtlRSSI")
    noise = extract("agrCtlNoise")
    snr = extract("lastRxSNR")
    channel = re.search(r"channel: ([0-9]+)", output).group(1)
    
    return WifiTestResult(
        rssi=Metric(rssi, unit=Unit.MBPS),
        noise=Metric(noise, unit=Unit.MBPS),
        snr=Metric(snr, unit=Unit.MILLISECONDS),
        channel=Metric(channel, unit=Unit.NONE)
    )

    
if __name__ == "__main__":
    LOCAL_ROUTER = IPAddress("192.168.0.1")
    GOOGLE_DNS = IPAddress("8.8.8.8")
    CLOUDFLARE = IPAddress("1.1.1.1")
    
    num_pings = 50
    local_router = do_ping_test(LOCAL_ROUTER, num_pings)
    google_dns = do_ping_test(GOOGLE_DNS, num_pings)
    cloudflare = do_ping_test(CLOUDFLARE, num_pings)
    
    print(f"{local_router=}")
    print(f"{google_dns=}")
    print(f"{cloudflare=}")
    
    speed_test = do_speed_test()
    download_speed = speed_test.download
    upload_speed = speed_test.upload
    ping = speed_test.ping
    
    print(f"{download_speed=}")
    print(f"{upload_speed=}")
    print(f"{ping=}")
    
    wifi_test = do_wifi_test()
    rssi=wifi_test.rssi
    noise=wifi_test.noise
    snr=wifi_test.snr
    channel=wifi_test.channel
    
    print(f"{rssi=}")
    print(f"{noise=}")
    print(f"{snr=}")
    print(f"{channel=}")

