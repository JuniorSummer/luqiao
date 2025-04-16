import json
from fastapi import FastAPI, HTTPException, Body
import uvicorn
import requests
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="题目生成接口")

# 定义请求参数模型
class QuestionRequest(BaseModel):
    single_choice_num: int
    yes_no_question_num: int

# TODO:切换为星海智文接口，获取知识库中的需要出题的内容
def get_knowledge_base():
    content = ["砂轮磨损机床自动停机，员工到机床前按冷却启停，循环启停。打开机床门，左手用固定扳手套住砂轮螺帽，右手用扳手拧开放下扳手，然后拧开并取出就砂轮。套上新砂轮，先用手拧上新换的砂轮螺帽，左手扶住砂轮螺帽，右手用扳手拧紧砂轮轴。关闭机床门依次按工作启停，冷却启停砂轮启停旋钮到长修，最后按循环启动。","今天来学习下成品检验和包装称重的内容。员工用双手食指各串起数个产品，置于身前拇指滑动产品外壁，使得产品在手指上旋转双眼，观察产品外壁是否不良？然后左手依次将串在右手的产品取出，同时观察产品的外壁和正反2面，是否存在不良再置产品于探照灯下双眼直视屏幕。同时，双手翻转产品，2次观察产品两面，并将合格品放在传送带上。关于不良的种类，判别检验台墙壁、贴纸上都有介绍，不了解的新员工都可以去看一下。重复检验动作至检验台产品基本检验干净。接下来讲解一下包装的主要注意事项，员工将已经检验好的包装台上的产品，用手指穿好，然后放齐有序地倾放在套有塑料包装袋的纸箱内重复放置产品动作，直至包装箱内产品放满。放满后将塑料袋口平铺盖好，然后盖上包装料箱，移动包装料箱至标准称重量称上。我们可以看到量称上得到产品质量的读数。读数界面上有3个读数，分别是产品重量、规定重量上限和规定重量下限。当黄灯亮起时，说明包装重量少，需要寻找哪里装漏了。当红灯亮起时，说明包装重量多，需要寻找哪里多装了。当绿灯亮起时，说明包装重量合适。很明显，现在产品重量是不符合其上下限标准的，黄灯也同时亮起。然后我们需要看一下是否包装放料的时候，哪个地方有空缺，我们需要找到空缺的地方，并放入遗漏的产品，然后重新观察一下，量称上的读数是否与该产品单箱的标准读数一致。此时我们看到显示的读数是在标准读数上下限之间的同时，亮称上绿灯亮起读数无误后，将产品包装箱自口密封。最后放入成品托盘上。"]
    return content

# TODO:切换为星海智文接口
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
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8').strip()
                
                # 不对数据进行解析
                yield line
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP 错误发生: {http_err}')
    except requests.exceptions.RequestException as req_err:
        print(f'请求错误发生: {req_err}')


def generate_question(single_choice_num, yes_no_question_num):
    _knowledge_base = get_knowledge_base()
    knowledge_base = ""
    for k in _knowledge_base:
        knowledge_base = k + '\n'
    
    template_1 = """
                请根据以下知识库内容{knowledge}，按照要求生成题目：

                ### 任务要求
                1. **题型**：包含单选题（{num_1}道）和判断题（{num_2}道），混合排列
                2. **题目内容**：从知识库中提取关键知识点作为题目核心，选项需紧密围绕知识点设计
               """
    template_2 = """
                3. **格式要求**（每个题目独立区块）：
                ```json
                {
                    "questions": {
                    {
                        "type": "单选题",        // 题型（单选题/判断题）
                        "question": "题干内容", // 包含具体知识点的问题描述
                        "options": ["A选项", "B选项", "C选项", "D选项"], // 单选题4个选项，判断题为["正确", "错误"]
                        "answer": "A"           // 正确答案（单选题为A/B/C/D，判断题为"正确"/"错误"）
                    },
                    // 其他题目按此格式依次排列
                    }
                }

                #### 示例数据
                ```json
                {
                "questions": {
                    {
                    "type": "单选题",
                    "question": "以下哪个是合法的Python变量名？",
                    "options": ["123var", "var-123", "var_123", "var@123"],
                    "answer": "C"
                    },
                    {
                    "type": "判断题",
                    "question": "布尔值True和False首字母必须大写",
                    "options": ["正确", "错误"],
                    "answer": "正确"
                    }
                }
                }

                4. **选项设计**：
                - 单选题干扰项需与正确选项有概念关联但存在本质区别
                - 判断题题干需直接对应知识库中的明确描述，避免模糊表述

                ### 输出规范
                - 每个题目之间用3个以上空行分隔
                - 严格按照给定格式输出，不得添加额外说明或格式符号
                - 答案需准确对应知识库内容，确保无事实性错误

                请开始生成题目：
                """
    query = template_1.format(
        knowledge = knowledge_base,
        num_1 = single_choice_num,
        num_2 = yes_no_question_num
    )
    query = query + '\n' + template_2
    full_response = ""
    for line in model_inference(query):
        # 对数据进行解析
        if line.startswith('data: '):
            line = line[6:]
        if line == "[DONE]":
            break
        try:
            json_data = json.loads(line)
            content = json_data['choices'][0]['delta'].get('content', '')
            full_response += content
            print(content, end="", flush=True)
        except json.JSONDecodeError:
            print(f"无法解析为JSON: {line}")
        # yield f"{line}\n"
    return full_response

def question_parse(output: str) -> Dict[str, Any]:
    """解析模型输出为结构化数据"""
    try:
        # 定位JSON代码块
        json_start = output.find("```json")
        json_end = output.find("```", json_start + 6)
        if json_start == -1 or json_end == -1:
            raise ValueError("未找到有效的JSON代码块")

        # 提取并解析JSON
        json_content = output[json_start+7:json_end].strip()
        return json.loads(json_content)
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON解析失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解析异常: {str(e)}"
        )

@app.post("/generate")
async def generate_questions(params: QuestionRequest = Body(...)):
    """题目生成主接口"""
    try:
        # 生成原始响应
        raw_output = generate_question(
            single_choice_num=params.single_choice_num,
            yes_no_question_num=params.yes_no_question_num
        )
        
        # 解析结构化数据
        parsed_data = question_parse(raw_output)
        
        return {
            "status": "success",
            "data": parsed_data,
            "count": len(parsed_data.get("questions", []))
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"题目生成失败: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1928)
