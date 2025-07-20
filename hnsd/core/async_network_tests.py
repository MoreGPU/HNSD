import asyncio
from collections import defaultdict
from ping3 import ping
import time
from typing import *


from hnsd.core.structures import (
    PingTestResult,
    IPAddress,
    Metric,
    Unit
)

LOCAL_ROUTER = IPAddress("192.168.0.1")
GOOGLE_DNS = IPAddress("8.8.8.8")
CLOUDFLARE = IPAddress("1.1.1.1")    

def display_ping_tests(**kwargs):
    for kw, arg in kwargs.items():
        print(f"{kw}: {arg.ping.value:.4f}")
        
############################################################
############ SEQUENTIAL TESTS / CONCURRENT PINGS ###########
############################################################

async def aping(addr: str, name: str = None, i: int = 2) -> float:
    loop = asyncio.get_running_loop()
    print(f"{name}: sleeping for {i} seconds...")
    await asyncio.sleep(i)
    return await loop.run_in_executor(None, ping, addr)
    
async def do_aping_test(address: IPAddress, name: str, num_pings: int = 10) -> PingTestResult:
    addr = address.value
    pings = await asyncio.gather(
        *[aping(addr, name) for _ in range(num_pings)]
    )
    avg_ping = sum(pings) / len(pings)
    return PingTestResult(
        ping=Metric(value=avg_ping, unit=Unit.SECONDS)
    )

async def sequential_tests_concurrent_pings():
    """This asynchronously sends N pings for each test. Tests happen in sequence."""
    local_ping_test = await do_aping_test(LOCAL_ROUTER, "local", num_pings=10)
    google_ping_test = await do_aping_test(GOOGLE_DNS, "google", num_pings=10)
    cloudflare_ping_test = await do_aping_test(CLOUDFLARE, "cloudflare", num_pings=10)
    
    display_ping_tests(
        local_ping_test=local_ping_test, 
        google_ping_test=google_ping_test, 
        cloudflare_ping_test=cloudflare_ping_test
    )

############################################################
######## CONCURRENT TESTS / SEQUENTIAL PINGS ###############
############################################################

def blocking_func(addr, num_pings) -> PingTestResult:
    print('running test')
    results = [ping(addr) for _ in range(num_pings)]
    avg_ping = sum(results) / len(results)
    return PingTestResult(
        ping=Metric(value=avg_ping, unit=Unit.SECONDS)
    )

async def do_ping_test(address: IPAddress, name: str, num_pings: int = 10) -> PingTestResult:
    addr = address.value
    loop = asyncio.get_running_loop()
    print(f"{name}: sleeping for one seconds...")
    await asyncio.sleep(1)
    return await loop.run_in_executor(None, blocking_func, addr, num_pings)

async def per_host_concurrent_ping_test(num_pings: int = 10):

    results = await asyncio.gather(
        do_ping_test(LOCAL_ROUTER, "local", num_pings),
        do_ping_test(GOOGLE_DNS, "google", num_pings),
        do_ping_test(CLOUDFLARE, "cloudflare", num_pings)
    )
    
    display_ping_tests(
        local_ping_test=results[0], 
        google_ping_test=results[1], 
        cloudflare_ping_test=results[2]
    )
    
############################################################
########## FULLY CONCURRENT TESTS AND PINGS ################
############################################################

async def fully_concurrent_tests_and_pings():
    
    num_pings = 10
    
    addresses = [
        ("local", LOCAL_ROUTER.value),
        ("google", GOOGLE_DNS.value),
        ("cloudflare", CLOUDFLARE.value)
    ]
    
    ip_task_pairs = [
        (name, asyncio.create_task(aping(addr, name))) 
        for name, addr in addresses
        for _ in range(num_pings)
    ]
        
    await asyncio.gather(
        *(task for _, task in ip_task_pairs)
    )
    
    results_by_ip: dict[IPAddress, list[float]] = defaultdict(list)
    for ip, task in ip_task_pairs:
        result = task.result()
        if result:
            results_by_ip[ip].append(result)
        
    results = {}
    for ip, vals in results_by_ip.items():
        avg_ping = sum(vals) / len(vals)
        results[ip] = PingTestResult(
            ping=Metric(value=avg_ping, unit=Unit.SECONDS)
        )
    
    display_ping_tests(
        local_ping_test=results['local'], 
        google_ping_test=results['google'], 
        cloudflare_ping_test=results['cloudflare']
    )


if __name__ == "__main__":
    print("Running tests sequentially, pings concurrently:\n")
    start_time = time.time()
    asyncio.run(sequential_tests_concurrent_pings())
    total_time = (time.time() - start_time)
    print(f"\ncompleted in {total_time:.2f} seconds\n")
    
    print("\n\nRunning tests concurrently, pings sequential:\n")
    start_time = time.time()
    asyncio.run(per_host_concurrent_ping_test())
    total_time = (time.time() - start_time)
    print(f"\ncompleted in {total_time:.2f} seconds\n")

    print("\n\nRunning tests and pings concurrently:\n")
    start_time = time.time()
    asyncio.run(fully_concurrent_tests_and_pings())
    total_time = (time.time() - start_time)
    print(f"\ncompleted in {total_time:.2f} seconds\n")
    
