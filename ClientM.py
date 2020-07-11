import socket
import time
import bisect


class ClientError(Exception):
    """User exception if method "put" not work"""
    print("The method didn't work")


class Client:
    def __init__(self, host_ip, port_input, timeout=None):
        """Create local variables and establish a connection"""
        self._host = host_ip
        self._port = port_input
        self._timeout = timeout
        # Try establish a connection
        try:
            self.socket = socket.create_connection((self._host, self._port), self._timeout)
        except socket.error as err_text:
            print("Error create connection - socket not been create", err_text)

    def put(self, metric_name, metric_value, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        try:
            self.socket.sendall(
                f"put {metric_name} {metric_value} {timestamp}\n".encode("utf8"))
        except socket.error as err_text:
            raise ClientError("Error send data on \"put\" method.", err_text)

        self.listening_server_response()

    def get(self, metric_name):
        try:
            self.socket.sendall(f"get {metric_name}\n".encode("utf8"))
        except socket.error as err_text:
            raise ClientError("Error send data on \"get\" method.")
        answer = self.listening_server_response()
        data = {}
        if answer != '':
            for row in answer.split("\n"):
                try:
                    key, value, timestamp = row.split()
                except ValueError as err_text:
                    raise ClientError("Error unpack values", err_text)
                if key not in data:
                    data[key] = []
                bisect.insort(data[key], (int(timestamp), float(value)))
        return data

    def close(self):
        print("The connection will be broken")
        try:
            self.socket.close()
            print("Disconnected")
        except socket.error as err_text:
            raise ClientError("Error close connection", err_text)

    def listening_server_response(self):
        """ Method for read server answer """

        input_data = b""
        while not input_data.endswith(b"\n\n"):
            input_data += self.socket.recv(1024)
        status_answer, data_answer = input_data.decode("utf8").split("\n", 1)
        data_answer = data_answer.strip()
        if status_answer == "error":
            raise ClientError(data_answer)
        return data_answer

if __name__ == "__main__":
    client = Client("127.0.0.1", 8888, timeout=15)
    client.put("palm.cpu", 0.5, timestamp=1150864247)
    client.put("palm.cpu", 2.0, timestamp=1150864248)
    client.put("palm.cpu", 0.5, timestamp=1150864248)
    client.put("eardrum.cpu", 3, timestamp=1150864250)
    client.put("eardrum.cpu", 4, timestamp=1150864251)
    client.put("eardrum.memory", 4200000)

    print(client.get("*"))
    client.close()