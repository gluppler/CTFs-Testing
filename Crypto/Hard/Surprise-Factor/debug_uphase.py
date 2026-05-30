#!/usr/bin/env python3
"""Debug the forward simulation for the correct u-phase length K."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
from bignum import div
from trace import TRACE

N = CURVE_N

d_test = 0x1337
hash_int = 0x936062b5d1eab7ae33bd038260bc88f61bafda75d1b7f86c7455a5c810b20000
r = 0xa23b92d900b788a44a1f03b6afe5f78b6ae497e47bfe9e03631e9d66427e9f03
m2 = 0xfc6e91580c1936f44c3e4609a0aa10d0442e48c0facb84b74eca0effc2ebd7e0
k = 0xfeadeedd779b203479d10e751b3c6fa1f50e85acc4ffc7e7d22cfcae0ba27228

hd = hash_int + r * d_test  # ~268 bits
numerator = m2 * hd  # ~524 bits (matches actual sign())
denominator = m2 * k  # ~512 bits
s = hd * pow(k, -1, N) % N

print(f"numerator bits: {numerator.bit_length()}")
print(f"denominator bits: {denominator.bit_length()}")
print(f"s = {hex(s)}")

# Actually run the GCD and collect the exact state
q = m2 * hd  # numerator to div
a_mod = q % N  # what div does: a = mod(a, N)
print(f"a_mod = {hex(a_mod)}")

# Run the actual GCD manually  
u = denominator
v = N
x1 = a_mod
x2 = 0

u_tz_counts_actual = []
v_tz_counts_actual = []
x1_parity_u_tz = []
x2_parity_v_tz = []
total_tz_counts = []

step = 0
first_v_sub = None

while u != 1 and v != 1:
    utz = 0
    while (u & 1) == 0:
        p = x1 & 1
        u //= 2
        if p:
            x1 = (x1 + N) // 2
        else:
            x1 //= 2
        utz += 1
        x1_parity_u_tz.append(p)
    
    vtz = 0
    while (v & 1) == 0:
        p = x2 & 1
        v //= 2
        if p:
            x2 = (x2 + N) // 2
        else:
            x2 //= 2
        vtz += 1
        x2_parity_v_tz.append(p)
    
    total_tz = utz + vtz
    total_tz_counts.append(total_tz)
    
    if step == 0:
        u_tz_counts_actual.append(utz)
        v_tz_counts_actual.append(vtz)
    
    if vtz > 0 and first_v_sub is None:
        first_v_sub = step
        print(f"First v-TZ at step {step} (0-indexed), utz={utz}, vtz={vtz}")
    
    if u >= v:
        if u == v:
            u = 0
            break
        u -= v
        x1 -= x2
    else:
        v -= u
        x2 -= x1
    
    step += 1

K = first_v_sub - 1 if first_v_sub else step
print(f"Total steps: {step}")
print(f"K (u-phase iterations) = first_v_sub - 1 = {K}")
print(f"u-phase actually has K={K} iterations")

# Verify: number of u-TZ runs before first v-TZ = K
# For the first K iterations: vtz_actual = 0, utz_actual > 0
# For iteration K: vtz_actual = 0, utz_actual > 0 (the one where u < N after TZ)

# Now check: can we compute u_0 from the trace's total TZ counts for first K iterations?
total_utz_first_K = sum(u_tz_counts_actual[:K+1])  # from 0 to K inclusive
print(f"Total TZ units in first {K+1} iterations: {total_utz_first_K}")

# The total TZ between ss markers in each iteration = utz + vtz
# For first K iterations: vtz = 0, so total = utz
# For iteration K: vtz = 0, total = utz
# So first K+1 (= K iterations + the transition iteration) have total = utz

# Actually wait, let me recount. Looking at the actual trace:
# Let's see what the 'total_tz_counts' array looks like

print(f"\nFirst 10 total TZ per iteration: {total_tz_counts[:10]}")
print(f"Last 10 total TZ per iteration: {total_tz_counts[-10:] if len(total_tz_counts) > 10 else total_tz_counts}")

# The u-phase consists of the first K+1 iterations where K is the one with first v-TZ
# Wait, iteration K is the one where vtz > 0 first appears.
# But iterations before K have only u-TZ.
# Iteration K has BOTH u-TZ and v-TZ (vtz > 0).
# So the u-phase has K pure-u iterations (0 through K-1).

# Actually, the u-phase ENDS when after u-TZ, u_odd < N.
# This happens during iteration K (the first v-subtraction iteration).
# In iteration K: u-TZ still pure, but after TZ, u_odd < N.
# Then: u < v = N: subtract v = N - u (v-subtraction).
# Now v is even.
# In iteration K+1: u is odd (no u-TZ), v is even (v-TZ happens).

# So K = number of iterations before the first v-subtraction
# = first_v_sub - 1

# Let me figure this out differently.
# In the u-phase: each iteration has u >= N after TZ, so u-subtraction.
# The last u-subtraction happens at iteration u_end_idx.
# After that: u < N.
# In the next iteration: u might be even (from u -= N), TZ happens. After TZ, u_odd < N.
# Then: u < v = N: v-subtraction.

# So the u-phase INCLUDES the iteration where u becomes < N after TZ.
# That iteration still has pure u-TZ (subtraction is still u-subtraction or v-subtraction).

# Hmm, let me be more careful. Let me count the subtractions that are u-subtractions.

u_phase_sub_count = 0
u_sim = denominator
v_sim = N
x1_sim = a_mod
x2_sim = 0

for it in range(step):
    # Simulate this iteration
    utz = 0
    while u_sim and (u_sim & 1) == 0:
        u_sim //= 2
        # x1 tracking (not relevant for u tracking)
        if x1_sim & 1:
            x1_sim = (x1_sim + N) // 2
        else:
            x1_sim //= 2
        utz += 1
    
    vtz = 0
    while v_sim and (v_sim & 1) == 0:
        v_sim //= 2
        if x2_sim & 1:
            x2_sim = (x2_sim + N) // 2
        else:
            x2_sim //= 2
        vtz += 1
    
    is_u_sub = u_sim >= v_sim
    if is_u_sub:
        u_phase_sub_count += 1
        
    if it == 0:
        print(f"\nIteration {it}: utz={utz}, vtz={vtz}, u_sub={is_u_sub}, u_val={u_sim.bit_length()}b, u >= N? {u_sim >= N}")
    
    if u_sim >= v_sim:
        # u-subtraction
        if u_sim == v_sim:
            u_sim = 0
            break
        u_sim -= v_sim
        x1_sim -= x2_sim
    else:
        # v-subtraction  
        v_sim -= u_sim
        x2_sim -= x1_sim
        if first_v_sub is not None and it <= first_v_sub:
            print(f"Iteration {it}: FIRST v-subtraction (u={u_sim.bit_length()}b, v={v_sim.bit_length()}b, u<N after TZ)")
    
    if it < 5 or it == first_v_sub:
        print(f"  After iteration {it}: u bits={u_sim.bit_length()}, u_even={u_sim%2==0}, v bits={v_sim.bit_length()}, v_even={v_sim%2==0}")

print(f"\nu-subtractions: {u_phase_sub_count}")
print(f"Total iterations: {step}")
print(f"First v-subtraction at iteration: {u_phase_sub_count}")

# So K = u_phase_sub_count is the number of u-subtractions.
# The number of pure u-TZ runs (where v-TZ = 0) = u_phase_sub_count
# But wait, at the transition iteration, v-TZ is still 0. So the transition iteration
# ALSO has pure u-TZ. So total pure u-TZ runs = u_phase_sub_count + 1?

# Let me check: at the transition iteration:
# u_tz > 0 (u is even after previous subtract)
# v_tz = 0 (v = N, odd)
# After TZ: u_odd < N
# Since u < v: v -= u (v-subtraction, NOT u-subtraction)

# So this iteration has pure u-TZ but a v-subtraction.
# So the number of pure u-TZ runs = u_phase_sub_count + 1 (the transition)
# But u_phase_sub_count is the number of u-subtractions, not iterations.

# Let me just use: K = first_v_sub where first_v_sub is the index of the first iteration 
# with vtz > 0 (from the original simulation).

K = first_v_sub  # index of first v-TZ
print(f"\nFirst v-TZ at iteration {K}")
print(f"Iterations 0 through {K-1} have vtz=0 (pure u-TZ or combined)")
# Actually, iteration K-1 has vtz=0. Iteration K has vtz>0.
# But which iteration has the transition (first v-subtraction)?
# The v-subtraction in iteration K-1 or K?

# Let me check: u starts large, gets TZ'd, then u >= N (u-subtractions).
# The transition is when u < N after TZ.
# When does this happen?

# Let me just track when u first becomes < N, and when the first v-subtraction happens.

u_sim = denominator
v_sim = N
first_u_lt_N = None
first_v_sub_actual = None

for it in range(step):
    utz = 0
    while u_sim and (u_sim & 1) == 0:
        u_sim //= 2
        utz += 1
    vtz = 0
    while v_sim and (v_sim & 1) == 0:
        v_sim //= 2
        vtz += 1
    
    if u_sim < v_sim and first_u_lt_N is None:
        first_u_lt_N = it
    
    if u_sim >= v_sim:
        if u_sim == v_sim: break
        u_sim -= v_sim
    else:
        if first_v_sub_actual is None:
            first_v_sub_actual = it
            print(f"First v-subtraction at iteration {it}, u bits={u_sim.bit_length()} (after TZ)")
        v_sim -= u_sim

print(f"First u < N after TZ: iteration {first_u_lt_N}")
print(f"First v-subtraction: iteration {first_v_sub_actual}")

# So: K_pure_u, the number of PURE u-TZ runs = first_v_sub_actual (iterations before first v-subtraction)
# But at iteration first_v_sub_actual - 1: vtz = 0 (still pure), u >= N (u-subtraction)
# At iteration first_v_sub_actual: u < N after TZ (first v-subtraction)

# Wait no. At iteration first_v_sub_actual: before subtract, u < N after TZ.
# But TZ happened first: u was even, got TZ'd to odd. Then u_odd < N.
# Since u < N (and v = N): v -= u (v-subtraction).
# v = N - u_odd. v is now even.

# So at this iteration: u-TZ happened (pure, vtz=0), but subtraction is v -= u.
# In the NEXT iteration: v is even, v TZ happens (vtz > 0).

# So: first_v_sub_actual iterations have pure u-TZ (= first u-subtraction + transition)
# And first_v_sub_actual is the index of the first v-subtraction.

# At iteration first_v_sub_actual: vtz = 0 (pure u-TZ)
# At iteration first_v_sub_actual + 1: vtz > 0

# So K = first_v_sub_actual iterations have vtz = 0
# The first v-TZ is at iteration first_v_sub_actual + 1

# Let me verify: in the ORIGINAL simulation we had first_v_sub is the index of first v-TZ.
# And first_v_sub_actual is the index of first v-subtraction.

print(f"\nVerification:")
print(f"first_v_sub + 1 = {first_v_sub + 1}")
print(f"first_v_sub_actual = {first_v_sub_actual}")
# These should be related: first v-subtraction happens 1 iteration before first v-TZ
# Because: v-subtraction makes v even, then next iteration's TZ(v) > 0.

# So K_pure_utz = first_v_sub_actual (number of pure u-TZ runs)
# And K_pure_utz = first_v_sub (index of first v-TZ = K_pure_utz)

# WAIT. From the code: first_v_sub = step where vtz > 0 FIRST appears.
# This is AFTER the first v-subtraction.
# So first_v_sub > first_v_sub_actual.

# Let me look: is first_v_sub = first_v_sub_actual + 1?
print(f"first_v_sub = first_v_sub_actual + 1: {first_v_sub == first_v_sub_actual + 1}")

# If so: K_pure_utz = first_v_sub_actual = first_v_sub - 1
# But I computed earlier: "First v-TZ at step 132 (0-indexed)"
# So K = 131 or 132?

# Let me just re-run the original simulation to get K.

# In the FIRST simulation (the one that prints "First v-TZ at step..."):
# first_v_sub was set when vtz > 0 inside the while loop.
# This happens AFTER the v-subtraction. So it's the FIRST iteration where v is even.

# And in the re-simulation above:
# first_u_lt_N is when u_odd < N for the first time (before subtract).
# first_v_sub_actual is when v -= u for the first time.

# These should be related: first_v_sub_actual >= first_u_lt_N.
# Because in the transition iteration: before TZ, u is even. After TZ, u_odd < N.
# Then v -= u happens.

# And first_v_sub = first_v_sub_actual + 1 (the next iteration has v TZ).

print(f"\nSo: K_pure_utz = {first_v_sub_actual} (iterations 0 through {first_v_sub_actual-1}, {first_v_sub_actual} total)")
print(f"These {first_v_sub_actual} iterations have vtz = 0 and pure u-TZ")

# Let me count total TZ units in these K iterations
u_tz_sum = 0
for i in range(first_v_sub_actual):
    u_tz_sum += total_tz_counts[i]

print(f"Total TZ units in {first_v_sub_actual} pure u-TZ iterations: {u_tz_sum}")

# Now verify: x1_0 from these parity bits should equal a_mod
all_parities = x1_parity_u_tz[:u_tz_sum]  # first u_tz_sum u-TZ parity bits
print(f"Number of parity bits: {len(all_parities)}")

B = 0
for i, bit in enumerate(all_parities):
    B |= (bit << i)
x1_0 = (-N * B) % (1 << len(all_parities))
print(f"x1_0 from parity = {hex(x1_0)}")
print(f"x1_0 actual     = {hex(a_mod)}")
print(f"Match: {x1_0 == a_mod}")

if x1_0 == a_mod:
    print("\n*** x1_0 RECONSTRUCTION SUCCESSFUL! ***")
    print(f"K = {first_v_sub_actual}, total TZ units = {u_tz_sum}")
