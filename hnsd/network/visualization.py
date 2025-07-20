from typing import Any, List

from hnsd.network.structures import PingTestResult

def display_ping_tests(tests: List[PingTestResult]):
    for test in tests:
        if test.name:
            print(f"{test.name} ping: {test.ping:.4f} {test.unit.value}")
        else:
            print(f"ping: {test.ping:.4f} {test.unit.value}")