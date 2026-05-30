#!/usr/bin/env python3

from Crypto.Util.number import inverse, long_to_bytes

# Values from challenge.py
N = 5719300213779416325256851872776653027909324796877980266623820853004372155651167511423224414632272876342158618719118179208478001636341899099528646494526203750084698800865188462434285701279650572207992894090302998548688725906478023040537073099383489711982025366195427469717026986469066749571108939664745316435656488569015098153972065848624534362015092440479695978631761994006932750400906889640107789127512764074346248128043011984471359609821574453323047654584775243523902707246020699856068373535601357839110102440230119874693153144413068688290774763773224467944612311432882306158122792771725498430902087078987633336389884507757858000063129368882837142878521889942491669146453735035290325920261800208095653618064739376507336260187554260778403514940612792680404222242859310504543770440022560490322100737286970267071807911344302752300705166258696759916883289235231670330781384554908339815876619584285370056219492835330942549684523
e = 65537
c = 3453154202590746781685514519790348383428338605487549487270128792659072556281636678280511773567835079028474292982679510231923435878884885237624882865115246649902877850582126586700485642648071714339322400197836517905800450717268263616517430543006579504454859265482502621450278452767326791955463687257023337725005567135904550180383037357808080551500610767788808151441444668096967124987975629159782873899298897106442212568575708981853836342013689720692182163885329693891440331336963609012657536639479246741688764399127691883385659118805732448894529515480200957295220114263587314599856974679084450372880727895481251960873630330383420029310933430701001785785351854046372347844767995279204913082872388137875518193161738798774534319457081813314436615565470196729234621658338220505611130331601866241538369675807371138910218433500129704202635106783563290926976284549401611825540046779947998046960428549930559981451042852204851177799625
p_msb = 179147486404486085085422197280000587511454751621722835223057137715594698827830504944899819370021301435651195665075445171992202325618549266532203524209842043097900940030382430999458527271239232703644029719824618423720152310281214560237886839107002367276333501889400036667383309616741614584516490568102496436224

def isqrt(n):
    """Integer square root"""
    if n < 0:
        raise ValueError('square root not defined for negative numbers')
    if n == 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

def check_prefix(x_prefix, bits_known):
    """Check if there exists a completion of x_prefix to a full 320-bit x
    such that p = p_msb + x satisfies the conditions"""
    # x_prefix contains the first bits_known bits of x (MSB first)
    # We need to check if there's any way to set the remaining bits
    
    # Construct the minimum and maximum possible values for x
    # with this prefix
    remaining_bits = 320 - bits_known
    x_min = x_prefix << remaining_bits
    x_max = ((x_prefix + 1) << remaining_bits) - 1
    
    # Corresponding p values
    p_min = p_msb + x_min
    p_max = p_msb + x_max
    
    # Check if there could be any p in [p_min, p_max] such that p^2 divides N
    # We'll check the endpoints and a few points in between
    
    # Check p_min
    p_squared_min = p_min * p_min
    if N % p_squared_min == 0:
        q = N // p_squared_min
        if q.bit_length() >= 1000 and q.bit_length() <= 1050 and q % 2 == 1:
            if p_min * p_min * q == N:
                return p_min  # Found exact match
    
    # Check p_max
    p_squared_max = p_max * p_max
    if N % p_squared_max == 0:
        q = N // p_squared_max
        if q.bit_length() >= 1000 and q.bit_length() <= 1050 and q % 2 == 1:
            if p_max * p_max * q == N:
                return p_max  # Found exact match
    
    # If the range is small enough, check all values
    if p_max - p_min <= 10000:
        for p_candidate in range(p_min, p_max + 1):
            p_squared = p_candidate * p_candidate
            if N % p_squared == 0:
                q = N // p_squared
                if q.bit_length() >= 1000 and q.bit_length() <= 1050 and q % 2 == 1:
                    if p_candidate * p_candidate * q == N:
                        return p_candidate
    
    # Otherwise, we can't definitively rule out this prefix
    return None

# Now let's try to build x bit by bit
x = 0
print('Building x bit by bit from MSB to LSB...')

for bit_pos in range(319, -1, -1):
    # Try setting this bit to 1
    x_test = x | (1 << bit_pos)
    result = check_prefix(x_test, 320 - bit_pos)
    if result is not None:
        # This bit can be 1
        x = x_test
        print(f'Bit {bit_pos}: 1')
    else:
        # This bit must be 0 (trying 1 didn't work)
        print(f'Bit {bit_pos}: 0')
        # x remains unchanged (bit is 0)

print(f'\nFinal x: {x}')
p = p_msb + x
print(f'p = {p}')

# Verify
p_squared = p * p
if N % p_squared == 0:
    q = N // p_squared
    print(f'q = {q}')
    print(f'q bits: {q.bit_length()}')
    if p * p * q == N:
        print('Verification: N = p^2 * q ✓')
        
        # Compute private key and decrypt
        phi = p * (p - 1) * (q - 1)
        d = inverse(e, phi)
        m = pow(c, d, N)
        flag = long_to_bytes(m)
        print(f'Flag: {flag}')
    else:
        print('Verification failed!')
else:
    print('Failed to find valid p!')

