from langchain_community.utilities import SearxSearchWrapper
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import HumanMessage

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

    # print(f"search results: {results}")
    '''
    search results: [{'Result': 'No good Search Result was found'}]
    search results: [{'snippet': '杭州主城区15天天气预报.萧山天气预报15天余杭天气预报15天富阳天气预报15天上城天气预报15天下城天气预报15天江干天气预报15天拱墅天气预报1...', 'title': '杭州天气预报15天_杭州天气预报15天查询,杭州未来15天天气预报- ...', 'link': 'https://www.tianqi.com/hangzhou/15/', 'engines': ['360search'], 'category': 'general'}, {'snippet': '2025年3月5日 - 杭州主城区30天天气预报.萧山天气预报30天余杭天气预报30天富阳天气预报30天上城天气预报30天下城天气预报30天江干天气预报30天拱墅天气预报30天西湖...', 'title': '杭州天气预报30天_杭州天气预报30天查询_杭州天气预报一个月_...', 'link': 'https://www.tianqi.com/hangzhou/30/', 'engines': ['360search'], 'category': 'general'}]
    '''

    if results and results[0]['Result'] == 'No good Search Result was found':
        return "未找到合适的搜索结果"
    elif results and 'snippet' in results[0]:
        return results
    else:
        return "未知的结果类型"


if __name__ == "__main__":
    query = "查询失败的返回结果是什么"
    results = searxng_search(query)

    # print(type(results))

    # for result in results:
    #     print(f"Snippet: {result['snippet']}")
    #     print(f"Title: {result['title']}")
    #     print(f"Link: {result['link']}")
    #     print(f"Source: {result['engines']}")
    #     print("------------------------------")
    
    # prompt_template = PromptTemplate(
    #     input_variables=["snippet1", "title1", "snippet2", "title2", "snippet3", "title3"],
    #     template="""
    #     请结合检索到的三个相关度最高的网页内容生成合适的回复：
    #     第一个网页摘要：{snippet1}
    #     第一个网页标题：{title1}

    #     第二个网页摘要：{snippet2}
    #     第二个网页标题：{title2}

    #     第三个网页摘要：{snippet3}
    #     第三个网页标题：{title3}
    #     """
    # )

    # # TODO：补充本地模型调用方式
    # chat_llm = ChatOpenAI(
    #     model_name="gpt-4",
    #     temperature=0.7,
    #     max_tokens=200
    #     )

    # chain = LLMChain(
    #     llm=chat_llm,
    #     prompt=prompt_template
    #     )
    
    # result = chain.run(
    #     snippet1="results[0]['snippet']",
    #     link1="results[0]['title']"
    #     snippet2="results[1]['snippet']",
    #     link2="results[1]['title']",
    #     snippet3="results[2]['snippet']",
    #     link3="results[2]['title']"
    #     )
    
    # print(result)
