from flask import Flask, request, jsonify, render_template
import socket
import threading
import re
import base64


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

    if command=='' or command==None:
        return jsonify(''), 200
    elif command and client_address:
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
            response = response.replace('&', '&amp;') \
                                .replace('<', '&lt;') \
                                .replace('>', '&gt;') \
                                .replace('"', '&quot;') \
                                .replace("'", '&#39;')
            return jsonify({'response': response}), 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return jsonify({'error': '指定客户端未连接'}), 400
    else:
        return jsonify({'error': '命令或客户端未提供'}), 400


@app.route('/screenshot', methods=['GET'])
def screenshot():
    client_address = request.args.get("client")  # 获取客户端地址
    if client_address:
        try:
            client_address_tuple = tuple(eval(client_address))
        except Exception as e:
            return jsonify({'error': f'地址解析错误: {str(e)}'}), 400

        with clients_lock:
            client_socket = clients.get(client_address_tuple)
        if client_socket:
            print(f"对 {client_address} 发送截图请求")
            try:
                client_socket.send(b'screenshot')  # 发送截图请求
            except Exception as e:
                return jsonify({'error': f'截图请求发送失败: {str(e)}'}), 500

            # 使用一个列表来收集所有接收到的数据片段
            image_data = b''  # 初始化数据接收变量
            while True:
                # 每次接收40960字节的数据
                response = client_socket.recv(40960)
                print(f"接收到 {len(response)} 字节数据")

                if len(response) < 40960:  # 当接收到的数据小于40960字节时，说明接收完成
                    print(f"对 {client_address} 截图接收完成")
                    image_data += response  # 将接收到的数据片段合并
                    # 将接收到的图像数据编码为 Base64
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    print(image_base64)
                    return jsonify({'message': '截图成功', 'image_data': image_base64}), 200
                elif not response:  # 当返回空字节串时，说明没有数据接收 等待下一次接收
                    break

                image_data += response  # 将接收到的数据片段合并

        else:
            return jsonify({'error': '指定客户端未连接'}), 400
    else:
        return jsonify({'error': '客户端未提供'}), 400
















if __name__ == "__main__":
    threading.Thread(target=accept_client, daemon=True).start()
    app.run(host='0.0.0.0', port=8780)