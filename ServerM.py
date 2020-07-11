# from operator import itemgetter
import asyncio


class ClientServerProtocol(asyncio.Protocol):

    def __init__(self):
        super(ClientServerProtocol, self).__init__()
        self.transport = None
        self.answer = None

    # This method is called when connecting from the side
    # of another system and contains the transport object
    def connection_made(self, transport):
        print('Connection from {}'.format(transport.get_extra_info('peername')))
        self.transport = transport

    # This method is called when the system is connected sends its data.
    # The data argument contains received information in bytes
    # The method also sends the server response
    def data_received(self, data):
        # Forming the server response depending on the input data
        self.interpret_data(data.decode("utf-8"))
        # Sending the server response
        self.transport.write(self.answer.encode("utf-8"))

    # Method that generates the server response
    # It also refers to the getters and setters of the main dictionary
    def interpret_data(self, command_text):
        self.answer = ""
        # Select a command from the line
        command_list = command_text.strip().split(' ')
        command_word = command_list[0]

        # Selecting an action depending on the command
        # At the same time, we form the text of the server response
        if command_word == "get" and len(command_list) == 2:
            self.answer = self.make_get_data(command_list[1])
        elif command_word == "put" and len(command_list) == 4:
            self.answer = self.make_put_data(
                command_list[1], command_list[2], command_list[3])
        else:
            self.answer = 'error\nwrong command\n\n'

    @staticmethod
    def make_get_data(metric_name):
        text_answer = "ok\n"
        if metric_name == "*":
            for metric_name, time_keys in main_server_data.items():
                for time in time_keys:
                    text_answer += f"{metric_name} {main_server_data[metric_name][time]} {time}\n"
        elif metric_name in main_server_data:
            for time in main_server_data[metric_name]:
                text_answer += f'{metric_name} {main_server_data[metric_name][time]} {time}\n'
        return text_answer + '\n'

    @staticmethod
    def make_put_data(metric_name, metric_value, timestamp):
        answer_text = "ok\n\n"
        if not metric_name in main_server_data:
            main_server_data[metric_name] = dict()
        try:
            main_server_data[metric_name][int(timestamp)] = float(metric_value)
        except ValueError:
            answer_text = 'error\nwrong command\n\n'
        # main_server_data[metric_name].sort(key=itemgetter(0))
        return answer_text


# the main function that starts and supports the server
def run_server(host, port):
    """Server startup function"""
    loop = asyncio.get_event_loop()
    server_coroutine = loop.create_server(ClientServerProtocol, host, port)
    server = loop.run_until_complete(server_coroutine)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stop from user")
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


main_server_data = dict()
if __name__ == "__main__":
    # Launch our server for the test
    run_server("127.0.0.1", 8888)
