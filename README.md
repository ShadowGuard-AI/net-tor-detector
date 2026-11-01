# net-tor-detector
Detects if the current network connection is routed through the Tor network. Uses a public Tor exit node list to compare against current IP address (obtained via 'requests'). - Focused on Basic network operations

## Install
`git clone https://github.com/ShadowStrikeHQ/net-tor-detector`

Install the requirements with `pip install -r requirements.txt`.

## Usage
`python3 main.py [params]`

## Services used
The tool makes two requests, and both services are named here so an operator can tell which third parties are contacted:

- `api.ipify.org` (https://api.ipify.org?format=json) is asked for this machine's own public IP address. Asking any service for a public IP shows that service the machine's network address.
- `check.torproject.org` (https://check.torproject.org/exit-addresses) provides the Tor Project exit node list. The list is downloaded in full and compared locally: each `ExitAddress` line in the published list carries an address and a date, and the address field is parsed out of each line for the comparison. No IP address is sent to this service.

## Exit status
The run exits with status 1 when the public IP address cannot be determined, and when the exit node list cannot be fetched, in which case it prints that the Tor check could not be completed instead of reporting a result. A completed check exits with status 0.

## Parameters
- `-h`: Show help message and exit

## License
Copyright (c) ShadowStrikeHQ
