from flask import Flask, request, jsonify, render_template
import socket
import threading
import re


app = Flask(__name__)

# 存储与本地电脑的连接: 使用字典来维护多个客户端
clients = {}
clients_lock = threading.Lock()  # 用于线程安全地操作客户端

def accept_client():
    server_ip = '0.0.0.0'
    server_port = 2222

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(55)  # 允许多个连接
    print(f"等待本地电脑连接...")

    while True:
        client_socket, addr = server.accept()
        with clients_lock:
            clients[addr] = client_socket  # 存储客户端连接
        print(f"本地电脑 {addr} 已连接!")

# 获取连接的客户端列表
@app.route('/clients', methods=['GET'])
def list_clients():
    with clients_lock:
        active_clients = list(clients.keys())
    return jsonify({'clients': active_clients}), 200

@app.route('/')
def index():
    return render_template('index.html')  # 返回 HTML 页面

@app.route('/execute', methods=['GET'])
def execute_command():
    client_address = request.args.get("client")  # 获取客户端地址
    command = request.args.get("command")  # 获取命令

    if command and client_address:
        # 简单处理，将字符串地址分割并转换为元组形式 (IP, PORT)
        try:
            client_address_tuple = tuple(eval(client_address))
        except Exception as e:
            return jsonify({'error': f'地址解析错误: {str(e)}'}), 400

        with clients_lock:
            client_socket = clients.get(client_address_tuple)  # 获取指定客户端的 socket
        if client_socket:
            print(f"对 {client_address} 发送命令: {command}")
            client_socket.send(command.encode())
            response = client_socket.recv(4096).decode('utf-8')  # 确保以 UTF-8 解码
            response = response.replace('\n', '<br>')
            return jsonify({'response': response}), 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return jsonify({'error': '指定客户端未连接'}), 400
    else:
        return jsonify({'error': '命令或客户端未提供'}), 400


if __name__ == "__main__":
    threading.Thread(target=accept_client, daemon=True).start()

    app.run(host='0.0.0.0', port=8780)