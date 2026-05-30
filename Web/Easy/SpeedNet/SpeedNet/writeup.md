# SpeedNet

## Status: Unsolved

## Target
- URL: `http://154.57.164.68:30227`
- Stack: nginx/1.28.0, Vite+React SPA, Express GraphQL backend
- Endpoints: `/graphql` (GraphQL), `/emails/` (email inbox)

## Recon
- GraphQL introspection revealed 8 mutations and 4 queries
- Frontend JS bundle extracted and analyzed

### GraphQL Schema
- **Queries**: `userProfile(userId: Int!)`, `currentInvoice`, `invoiceHistory(limit: Int)`, `dataUsageStats(days: Int)`
- **Mutations**: `register`, `login`, `updateProfile`, `forgotPassword`, `devForgotPassword`, `resetPassword`, `verifyTwoFactor`, `resendOTP`

## Attack Chain Attempted

### 1. devForgotPassword → Password Reset
- `devForgotPassword(email: "admin@speednet.htb")` returns the reset token directly (debug endpoint)
- Used it to reset admin's password to `Hacked123!`
- Login with admin credentials works but triggers 2FA challenge:
  ```
  {"errors":[{"message":"2FA_REQUIRED:<uuid>", ...}]}
  ```

### 2. NoSQL/SQL Injection
- Tried injection in `login` email/password fields, `userProfile` userId — all blocked with proper validation

### 3. JWT Manipulation
- Algorithm "none" attack: rejected
- Modified payload with different userId: "Not authenticated"
- No "Bearer" prefix needed — raw JWT is accepted
- Signature cannot be forged without the secret

### 4. Mass Assignment
- Extra fields in `login`, `createUser`, `updateProfile` variables — silently ignored
- `twoFactorAuthEnabled` can only be toggled via `updateProfile` (requires auth)

### 5. IDOR
- `userProfile(userId: 1)` works without auth — can read admin's full profile (including `twoFactorAuthEnabled: true`)
- `currentInvoice` and `invoiceHistory` don't accept userId parameter — only return current user's data
- Auth required for billing/invoice queries

### 6. 2FA OTP Brute Force
- OTP is a 4-digit numeric code sent to user's registered email
- Email inbox at `/emails/?email=X` captures emails sent TO that address
- Admin's OTP goes to `admin@speednet.htb` — not accessible
- Tested OTP brute force from 0-99999 using both individual and batch GraphQL requests
- Writeup reference (sahandbabali/Hack-The-Box---SpeedNet) confirms brute-force approach with range 1000-999999
- **90k+ OTPs tested — none found**

### 7. GraphQL Batching
- Server partially supports array-of-mutations batching
- Named operations with `variables` parameter works better but unreliable
- No rate limiting detected on `verifyTwoFactor`
- Server returns empty/null responses for some batches

## Why Failed
- Admin's 2FA OTP cannot be intercepted (no access to admin@speednet.htb inbox)
- Brute force over 90k values found nothing — OTP may not be generated for admin in this instance
- No alternative path found: no hidden GraphQL fields, no SSTI, no SSRF, no file read
- Challenge may have a different intended solution path on this specific instance
- The 2FA brute-force approach from public writeups may require a PAT or other context not available

## Lessons Learned
- `devForgotPassword` leaks reset tokens — powerful for password resets but doesn't bypass 2FA
- Email inbox only captures emails TO the configured address, not FROM
- GraphQL batching can be used for brute force but has reliability issues
- No rate limiting ≠ viable brute force — range may be too large to exhaust before token expiry
