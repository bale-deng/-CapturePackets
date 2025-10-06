# -*- coding: utf-8 -*-
"""
一个功能完整的命令行HTTP接口测试工具 (v3 - 支持详细模式)
作者: Bale
"""
import requests
import argparse
import json
import sys


def make_request(method,
                 url,
                 headers=None,
                 data=None,
                 json_data=None,
                 verbose=False):
    """
    发送HTTP请求并打印详细的请求和响应信息。
    
    :param verbose: 如果为True，则打印出完整的请求细节。
    """
    # ------------------------------------------------------------------
    # 1. 如果开启了详细模式，打印出完整的“发送请求”信息
    # ------------------------------------------------------------------
    if verbose:
        print("---------- 🚀 发送请求 (Outgoing Request) ----------\n")
        print(f"> {method.upper()} {url} HTTP/1.1")

        # 准备要打印的头信息，包括用户自定义的和即将自动生成的
        final_headers = headers.copy() if headers else {}
        if json_data:
            final_headers['Content-Type'] = 'application/json'

        print("> Headers:")
        for key, value in final_headers.items():
            print(f">   {key}: {value}")

        # 打印消息体
        if data:
            print("\n> Body (Form Data/Raw Text):")
            print(data)
        elif json_data:
            print("\n> Body (JSON):")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))

        print("\n------------------------------------------------------\n")
    else:
        print(f"🚀 正在发送 {method.upper()} 请求到: {url} ...")

    # ------------------------------------------------------------------
    # 2. 执行实际的HTTP请求
    # ------------------------------------------------------------------
    try:
        response = requests.request(method=method,
                                    url=url,
                                    headers=headers,
                                    data=data,
                                    json=json_data,
                                    timeout=10)
        response.raise_for_status()  # 检查HTTP错误状态码

        # ------------------------------------------------------------------
        # 3. 打印“得到响应”信息
        # ------------------------------------------------------------------
        print("---------- ✅ 得到响应 (Server Response) ----------\n")

        print(
            f"🔗 状态: HTTP/{response.raw.version / 10.0} {response.status_code} {response.reason}"
        )

        print("\n📋 响应头 (Headers):")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print("\n📦 响应体 (Body):")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            # 如果不是JSON，则安全地打印文本
            if response.text:
                print(response.text)
            else:
                print("(无响应体)")

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if e.response:
            print(f"   响应内容: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败，请检查URL或网络连接: {e}")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="一个功能完整的命令行HTTP接口测试工具。",
        formatter_class=argparse.RawTextHelpFormatter  # 保持帮助信息格式
    )

    parser.add_argument("method", help="HTTP请求方法, 例如: GET, POST, PUT, DELETE。")
    parser.add_argument("url", help="请求的目标URL。")

    parser.add_argument("-H",
                        "--header",
                        action="append",
                        help="请求头, 格式为 'Key:Value'。\n可以多次使用以添加多个头。")

    body_group = parser.add_mutually_exclusive_group()
    body_group.add_argument("-d",
                            "--data",
                            help="要发送的表单数据 (例如 'key1=value1&key2=value2')。")
    body_group.add_argument("-j",
                            "--json_data",
                            help="要发送的JSON格式的字符串 (例如 '{\"key\": \"value\"}')。")
    body_group.add_argument("-f",
                            "--file",
                            help="包含JSON请求体的文件路径 (例如 data.json)。")

    # --- 新增详细模式开关 ---
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",  # 当出现-v时，这个参数的值为True
        help="详细模式，打印出完整的请求信息。")

    args = parser.parse_args()

    headers = {}
    if args.header:
        for header in args.header:
            try:
                key, value = header.split(":", 1)
                headers[key.strip()] = value.strip()
            except ValueError:
                print(f"⚠️ 无效的头格式: '{header}'。已忽略。")

    json_body = None
    raw_body = args.data

    if args.json_data:
        try:
            json_body = json.loads(args.json_data)
        except json.JSONDecodeError:
            print("❌ 错误: --json_data 提供的内容不是有效的JSON格式。")
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                json_body = json.load(f)
        except FileNotFoundError:
            print(f"❌ 错误: 文件未找到 '{args.file}'。")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ 错误: 文件 '{args.file}' 的内容不是有效的JSON格式。")
            sys.exit(1)

    make_request(args.method,
                 args.url,
                 headers,
                 raw_body,
                 json_body,
                 verbose=args.verbose)


if __name__ == "__main__":
    main()
