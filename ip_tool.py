import os
import json
import argparse
import subprocess
import ipaddress
from collections import Counter

def get_running_containers():
    """Retrieve a list of running container IDs (works for Docker and Kubernetes)."""
    try:
        result = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True, check=True)
        container_ids = result.stdout.strip().split("\n")
        return [cid for cid in container_ids if cid]
    except Exception as e:
        print(f"Error getting running containers: {e}")
        return []

def collect_ips(output_file="collected_ips.json"):
    """Collect CIDR blocks from all running containers using 'ip -j addr show'."""
    ip_networks = []
    containers = get_running_containers()
    
    for container in containers:
        try:
            result = subprocess.run(["docker", "exec", container, "ip", "-j", "addr", "show"], capture_output=True, text=True, check=True)
            interfaces = json.loads(result.stdout)
        except Exception as e:
            print(f"Error running 'ip -j addr show' in container {container}: {e}")
            continue
        
        for iface in interfaces:
            if iface.get("ifname") == "lo":  # Exclude loopback
                continue
            for addr_info in iface.get("addr_info", []):
                ip = addr_info.get("local")
                prefix = addr_info.get("prefixlen")
                if ip and prefix:
                    network = str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False))
                    ip_networks.append(network)
    
    # Overwrite the file with the latest collected IP networks
    with open(output_file, "w") as f:
        json.dump(ip_networks, f, indent=4)
    
    print(f"Collected IP networks saved to {output_file}")

def check_collision(input_file):
    """Check for duplicate IP networks by reading from the specified file."""
    try:
        with open(input_file, "r") as f:
            ip_networks = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return
    
    counter = Counter(ip_networks)
    duplicates = {network: count for network, count in counter.items() if count > 1}
    
    if duplicates:
        print("Colliding IP networks detected:")
        collision_result = {"colliding_networks": list(duplicates.keys())}
        print(json.dumps(collision_result, indent=4))
    else:
        print("No collisions found.")

def main():
    parser = argparse.ArgumentParser(description="IP Tool for collecting and checking IP network collisions.")
    parser.add_argument("--check-collision", metavar="FILE", type=str, help="Check for IP network collisions using the specified file")
    args = parser.parse_args()
    
    collect_ips()
    
    if args.check_collision:
        check_collision(args.check_collision)

if __name__ == "__main__":
    main()
