import argparse
import asyncio 
import time
from typing import Optional

from ping3 import ping

from hnsd.network import (
    LOCAL_ROUTER,
    GOOGLE_DNS,
    CLOUDFLARE
)
from hnsd.network.structures import (
    IPAddress,
    Metric,
    PingTestResult,
    Unit,
    PingTestConfig
)
from hnsd.network.visualization import display_ping_tests
    
    
def do_ping_test(
    address: IPAddress, 
    name: Optional[str] = None,
    config: Optional[PingTestConfig] = None,
    ) -> Metric:
    """Average ping of N calls"""
    num_pings = config.num_pings
    delay = config.delay
    
    results = []
    for _ in range(num_pings):
        time.sleep(delay)
        results.append(ping(address.value))
    
    avg_ping = sum(results) / len(results)
    
    return PingTestResult(
        ping=avg_ping,
        unit=Unit.SECONDS,
        name=name,
        metadata=config
    )


async def do_ping_test_async(
    address: IPAddress, 
    name: Optional[str] = None, 
    config: Optional[PingTestConfig] = None
    ) -> Metric:
    
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, do_ping_test, address, name, config)


async def do_all_ping_tests(config: PingTestConfig):
    
    futures = asyncio.gather(
        do_ping_test_async(LOCAL_ROUTER, "local", config),
        do_ping_test_async(GOOGLE_DNS, "google", config),
        do_ping_test_async(CLOUDFLARE, "cloudflare", config)
    )
    
    ping_tests = await futures
    display_ping_tests(ping_tests)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping test runner")
    
    parser.add_argument(
        "--num_pings", 
        default=5, 
        type=int, 
        help="Number of times to ping each address."
    )
    parser.add_argument(
        "--delay", 
        default=0, 
        type=int, 
        help="Number of seconds to wait between each ping."
    )
    args = parser.parse_args()

    config = PingTestConfig(
        num_pings=args.num_pings,
        delay=args.delay
    )    
    
    asyncio.run(do_all_ping_tests(config))