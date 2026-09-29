import ipaddress
import socket
from urllib.parse import urlparse

class SecurityError(Exception):
    """Raised when a URL violates network security policies (e.g., SSRF)."""
    pass

def validate_target_url(target_url: str) -> str:
    """
    Validates a target URL against SSRF threats:
    - Must be http or https
    - Hostname cannot resolve to loopback, private, multicast, or reserved IPs
    """
    parsed = urlparse(target_url)
    
    if parsed.scheme not in ("http", "https"):
        raise SecurityError("Only http and https schemes are permitted.")
        
    hostname = parsed.hostname
    if not hostname:
        raise SecurityError("Invalid URL: missing hostname.")

    try:
        # Resolve hostname to IPv4/IPv6 addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for item in addr_info:
            ip_str = item[4][0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                raise SecurityError(f"Access to private/internal network address ({ip_str}) is prohibited.")
    except socket.gaierror:
        raise SecurityError(f"Unable to resolve host: {hostname}")
        
    return target_url
