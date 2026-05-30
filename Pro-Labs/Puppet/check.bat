@echo off
echo === PointAndPrint Registry ===
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Printers\PointAndPrint" 2>nul || echo KEY NOT FOUND
echo.
echo === Spooler Status ===
sc query Spooler | findstr STATE
echo.
echo === Current User ===
whoami
echo.
echo === Privileges ===
whoami /priv
echo.
echo === Admins ===
net localgroup Administrators
