from langchain_community.utilities import SearxSearchWrapper
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import HumanMessage
import requests
import json

def searxng_search(query):
    search = SearxSearchWrapper(searx_host="http://localhost:9003/")
    results = search.results(
        query,                                  # 搜索内容
        language="zh-CN",                       # 语言
        safesearch=2,                           # 可选0(不过滤任何结果),1(中等级别内容过滤),2(严格级别内容过滤)
        categories="general",                   # 搜索内容，取值general/images/videos等
        engines=["baidu", "360search", "bing", "sougo", "bing_news"],    # 搜索引擎
        num_results=5                          # 返回内容数
    )

    # TODO:如果没检索到结果记得返回内容
    # print(f"search results: {results}")

    return results
    

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
        "max_tokens": 2048,
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
    query = "成年人自学乐器，钢琴和吉他哪个更省钱？"
    results = searxng_search(query)

    # print(type(results))

    for result in results:
        print(f"Snippet: {result['snippet']}")
        print(f"Title: {result['title']}")
        print(f"Link: {result['link']}")
        print(f"Source: {result['engines']}")
        print("------------------------------")
    
    template="""
        第一个网页摘要：{snippet1}
        第一个网页标题：{title1}

        第二个网页摘要：{snippet2}
        第二个网页标题：{title2}

        第三个网页摘要：{snippet3}
        第三个网页标题：{title3}
        请结合检索到的三个相关度最高的网页内容，以简洁的语言回答这个问题：{query}。
        """

    new_query = template.format(
        snippet1="results[0]['snippet']",
        title1="results[0]['title']",
        snippet2="results[1]['snippet']",
        title2="results[1]['title']",
        snippet3="results[2]['snippet']",
        title3="results[2]['title']",
        query=query
    )
    model_inference(new_query)
    print(f"\n参考网址如下：\n{results[0]['link']}\n{results[1]['link']}\n{results[2]['link']}\n")
