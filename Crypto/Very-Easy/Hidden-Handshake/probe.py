import socket

HOST = "154.57.164.65"
PORT = 30647

def get_encrypted(pass2: str, user: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((HOST, PORT))

    data = b""
    while b"secure access key:" not in data:
        data += s.recv(4096)

    s.sendall(pass2.encode() + b"\n")

    while b"Agent Codename:" not in data:
        data += s.recv(4096)

    s.sendall(user.encode() + b"\n")

    result = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            result += chunk
        except socket.timeout:
            break

    s.close()
    return result.decode(errors="replace")

if __name__ == "__main__":
    result = get_encrypted("aaaaaaaa", "TestUser")
    print(result)
