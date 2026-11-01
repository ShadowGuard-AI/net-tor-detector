import socket
import requests
import logging
import argparse
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_ip(ip):
    """
    Validates if the provided string is a valid IPv4 address.

    Args:
        ip (str): The IP address to validate.

    Returns:
        bool: True if the IP address is valid, False otherwise.
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def get_public_ip():
    """
    Retrieves the public IP address of the current machine using an external service.

    Returns:
        str: The public IP address, or None if an error occurred.
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()['ip']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        return None

def check_tor_exit_node(ip, tor_exit_list_url='https://check.torproject.org/exit-addresses'):
    """
    Checks if the given IP address is a Tor exit node by comparing it against a public list.

    Args:
        ip (str): The IP address to check.
        tor_exit_list_url (str): The URL of the Tor exit node list. Defaults to the Tor Project's official list.

    Returns:
        bool or None: True if the IP address is found in the Tor exit node
        list, False if it was checked and not found, and None when the
        list could not be fetched, so the check result is unknown.
    """
    try:
        response = requests.get(tor_exit_list_url, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        # The published list carries each address on an ExitAddress line
        # together with a date: "ExitAddress 203.0.113.9 2026-10-30 02:03:04".
        # Parse the address field out of each such line and compare those.
        exit_addresses = set()
        for line in response.text.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == "ExitAddress":
                exit_addresses.add(parts[1])
        return ip in exit_addresses
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Tor exit node list: {e}")
        return None

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Detects if the current network connection is routed through the Tor network.")
    return parser

def main():
    """
    Main function to execute the Tor detection logic.
    """
    parser = setup_argparse()
    args = parser.parse_args() # Parse command-line arguments

    public_ip = get_public_ip()

    if public_ip:
        logging.info(f"Public IP address: {public_ip}")

        if not is_valid_ip(public_ip):
            logging.error("Invalid IP address obtained. Exiting.")
            sys.exit(1)

        is_tor = check_tor_exit_node(public_ip)

        if is_tor is None:
            print("Tor check could not be completed: the Tor exit node list could not be fetched.")
            logging.error("Tor check could not be completed: the Tor exit node list could not be fetched.")
            sys.exit(1)
        elif is_tor:
            print("Connection is likely routed through the Tor network.")
            logging.warning("Connection is likely routed through the Tor network.")
        else:
            print("Connection is likely NOT routed through the Tor network.")
            logging.info("Connection is likely NOT routed through the Tor network.")
    else:
        print("Failed to determine public IP address.")
        logging.error("Failed to determine public IP address.")
        sys.exit(1)

if __name__ == "__main__":
    main()