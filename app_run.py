from langchain_community.utilities import SearxSearchWrapper
from langchain import PromptTemplate
import json
import subprocess
import time
from fastapi import FastAPI, Body
import uvicorn
from fastapi.responses import StreamingResponse
import aiohttp
from pydantic import BaseModel


def start_searxng_service():
    try:
        searxng_dir = "/root/searxng"
        process = subprocess.Popen(['python', 'searx/webapp.py'], cwd=searxng_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(10)
        return process
    except Exception as e:
        print(f"启动searxng服务时出错: {e}")
        return None


def searxng_search(query):
    search = SearxSearchWrapper(searx_host="http://localhost:9003/")
    results = search.results(
        query,
        language="zh-CN",
        safesearch=2,
        categories="general",
        engines=["baidu", "360search", "bing", "sougo", "bing_news"],
        num_results=5
    )
    if isinstance(results, list) and results:
        first_result = results[0]
        if isinstance(first_result, dict) and 'Result' in first_result and first_result['Result'] == 'No good Search Result was found':
            return "未找到合适的搜索结果"
        elif isinstance(first_result, dict) and 'snippet' in first_result:
            return results
    return "未知的结果类型"


async def model_inference(query):
    url = 'http://125.122.39.104:1025/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "model": "deepseekr1",
        "messages": [{"role": "system", "content": query}],
        "max_tokens": 2048,
        "stream": True
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()
            async for line in response.content.iter_any():
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        line = line[6:]
                    if line == "[DONE]":
                        break
                    try:
                        json_data = json.loads(line)
                        content = json_data['choices'][0]['delta'].get('content', '')
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        print(f"无法解析为JSON: {line}")


async def main(query):
    searxng_process = start_searxng_service()
    if searxng_process:
        try:
            results = searxng_search(query)
            if results == "未找到合适的搜索结果" or results == "未知的结果类型":
                yield "未找到合适的搜索结果，请换个说法再试\n"
            else:
                yield "已搜索到相关链接，答案生成中\n"
                template = """
                    第一个网页摘要：{snippet1}
                    第一个网页标题：{title1}
                    第二个网页摘要：{snippet2}
                    第二个网页标题：{title2}
                    第三个网页摘要：{snippet3}
                    第三个网页标题：{title3}
                    请结合检索到的三个相关度最高的网页内容，以简洁的语言回答这个问题：{query}。
                    """
                new_query = template.format(
                    snippet1=results[0]['snippet'],
                    title1=results[0]['title'],
                    snippet2=results[1]['snippet'],
                    title2=results[1]['title'],
                    snippet3=results[2]['snippet'],
                    title3=results[2]['title'],
                    query=query
                )
                async for chunk in model_inference(new_query):
                    print(chunk)
                    yield chunk
                # print(f"\n\n参考网址如下：\n{results[0]['link']}\n{results[1]['link']}\n{results[2]['link']}\n")
                yield f"\n\n参考网址如下：\n{results[0]['link']}\n{results[1]['link']}\n{results[2]['link']}\n"
        except Exception as e:
            yield f"主程序出错: {e}"
        finally:
            searxng_process.terminate()


app = FastAPI()

class QueryRequest(BaseModel):
    query: str

# 修改为POST请求
@app.post("/run_internet_search")
async def run_internet_search(request: QueryRequest):
    return StreamingResponse(main(request.query))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1927)
