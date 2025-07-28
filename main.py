import argparse
import asyncio
from pathlib import Path
import yaml
from typing import Dict, Any, List

from hnsd.services.ping_service import (
    PingTestConfig,
    do_ping_test_async
)
from hnsd.services.log_writer import LogWriter
from hnsd.entities.ping_result import PingTestResult

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)


async def run_pings(configs: List[PingTestConfig], test_logger: LogWriter, ping_logger: LogWriter) -> PingTestResult:
    """Run asynchronous pings for a list of hosts."""
    futures = [
        do_ping_test_async(config, test_logger, ping_logger)
        for config in configs
    ]
    results = await asyncio.gather(*futures)
    
    for result in results:
        print(f"{result.host}: {result.average_latency} {result.unit.value}")


async def main():
    parser = argparse.ArgumentParser(description="Ping test runner")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("./config/config.yaml"),
        help="Path to configuration file"
    )
    parser.add_argument(
        "--test-log",
        type=Path,
        help="Override log file path from config"
    )
    parser.add_argument(
        "--ping-log",
        type=Path,
        help="Override log file path from config"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    test_log_path = args.test_log if args.test_log else Path(config.get("test_log_path", "/var/log/ping_test.log"))  
    ping_log_path = args.ping_log if args.ping_log else Path(config.get("ping_log_path", "/var/log/ping_stream.log"))  
    
    from hnsd.services.log_writer import setup_logger
    
    test_logger = setup_logger("test_logger", test_log_path)
    ping_logger = setup_logger("ping_logger", ping_log_path)
     
    hosts = [host["name"] for host in config["hosts"]]
    addresses = [addresses["address"] for addresses in config["hosts"]]
    num_pings = [config["num_pings"] for _ in range(len(hosts))]
    timeouts = [config["timeout"] for _ in range(len(hosts))]
    
    assert len(hosts) == len(addresses), "Host/address mismatch in config."
    
    ping_configs = [
        PingTestConfig(
            host=host, 
            address=address, 
            num_pings=num_pings, 
            timeout=timeout
        )
        for host, address, num_pings, timeout 
        in zip(hosts, addresses, num_pings, timeouts)
    ]
    
    await run_pings(ping_configs, test_logger, ping_logger)


if __name__ == "__main__":
    asyncio.run(main())
