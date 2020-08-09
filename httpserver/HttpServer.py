"""
    httpserver 主程序
"""

from socket import *
from threading import Thread
import re
import json

from config import *

ADDR = (HOST, PORT)


def connect_frame(env):
    """
        和 WebFrame 通信
    :param env: type dict
                key: method,info
    :return:
    """
    sock_fd = socket()
    try:
        sock_fd.connect((frame_ip, frame_port))
    except Exception as e:
        print(e)
        return

    request_msg = json.dumps(env)  # dict => Json
    sock_fd.send(request_msg.encode())

    response_msg = sock_fd.recv(4096 * 100).decode()
    return json.loads(response_msg)  # Json => dict


class HTTPServer:
    """
        核心代码
    """

    def __init__(self, address):
        self.address = address
        self.create_socket()
        self.bind()

    def create_socket(self):
        """
            创建套接字
        :return:
        """
        self.sock_fd = socket()
        self.sock_fd.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)  # 端口重用是否开启由配置文件决定

    def bind(self):
        """
            绑定地址
        :return:
        """
        self.sock_fd.bind(self.address)
        self.ip = self.address[0]
        self.port = self.address[1]

    def server_forever(self):
        """
            启动服务器
        :return:
        """
        self.sock_fd.listen(5)
        print("Listen the port %d ..." % self.port)
        while True:
            conn_fd, addr = self.sock_fd.accept()
            print("Connecnt from ...", addr)
            client = Thread(target=self.handle, args=(conn_fd,))
            client.setDaemon(True)
            client.start()

    def handle(self, conn_fd):
        request_msg = conn_fd.recv(1024).decode()
        print(request_msg)
        # 匹配请求头中的请求 类别 和 内容，
        #    并分别使用 method,info 两个捕获组，分组匹配
        pattern = r"(?P<method>[A-Z]+)\s+(?P<info>/\S*)"
        try:
            env = re.match(pattern, request_msg).groupdict()
        except:
            conn_fd.close()
            return
        else:
            data = connect_frame(env)
            if data:
                self.response(conn_fd, data)

    def response(self, conn_fd, data):
        """
            将数据整理为响应的格式发送给浏览器
        :param data: 应用响应的数据
        :return:
        """
        if data['status'] == '200':
            responseHeaders = "HTTP/1.1 200 OK\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data['data']
        elif data['status'] == '404':
            responseHeaders = "HTTP/1.1 404 Not Found\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data['data']
        elif data['status'] == '500':
            pass

        # 将数据发送给浏览器
        response_data = responseHeaders + responseBody
        conn_fd.send(response_data.encode())


if __name__ == '__main__':
    httpd = HTTPServer(ADDR)
    httpd.server_forever()
