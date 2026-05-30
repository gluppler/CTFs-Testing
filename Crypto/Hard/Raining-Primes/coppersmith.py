#!/usr/bin/env python3
"""
Bivariate Coppersmith implementation for factoring RSA modulus
given n = (a1*r + b1)*(a2*r + b2) with known r.
"""
import sys
from math import gcd
from fpylll import IntegerMatrix, LLL

def coppersmith_factor(n, r, X=2**384, Y=2**256, m=3):
    """
    Given n and r, find factors p, q such that n = p*q
    where p = a1*r + b1, q = a2*r + b2
    with |a1| < X, |a2| < X, |b1| < Y, |b2| < Y.
    
    Uses bivariate Coppersmith on f(x,y) = r*x + y.
    """
    # We want to find (a1, b1) such that p = r*a1 + b1 divides n.
    # The polynomial is f(x,y) = r*x + y.
    # Condition: X * Y < r (marginally satisfied: 2^640 = 2^384 * 2^256)
    
    # Build the lattice for Howgrave-Graham's method
    # Monomials: x^i * y^j for i+j <= m
    # Shifts: f(x,y)^k * n^(m-k) for k in 0..m
    # Plus: x^i * y^j * f(x,y)^k * n^(m-k) for various i,j,k
    
    # Actually, let's use the simpler approach:
    # Build lattice from coefficients of f(x,y)^i * n^(deg-i) for i in 0..deg
    
    # For bivariate Coppersmith, we build a lattice where
    # each row corresponds to a polynomial shift.
    # The lattice dimension is O(m^2).
    
    deg = m
    
    # Generate monomials: x^i * y^j for i+j <= deg
    monomials = []
    for total in range(deg + 1):
        for i in range(total + 1):
            j = total - i
            monomials.append((i, j))
    
    n_mon = len(monomials)
    print(f"Number of monomials: {n_mon}")
    
    # Generate polynomial shifts: for each monomial x^i*y^j,
    # multiply by f(x,y)^k * n^{deg-i-j-k} for appropriate k
    # Total degree constraint: i+j+k <= deg
    
    polynomials = []
    poly_info = []  # (i, j, k) for each polynomial
    
    for i_idx, (i, j) in enumerate(monomials):
        k_max = deg - i - j
        for k in range(k_max + 1):
            poly_info.append((i, j, k))
            # Polynomial: x^i * y^j * f(x,y)^k * n^(deg - i - j - k)
    
    n_poly = len(poly_info)
    print(f"Number of polynomials: {n_poly}")
    
    # Build the coefficient matrix
    # Row for polynomil p_idx, column for monomial m_idx
    # Coefficient of monomial (di, dj) in polynomial p_idx
    
    # We need to expand f(x,y)^k where f(x,y) = r*x + y
    # f(x,y)^k = sum_{t=0}^k C(k,t) * (r*x)^t * y^(k-t)
    #          = sum_{t=0}^k C(k,t) * r^t * x^t * y^(k-t)
    
    from math import comb
    
    # Precompute binomial coefficients
    binom = {}
    for k in range(deg + 1):
        for t in range(k + 1):
            binom[(k, t)] = comb(k, t)
    
    # Build the matrix
    M = IntegerMatrix(n_poly, n_mon)
    
    for p_idx, (i, j, k) in enumerate(poly_info):
        # This polynomial is: x^i * y^j * f(x,y)^k * n^(deg - i - j - k)
        n_power = deg - i - j - k
        
        # For each term in f(x,y)^k, we get x^t * y^(k-t) * r^t * C(k,t)
        # So total monomial: x^(i+t) * y^(j+k-t) * r^t * C(k,t) * n^n_power
        
        for t in range(k + 1):
            di = i + t
            dj = j + k - t
            
            # Find monomial index
            try:
                m_idx = monomials.index((di, dj))
            except ValueError:
                continue
            
            coeff = r**t * binom[(k, t)] * (n ** n_power)
            M[p_idx, m_idx] = coeff
    
    print(f"Lattice dimension: {n_poly} x {n_mon}")
    
    # Apply scaling: x -> x*X, y -> y*Y at monomial level
    for m_idx, (mi, mj) in enumerate(monomials):
        for p_idx in range(n_poly):
            M[p_idx, m_idx] = M[p_idx, m_idx] * (X ** mi) * (Y ** mj)
    
    # Apply LLL
    print("Running LLL...")
    M_reduced = LLL.reduction(M)
    print("LLL done!")
    
    # Extract short vectors and try to find factors
    for row_idx in range(n_poly):
        # Get the coefficients of the polynomial represented by this row
        # This polynomial should have small coefficients (after scaling)
        # Unscale: coeff = coeff_scaled / (X^mi * Y^mj)
        
        # The polynomial h(x, y) = sum coeff * x^mi * y^mj
        # We want h(a1, b1) = 0 (mod something)
        
        # Since h is a combination of shifts, h(a1,b1) is small and
        # divisible by n^m / something
        
        # Extract the coefficients
        h_coeffs = {}
        for m_idx, (mi, mj) in enumerate(monomials):
            val = M_reduced[row_idx, m_idx]
            if val != 0:
                unscaled = val // (X**mi * Y**mj)
                if unscaled * (X**mi * Y**mj) != val:
                    unscaled = val / (X**mi * Y**mj)  # float, might be lossy
                h_coeffs[(mi, mj)] = unscaled
        
        if not h_coeffs:
            continue
        
        # Compute h(a1, a2) for various candidate a1, a2
        # Actually, we need a different approach:
        # Find roots of h(xX, yY) = 0
        
        # For bivariate polynomial, find small integer roots
        # Try to extract factor via resultant or gcd
        
        # Simple approach: if h(x, y) has degree 1 in x:
        # h(x, y) = c1*x + c2*y + c3
        # Then a1 = -(c2*y + c3)/c1
        # For some y = b1 (unknown)
        
        # Actually, the resultant of h1 and h2 gives a univariate polynomial
        # whose roots include the shared x or y coordinate.
        
        # But we need TWO polynomials (two reduced rows).
        # Take the first two reduced rows and compute resultant.
        
        if row_idx >= 1:
            # Try resultant with previous row
            # g(x,y) = row_0, h(x,y) = row_1
            # res_y(g, h) has x roots including a1
            # res_x(g, h) has y roots including b1
            
            # Extract coefficients for previous row
            g_coeffs = {}
            for m_idx, (mi, mj) in enumerate(monomials):
                val = M_reduced[0, m_idx]
                if val != 0:
                    unscaled = val // (X**mi * Y**mj)
                    g_coeffs[(mi, mj)] = unscaled
            
            # Try to compute resultant manually for simple cases
            if len(h_coeffs) <= 10 and len(g_coeffs) <= 10:
                # Compute res_y(g, h) - find common root in y
                # This is messy for high-degree polynomials.
                pass
    
    return None

def find_factor_simple(n, r):
    """Try a simpler approach: find p = a*r + b by checking small b values."""
    print("Trying simple approach: check small b values...")
    
    n_r = n % r
    n_q2 = n // (r * r)
    n_qr = (n // r) % r
    
    # For each pair of b values from our samples that multiply to n_r:
    # S = a1*b2 + a2*b1 ≈ n_qr (or n_qr + r)
    # a1*a2 ≈ n_q2
    
    # Let me try to compute a1 and a2 directly using the formulas
    # We know: 
    # P = b1*b2 = n_r
    # S = a1*b2 + a2*b1 = n_qr or n_qr + r
    # Q = a1*a2 = n_q2 or n_q2 - 1
    
    # Try all combinations of S and Q
    for Q in [n_q2, n_q2 - 1, n_q2 + 1]:
        if Q <= 0:
            continue
        for S in [n_qr, n_qr + r, n_qr - r]:
            if S <= 0 or S >= 2**641:
                continue
            
            # We have:
            # a1*a2 = Q
            # a1*b2 + a2*b1 = S
            # b1*b2 = P = n_r
            
            # From b1*b2 = P: b2 = P / b1
            # From a1*b2 + a2*b1 = S: a1*P/b1 + a2*b1 = S
            # → P*a1 + a2*b1^2 = S*b1
            # → a2*b1^2 - S*b1 + P*a1 = 0
            # → b1 = (S ± sqrt(S^2 - 4*P*a1*a2)) / (2*a2)
            # → b1 = (S ± sqrt(S^2 - 4*P*Q)) / (2*a2)
            
            disc = S*S - 4*Q*n_r
            if disc <= 0:
                continue
            
            # Try to find integer sqrt
            from math import isqrt
            sqrt_disc = isqrt(disc)
            if sqrt_disc * sqrt_disc != disc:
                continue
            
            # b1 = (S - sqrt_disc) / (2) ... but we need a2 which we don't know
            # Let me instead try to find a1, a2 from Q = a1*a2
            
            # For each known a value from raining primes
            # ... but a1 and a2 might not be in our samples...
            
            # Alternative: use gcd approach
            # p = a1*r + b1
            # n mod (a1*r + b1) = 0
            
            # Try to find a1 using the discriminant
            # We need a2 such that 2*a2 divides (S - sqrt_disc)
            num = S - sqrt_disc
            if num <= 0:
                num = S + sqrt_disc
            
            # a2 must divide num such that 2*a2 = num//b1
            # b1 = (S - sqrt_disc) / (2*a2)
            # So a2 = (S - sqrt_disc) / (2*b1)
            # But we don't know b1 either!
            
            # Let me try all factors of Q as candidates for a1 and a2
            # Q is 768 bits... too many factors
    
    return None

if __name__ == '__main__':
    # Test with simple parameters
    r = 3437737891708250164010438009564758468541609891740546469788040167738222726671459546499480366423691061745030851866201598194680969834604763005258448258651419818703144021145530671762742756448938909
    n = 10556242293761844297113990582703814385282199834377290513237726943923239788601276823551605219565894817273914952514370587525912005981121052168862299850637154932951346986083459178377836350613536971862997354335127939918743139117110695877925536968750518835066432078300244288400911999950376465793853565598926219424768573600390118035530513845169961367726300240566450792716447854291883344843906415275943756435524886561249315496134856712238705051847411085471607070773766261159784956327228973928220610871267000121614120647823451253874423952495868368509587021623150765845305441944213979030021892769017256237133607196244602789079
    
    find_factor_simple(n, r)
