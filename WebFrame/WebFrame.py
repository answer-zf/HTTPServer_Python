"""
    后端应用（框架）程序
"""

from select import select
from socket import *
import json

from settings import *  # 配置模块
from urls import *  # 路由模块

frame_address = (frame_ip, frame_port)


class Application:
    def __init__(self):
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
        self.sock_fd.bind(frame_address)

    def start(self):
        """
            启动服务
        :return:
        """
        self.sock_fd.listen(5)
        print("Listen the port %d" % frame_port)

        rlist = [self.sock_fd]
        wlist = []
        xlist = []

        # IO 多路复用监听请求
        while True:
            rs, ws, xs = select(rlist, wlist, xlist)
            for r in rs:
                if r is self.sock_fd:
                    conn_fd, addr = r.accept()
                    rlist.append(conn_fd)
                else:
                    self.handle(r)
                    rlist.remove(r)

    def handle(self, conn_fd):
        """
            处理 httpserver 请求并响应
        :param conn_fd: 连接套接字
        :return:
        """
        request_msg = conn_fd.recv(1024).decode()
        request_msg = json.loads(request_msg)

        if request_msg['method'] == "GET":
            if request_msg['info'] == "/" or request_msg['info'][-5:] == ".html":
                response_msg = self.get_html(request_msg['info'])
            else:
                response_msg = self.get_data(request_msg['info'])
        elif request_msg['method'] == "POST":
            pass

        # 将数据发送给 httpserver
        response_msg = json.dumps(response_msg)
        conn_fd.send(response_msg.encode())
        conn_fd.close()

    def get_html(self, info):
        """
            处理静态页面
        :param info: 请求内容
        :return:
        """
        if info == "/":
            filename = STATIC_DIR + "/index.html"
        else:
            filename = STATIC_DIR + info

        try:
            fd = open(filename)
        except Exception as e:
            f = open(STATIC_DIR + "/404.html")
            return {'status': '404', 'data': f.read()}
        else:
            return {'status': '200', 'data': fd.read()}

    def get_data(self, info):
        """
            处理数据请求
        :param info: 请求内容
        :return:
        """
        for url, func in urls:
            if url == info:
                return {'status': '200', 'data': func()}
        return {'status': '404', 'data': 'Fail ..........'}


if __name__ == '__main__':
    app = Application()
    app.start()
