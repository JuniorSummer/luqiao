import requests
import json

'''
根据curl调用方式改写：
curl -X POST 
-H "Content-Type: application/json" 
-d '{"model":"deepseekr1",
    "messages":[{"role":"system","content":"介绍一下杭州 的几个景点，我想去玩。"}],
    "max_tokens":2000,
    "stream":true}' 
http://125.122.39.104:1025/v1/chat/completions
'''

def model_inference(query):
    # 请求的 URL
    url = 'http://125.122.39.104:1025/v1/chat/completions'

    # 请求头
    headers = {
        'Content-Type': 'application/json'
    }

    # 请求体
    data = {
        "model": "deepseekr1",
        "messages": [{"role": "system", "content": query}],
        "max_tokens": 512,
        "stream": True
    }

    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        # 检查响应状态码
        response.raise_for_status()
        full_response = ""

        # 处理流式响应
        for line in response.iter_lines():
            if line:
                # 转码编译
                line = line.decode('utf-8')
                # 过滤掉以 'data: ' 开头的前缀
                if line.startswith('data: '):
                    line = line[6:]
                if line == "[DONE]":
                    return
                try:
                    # 解析 JSON 数据，形成流式输出
                    json_data = json.loads(line)
                    content = json_data['choices'][0]['delta']['content']
                    full_response += content
                    print(content, end="", flush=True)
                except json.JSONDecodeError:
                    print(f"无法解析为 JSON: {line}")
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP 错误发生: {http_err}')
    except requests.exceptions.RequestException as req_err:
        print(f'请求错误发生: {req_err}')


if __name__ == "__main__":
    query = "介绍一下杭州的几个景点，我想去玩。"
    model_inference(query)
