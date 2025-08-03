import asyncio 
from enum import Enum
from dataclasses import dataclass
from statistics import mean
import time
from typing import Optional, List
from datetime import datetime

from ping3 import ping

from hnsd.services.log_writer import LogWriter
from hnsd.entities.ping_result import (
    PingResult,
    PingTestConfig,
    PingTestResult,
    Unit
)

def ping_once(host: str, address: str, logger: Optional[LogWriter]=None) -> PingResult:    
    try:
        latency = ping(address)
        success = latency is not None
        error = None if success else "No response"
    except Exception as e:
        latency = None
        success = False
        error = str(e)
    
    result = PingResult(
        host=host,
        address=address,
        success=success,
        latency=latency,
        unit=Unit.SECONDS,
        timestamp=datetime.now().isoformat(),
        error=error
    )
    
    if logger:
        logger.info(result.to_json())
    
    return result

        
def build_ping_test_results(results: List[PingResult], config: PingTestConfig) -> PingTestResult:
    successful = [r.latency for r in results if r.success and r.latency is not None]
    avg_latency = mean(successful) if successful else None
    success_rate = len(successful) / len(results) * 100
    return PingTestResult(
        host_name=config.host_name,
        address=config.address,
        unit=Unit.SECONDS,
        average_latency=avg_latency,
        success_rate=success_rate,
        timestamp=datetime.now().isoformat(),
        metadata=config
    )
    
    
def do_ping_test(
    config: PingTestConfig,
    test_logger: Optional[LogWriter] = None,
    ping_logger: Optional[LogWriter] = None
) -> PingTestResult:
    host_name = config.host_name
    address = config.address
    num_pings = config.num_pings
    timeout = config.timeout
    
    results = []
    for _ in range(num_pings):
        results.append(ping_once(host_name, address, ping_logger))
        time.sleep(timeout)
     
    results = build_ping_test_results(
        results=results,
        config=config
    )
    
    if test_logger:
        test_logger.info(results.to_json())
    
    return results
    
async def do_ping_test_async(
    config: PingTestConfig,
    test_logger: Optional[LogWriter] = None,
    ping_logger: Optional[LogWriter] = None,
):
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(
        None,
        do_ping_test,
        config,
        test_logger,
        ping_logger
    )
     
    if test_logger:
        test_logger.info(results.to_json())
    
    return results
