#!/usr/bin/env python3
"""
Test script for the cookie parser functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the parser functions from the Cookie Mode page
# We'll simulate the functions here for testing
import re
from typing import Dict

def parse_tabular_cookies(cookie_data: str) -> Dict[str, str]:
    """
    Parse cookies from tabular format (browser export format)
    """
    cookies = {}
    lines = cookie_data.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Split by tabs (most common) or multiple spaces
        fields = re.split(r'\t+|\s{2,}', line)
        
        if len(fields) >= 2:
            cookie_name = fields[0].strip()
            cookie_value = fields[1].strip()
            
            # Skip empty names or values
            if cookie_name and cookie_value:
                cookies[cookie_name] = cookie_value
    
    return cookies

def filter_terabox_cookies(cookies: Dict[str, str]) -> Dict[str, str]:
    """
    Filter cookies to get only TeraBox-relevant ones
    """
    # Important TeraBox cookies
    important_cookies = ['ndus', 'BDUSS', 'STOKEN', 'csrfToken', 'lang']
    
    # TeraBox domain patterns
    terabox_domains = ['terabox.com', '1024terabox.com', 'terabox.app']
    
    filtered = {}
    
    for name, value in cookies.items():
        # Include important cookies regardless of domain
        if name in important_cookies:
            filtered[name] = value
        # Include cookies that might be TeraBox related
        elif any(domain in name.lower() for domain in ['terabox', '1024']):
            filtered[name] = value
        # Include session-related cookies
        elif name.lower() in ['sessionid', 'session', 'auth', 'token']:
            filtered[name] = value
        # Include bid cookies (common in TeraBox)
        elif 'bid' in name.lower():
            filtered[name] = value
        # Include stripe cookies (payment-related)
        elif 'stripe' in name.lower():
            filtered[name] = value
    
    return filtered

def format_cookie_string(cookies: Dict[str, str]) -> str:
    """
    Format cookies dictionary into a proper cookie string
    """
    cookie_pairs = []
    for name, value in cookies.items():
        # Clean the value (remove quotes if present)
        clean_value = value.strip('"\'')
        cookie_pairs.append(f"{name}={clean_value}")
    
    return "; ".join(cookie_pairs)

def test_with_provided_data():
    """Test with the data provided by the user"""
    
    sample_data = """__bid_n	1995f6d331f9b86c584207	.1024terabox.com	/	2026-10-24T01:41:32.686Z	29						Medium	
__Host-1PLSID	s.IN|s.youtube:g.a0001ghqvP9lxtG2BjokTe1aYnSlL5_w2sa17vn0uOXH1L6xDwvcqluqKQ9tD3q_6quqcrU-VQACgYKAVwSARESFQHGX2MiPvH7upD_B3U5Ds5CYUMoaRoVAUF8yKpFKzHQdGdvBuBQEqWlGhJv0076	accounts.google.com	/	2026-10-24T01:19:10.290Z	181	✓	✓				High	
__Host-3PLSID	s.IN|s.youtube:g.a0001ghqvP9lxtG2BjokTe1aYnSlL5_w2sa17vn0uOXH1L6xDwvclF3jzv1KbWKtpnDjOZbrnwACgYKAekSARESFQHGX2MiS3j0guxEWhHVyYJxzNhK4BoVAUF8yKqTXZwwLFZFbdw-9sbR69W00076	accounts.google.com	/	2026-10-24T01:19:10.290Z	181	✓	✓	None			High	
__Host-GAPS	1:V8UF2sklbipb9XW7ywaHd3sepfw8SXJC0bSl6PjbWceuG8aXY4FitJsNbz2yzMCEMkG8MI4ETNRXDP_YvPvUeFPbvz0M1A:2NYqG9WpZTu9CbPK	accounts.google.com	/	2026-10-24T01:19:10.290Z	124	✓	✓				High	
__Secure-1PAPISID	NitE3TtP88fB00dO/AMFyQ30R8ESDdhtdH	.google.com	/	2026-10-24T01:19:10.290Z	51		✓				High	
__Secure-1PSID	g.a0001ghqvDWsNSgBXg-UV4NdbRxNAOBQSJylaL59nmrwIEaT5IL4x9X1xTEczjIGHUyEYYmdRgACgYKAcUSARESFQHGX2MisKqT3GzY-9E15TuZueDC2xoVAUF8yKr5DDCqpbsYD8hotxR9eBp10076	.google.com	/	2026-10-24T01:19:10.289Z	167	✓	✓				High	
__Secure-1PSIDCC	AKEyXzUIJDrbGVQqiJjFi4HliXTKCRib18PPzZEUCOUhTgTc1uvdexG-mQ2gszaPsvIihNqE6Q	.google.com	/	2026-09-19T01:41:17.382Z	90	✓	✓				High	
__Secure-1PSIDTS	sidts-CjIBmkD5S7Zxvnj-ncUmCjRe84mmf1WDVBDKiMrmsrwx0-dJuIhHHIza1_gh_9F9BuO9GBAA	.google.com	/	2026-09-19T01:36:21.173Z	94	✓	✓				High	
__Secure-3PAPISID	NitE3TtP88fB00dO/AMFyQ30R8ESDdhtdH	.google.com	/	2026-10-24T01:19:10.290Z	51		✓	None			High	
__Secure-3PSID	g.a0001ghqvDWsNSgBXg-UV4NdbRxNAOBQSJylaL59nmrwIEaT5IL4xDwvclF3jzv1KbWKtpnDjOZbrnwACgYKAWMSARESFQHGX2Miq9Iqq13sDN4F6_NR5Zs7jxoVAUF8yKqnmPh2KxyjhIPYzSL9kcpA0076	.google.com	/	2026-10-24T01:19:10.289Z	167	✓	✓	None			High	
__Secure-3PSIDCC	AKEyXzVl9DO9q5-3XoiwEs6MgSj7xnTl09iBoburfPeLF-xc1WOiNdFqnNWz1XOSkec2OsFnFik	.google.com	/	2026-09-19T01:41:17.383Z	91	✓	✓	None			High	
__Secure-3PSIDTS	sidts-CjIBmkD5S7Zxvnj-ncUmCjRe84mmf1WDVBDKiMrmsrwx0-dJuIhHHIza1_gh_9F9BuO9GBAA	.google.com	/	2026-09-19T01:36:21.174Z	94	✓	✓	None			High	
__stripe_mid	d7a568bf-de37-4191-afa2-144829d37dae05eb46	.dm.1024terabox.com	/	2026-09-19T01:41:43.000Z	54		✓	Strict			Medium	
__stripe_sid	18df916d-6beb-4558-b410-caa96cd57f1a2941b5	.dm.1024terabox.com	/	2025-09-19T02:11:43.000Z	54		✓	Strict			Medium"""

    print("=== Testing Cookie Parser ===")
    print("\n1. Parsing tabular cookie data...")
    
    # Parse all cookies
    all_cookies = parse_tabular_cookies(sample_data)
    print(f"✅ Parsed {len(all_cookies)} total cookies")
    
    # Show all cookies
    print("\nAll parsed cookies:")
    for name, value in all_cookies.items():
        print(f"  {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    print("\n2. Filtering TeraBox-relevant cookies...")
    
    # Filter TeraBox cookies
    terabox_cookies = filter_terabox_cookies(all_cookies)
    print(f"✅ Found {len(terabox_cookies)} TeraBox-relevant cookies")
    
    # Show filtered cookies
    print("\nTeraBox-relevant cookies:")
    for name, value in terabox_cookies.items():
        print(f"  {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    print("\n3. Formatting cookie string...")
    
    # Format as cookie string
    cookie_string = format_cookie_string(terabox_cookies)
    print(f"✅ Generated cookie string ({len(cookie_string)} characters)")
    print(f"\nCookie String: {cookie_string[:200]}{'...' if len(cookie_string) > 200 else ''}")
    
    return all_cookies, terabox_cookies, cookie_string

if __name__ == "__main__":
    test_with_provided_data()
