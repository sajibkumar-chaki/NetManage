# NetManage Test Cases

| ID | Test | Input | Expected Result |
|---|---|---|---|
| T01 | Valid IPv4 | 192.168.1.1 | Valid |
| T02 | Valid IPv6 | 2001:db8::1 | Valid |
| T03 | Invalid IP | 999.999.1.1 | Invalid |
| T04 | Add device | Router1 / 192.168.1.1 | Device added |
| T05 | Search device | Router1 | Device found |
| T06 | Search missing device | Firewall99 | No match |
| T07 | Generate report | 2 devices | Correct totals |
| T08 | Automated test suite | pytest | All tests pass |
