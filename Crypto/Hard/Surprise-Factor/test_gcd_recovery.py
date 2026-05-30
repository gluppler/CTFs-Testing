#!/usr/bin/env python3
"""Test the GCD recovery on known values."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))

from bignum import div
from trace import TRACE

def test_known_values():
    """Test with known values to verify GCD recovery works."""
    N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Choose some test values
    nonce_mask = 0x123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    k = 0xfedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210
    hash_int = 0x1111111111111111111111111111111111111111111111111111111111111111
    privkey = 0x2222222222222222222222222222222222222222222222222222222222222222
    r = 0x3333333333333333333333333333333333333333333333333333333333333333
    
    # Compute values as in ECDSA
    hd = (hash_int + r * privkey) % N
    numerator = (nonce_mask * hd) % N
    denominator = nonce_mask * k  # Full product
    s = (hd * pow(k, -1, N)) % N
    
    print(f"N bits: {N.bit_length()}")
    print(f"nonce_mask bits: {nonce_mask.bit_length()}")
    print(f"k bits: {k.bit_length()}")
    print(f"denominator bits: {denominator.bit_length()}")
    print(f"numerator bits: {numerator.bit_length()}")
    print(f"s: {hex(s)}")
    print(f"hd: {hex(hd)}")
    
    # Generate the trace for div(numerator, denominator, N)
    TRACE.configure({"half", "add", "sub", "div"})
    TRACE.reset()
    result = div(numerator, denominator, N)
    trace_list = TRACE.get_trace()
    trace_str = ''.join(trace_list)
    
    print(f"Trace length: {len(trace_str)}")
    print(f"Result matches s: {result == s}")
    
    # Find the div trace
    div_pos = trace_str.rfind('v')
    if div_pos >= 0:
        gcd_trace = trace_str[div_pos+1:]
        print(f"GCD trace length: {len(gcd_trace)}")
        
        # Simple analysis: count h and s
        h_count = gcd_trace.count('h')
        s_count = gcd_trace.count('s')
        print(f"GCD trace: h={h_count}, s={s_count}")
        
        # Each TZ removal = 2 halves, sometimes with an add between
        # Number of TZ removals = h_count / 2
        tz_count = h_count // 2
        print(f"Estimated TZ removals: {tz_count}")
        
        # Try to manually verify a few steps would work
        # But for now, just confirm we can see the pattern
        
    else:
        print("No 'v' found in trace!")

if __name__ == '__main__':
    test_known_values()