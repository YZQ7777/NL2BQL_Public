from All_Template import security_check_template, retrieve_database_info_template, BQL_generate_template
import time
from gradio_client import Client
from tqdm import tqdm  # 进度条库
import pandas as pd
import json
import gradio as gr
import re
import os

# 提示：若想更换为海岳大模型API，清更改client和get_response函数的对应参数。
from openai import OpenAI
client = OpenAI(
    api_key = "efef5db460e5d0c37bbcd56de6dfe6f8.lSa0YIVRpHRnEIuk",
    base_url = "https://open.bigmodel.cn/api/paas/v4/",
)

# 类似openai调用智谱大模型
def get_response(query, model="GLM-4-Plus"):
    """
    阻塞式单线程函数:输入一个question,返回一个回答
    """
    while True:
        try:
            # 调用模型获取回应
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": query}],
            )
            # 如果没有异常，返回正常的响应内容
            return completion.choices[0].message.content
        except Exception as e:
            # 如果发生异常，输出错误信息并等待一段时间后继续重试
            print(f"Error occurred: {e}. Retrying in 1 seconds...")
            time.sleep(1)

# 调用huggingface的Qwen2.5-7B模型
def get_response_Qwen(query, radio="7B", system_prompt="You are Qwen, created by Alibaba Cloud. You are a helpful assistant."):
    """
    调用API获取响应，使用指定的radio和system_prompt，并添加重试机制。
    
    参数:
    - query: 用户输入的查询内容
    - radio: 指定的radio选项，默认值为"7B"
    - system_prompt: 指定的system提示，默认值为"You are Qwen, created by Alibaba Cloud. You are a helpful assistant."

    返回:
    - 成功时返回API的响应文本结果
    """
    
    # 使用循环实现重试机制
    while True:
        try:
            # 创建客户端
            client = Client("Qwen/Qwen2.5")

            # 调用 predict 方法获取结果
            result = client.predict(
                query=query,
                history=[],
                system=system_prompt,
                radio=radio,
                api_name="/model_chat"
            )
            return result[1][0][1]['text']  # 成功时返回结果
            
        except Exception as e:
            print(f"请求失败，错误信息：{e}")
            print("1秒后重试...")
            time.sleep(1)

def security_check(user_input):
    """
    执行安全检查，将自然语言输入交由大模型评估是否符合安全标准。
    
    参数:
    - user_input: 用户输入的自然语言查询描述

    返回:
    - 若安全检查通过，返回 ("True;响应结果")。
    - 若未通过，返回 ("False;拒绝原因")。
    """

    query = security_check_template.format(user_input)

    # 调用 get_response 进行安全审查
    response = get_response(query=query)

    print(f"输入：{user_input};安全检查结果: {response}")

    # 提取结果格式，以 ";" 进行分隔，确定是否通过安全检查
    if "True" in response:
        return True, None
    else:
        return False, response

def extract_be_ids(compress_database_info_path):
    """
    从给定的文件中提取所有的 be_id 并返回列表。

    :param compress_database_info_path: 文件路径
    :return: 包含所有 be_id 的列表
    """
    be_ids = []
    try:
        with open(compress_database_info_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # 使用正则表达式匹配 be_id
            be_ids = re.findall(r'be_id=([\w-]+)', content)
    except Exception as e:
        print(f"Error reading file: {e}")
    return be_ids

def get_table_info(be_ids, compress_database_info_path):
    """
    根据给定的 BE_ID 列表，从压缩数据库信息文件中查找对应的表信息。

    参数:
    - be_ids: 涉及到的 BE_ID 列表。
    - compress_database_info_path: 压缩数据库信息文件路径。

    返回:
    - 涉及到的表的详细信息，以字符串形式返回。
    """
    table_info_list = []

    # 正则表达式用于解析 BECompressEntity 的内容
    entity_pattern = re.compile(
        r"BECompressEntity\(be_id=(.*?), table_id=(.*?), table_name=(.*?), "
        r"header_names=\[(.*?)\], header_meanings=\[(.*?)\], header_types=\[(.*?)\], "
        r"header_units=\[(.*?)\], header_attribute=\[(.*?)\]\)"
    )

    # 打开文件并读取内容
    try:
        with open(compress_database_info_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 匹配每一行的 BECompressEntity 格式
                match = entity_pattern.search(line)
                if match:
                    entity_be_id = match.group(1).strip()
                    if entity_be_id in be_ids:
                        # 获取相关信息
                        table_id = match.group(2).strip()
                        table_name = match.group(3).strip()
                        header_names = [name.strip() for name in match.group(4).split(", ")]
                        header_meanings = [meaning.strip() for meaning in match.group(5).split(", ")]
                        
                        # 构建字段信息字符串
                        field_info = "\n            ".join(  # 注意这里直接调整为多一级缩进
                            f"{name}: {meaning}" for name, meaning in zip(header_names, header_meanings)
                        )

                        table_info = (
                            f"    BE_ID: {entity_be_id}\n"
                            f"        table_id: {table_id}\n"
                            f"        table_name: {table_name}\n"
                            f"        字段信息:\n"
                            f"            {field_info}\n"  # 不需要再加额外缩进
                        )
                        table_info_list.append(table_info)
                        
    except FileNotFoundError:
        print(f"文件 {compress_database_info_path} 未找到.")
    except Exception as e:
        print(f"读取文件时出现错误: {e}")
    
    # 检查结果
    if not table_info_list:
        print("没有找到匹配的表信息。")
        return None

    return "\n".join(table_info_list)

def generate_BQL(relative_database_info, user_input):
    """
    生成BQL语句

    参数:
    - relative_database_info: 涉及到的表的详细信息
    - user_input: 用户输入的自然语言查询描述

    返回:
    - 生成的BQL语句
    """

    query = BQL_generate_template.format(relative_database_info, user_input)

    response = get_response(query=query)

    return response

def cmd_user_query_interface(be_compress_path):
    print("欢迎使用NL2BQL查询助手。请在输入查询描述后按回车键。输入'exit'退出对话。\n")
    
    while True:
        # Step 1: 获取用户输入
        user_input = input("请输入查询描述: ")
        
        # 检查退出指令
        if user_input.lower() == "exit":
            print("\n感谢您的使用，期待下次再见！")
            break

        # Step 2: 执行安全检查
        is_safe, error_reason = security_check(user_input)
        
        if not is_safe:
            # 如果安全检查未通过，返回错误原因并继续下一个循环
            print(f"\n十分抱歉,您的查询请求未通过安全审查,原因: {error_reason}")
            print("-" * 50)
            continue
        
        # Step 2: 检索数据库信息
        all_be_id = extract_be_ids(be_compress_path)

        all_table_info = get_table_info(all_be_id,be_compress_path)
        
        database_info_query = retrieve_database_info_template.format(all_table_info, user_input)

        # Step 3: 获得筛选数据

        database_info_response = get_response(database_info_query)

        database_info_response_split = database_info_response.split(";")

        specific_be_id = []

        for be_id in database_info_response_split:
            specific_be_id.append(be_id.strip())

        specific_table_info = get_table_info(specific_be_id,be_compress_path)
        
        if not specific_be_id or not specific_table_info:
            print("\n十分抱歉,无法检索到相关数据库信息，请检查查询描述是否正确。")
            print("-" * 50)
            continue
        
        # Step 4: 生成 BQL 语句
        bql_statement = generate_BQL(specific_table_info, user_input)
        
        # 输出生成的 BQL 语句并加分界线
        print(f"\n生成的 BQL 语句:\n{bql_statement}")
        print("=" * 50 + "\n")

def gradio_user_query_interface(be_compress_path):
    # 创建Gradio界面
    with gr.Blocks() as demo:
        gr.Markdown("# 欢迎使用NL2BQL查询助手,请输入您想要查询的语句.")

        chatbox = gr.Chatbot(label="Chat")  # 创建一个Chatbot来显示对话历史
        user_input = gr.Textbox(label="请输入查询描述", placeholder="请输入查询描述...", elem_id="user_input", show_label=False)
        
        # 将 submit 和 clear 放在同一行
        with gr.Row():
            clear_button = gr.Button("clear")
            submit_button = gr.Button("submit")

        def add_message_to_chatbox(user_message, history):
            # 调用 API 获取响应
            status,response = query_api(user_message,be_compress_path,be_id_need=False)
            # 添加用户消息和 API 响应到历史记录
            history.append((user_message,response))
            return history

        # 按钮点击事件：将用户输入添加到对话框，并清空输入框
        submit_button.click(add_message_to_chatbox, inputs=[user_input, chatbox], outputs=chatbox)
        submit_button.click(lambda: "", None, user_input)  # 清空输入框
        user_input.submit(add_message_to_chatbox, inputs=[user_input, chatbox], outputs=chatbox)  # 回车提交功能
        user_input.submit(lambda: "", None, user_input)  # 回车后清空输入框

        # 清空对话框
        clear_button.click(lambda: [], None, chatbox)

    return demo

def extract_bql_snippet(text):
    """
    提取文本中从 '''sql\n 到下一次 \n 中间的 BQL 部分。

    :param text: 包含 BQL 片段的字符串
    :return: 提取的 BQL 语句列表
    """
    # 匹配多个边界模式的正则表达式
    pattern = r"(?:```|'''|\"\"\")sql\n(.*?)(?:\n```|\n'''|\n\"\"\")"
    matches = re.findall(pattern, text, re.DOTALL)  # 使用 DOTALL 处理多行内容
    return matches[0]

def is_bql_snippet_format(text):
    """
    判断文本是否符合 '''sql\n 到 \n''' 的模式。

    :param text: 输入文本
    :return: 布尔值，是否符合模式
    """
    pattern = r"(?:```|'''|\"\"\")sql\n.*?(?:\n```|\n'''|\n\"\"\")"
    return bool(re.search(pattern, text, re.DOTALL))

def query_api(user_input,be_compress_path,be_id_need=False):
    """
    直接进行一次NL2BQL的任务,无交互
    输入: 用户输入的自然语言查询描述
    输出为下面的两种情况: 
        情况1，执行成功：True, "生成的BQL语句"
        情况2，执行失败：False, "错误原因"
    """
    # Step 1: 执行安全检查
    is_safe, error_reason = security_check(user_input)
    
    if not is_safe:
        # 如果安全检查未通过，返回错误原因
        if not be_id_need:
            return False, f"十分抱歉,您的查询请求未通过安全审查,原因: {error_reason}"
        else:
            return False, f"十分抱歉,您的查询请求未通过安全审查,原因: {error_reason}", None

    # Step 2: 检索数据库信息
    all_be_id = extract_be_ids(be_compress_path)

    all_table_info = get_table_info(all_be_id,be_compress_path)
    
    database_info_query = retrieve_database_info_template.format(all_table_info, user_input)

    # Step 3: 获得筛选数据

    database_info_response = get_response(database_info_query)

    database_info_response = database_info_response.strip().replace("\n", "")

    database_info_response_split = database_info_response.split(";")

    specific_be_id = []

    for be_id in database_info_response_split:
        if be_id != "":
            specific_be_id.append(be_id)

    specific_table_info = get_table_info(specific_be_id,be_compress_path)
    
    if not specific_be_id or not specific_table_info:
        # 如果无法检索到相关数据库信息，返回错误原因
        if not be_id_need:
            return False, "十分抱歉,无法检索到相关数据库信息,请检查查询描述是否正确。"
        else:
            return False, "十分抱歉,无法检索到相关数据库信息,请检查查询描述是否正确。", None
    
    # Step 4: 生成 BQL 语句
    BQL_respones = generate_BQL(specific_table_info, user_input)
    
    if is_bql_snippet_format(BQL_respones):
        BQL_respones = extract_bql_snippet(BQL_respones)

    # 返回执行成功和生成的结果
    if not be_id_need:
        return True, BQL_respones
    else:
        return True, BQL_respones, specific_be_id

def generate_test_result(test_excel_path, result_save_path,be_compress_path):
    """
    生成测试结果并写入JSON文件
    输入: 
        test_excel_path: 测试用例的Excel文件路径
        result_save_path: 保存测试结果的文件夹路径，生成两个文件：
                          - result.json: 不带自然语言作为key的结果
                          - result_withNL.json: 带自然语言作为key的结果
        be_compress_path: 业务实体压缩文件路径
    """
    # 定义文件路径
    result_path = os.path.join(result_save_path, "result.json")
    result_with_nl_path = os.path.join(result_save_path, "result_withNL.json")

    # 读取 Excel 文件
    try:
        df = pd.read_excel(test_excel_path)
    except Exception as e:
        print(f"读取 Excel 文件时发生错误: {e}")
        return

    # 初始化保存结构
    results = {}
    results_with_nl = {}

    # 尝试加载已有的 result_withNL.json 数据
    if os.path.exists(result_with_nl_path):
        try:
            with open(result_with_nl_path, 'r', encoding='utf-8') as json_file:
                results_with_nl = json.load(json_file)
            print(f"加载已有的 {result_with_nl_path} 文件，避免重复查询。")
        except json.JSONDecodeError:
            print(f"{result_with_nl_path} 文件为空或损坏，将重新创建。")

    # 初始化不带自然语言的 results 格式
    if os.path.exists(result_path):
        try:
            with open(result_path, 'r', encoding='utf-8') as json_file:
                results = json.load(json_file)
        except json.JSONDecodeError:
            print(f"{result_path} 文件为空或损坏，将重新创建。")
    
    # 使用 tqdm 添加进度条
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        # 提取自然语言和相关业务信息
        user_query = row['自然语言']
        related_entities = row['相关业务实体']
        bql_statement = row['BQL语句']

        # 跳过已有查询
        if user_query in results_with_nl:
            print(f"查询: {user_query} 已存在于结果中，跳过。")
            # 为不带自然语言的格式生成递增编号
            entry_id = str(len(results) + 1)
            continue

        # 为不带自然语言的格式生成递增编号
        entry_id = str(len(results) + 1)

        status,BQL_respones,specific_be_id = query_api(user_query,be_compress_path,be_id_need=True)

        if status:
            # 创建记录
            entry_data = {
                "BeID": specific_be_id,
                "BQL": BQL_respones
            }
        else:
            entry_data = {
                "Error": BQL_respones
            }

        print(f"查询: {user_query} 结果: {entry_data}")

        # 更新到两个结果字典
        results[entry_id] = entry_data
        results_with_nl[user_query] = entry_data

        # 每条记录处理完后立即写回文件
        try:
            with open(result_path, 'w', encoding='utf-8') as result_file:
                json.dump(results, result_file, ensure_ascii=False, indent=4)
            with open(result_with_nl_path, 'w', encoding='utf-8') as result_with_nl_file:
                json.dump(results_with_nl, result_with_nl_file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"写入 JSON 文件时发生错误: {e}")
            break

    print(f"测试结果已保存到 {result_path} 和 {result_with_nl_path}")

def main():
    while True:
        # 提示用户选择模式
        print("请选择操作模式：")
        print("1. 生成测试结果模式")
        print("2. 使用命令行界面进行交互")
        print("3. 使用Gradio界面进行交互")
        print("4. 退出程序")

        # 获取用户选择
        mode = input("请输入 1、2、3 或 4 来选择模式: ").strip()
        print()

        # 获取当前工作目录
        current_dir = os.getcwd()

        if mode == "1":
            test_excel_path = os.path.join(current_dir, "NL2BQL测试验证集.xlsx")
            result_save_path = os.path.join(current_dir)
            be_compress_path = os.path.join(current_dir, "业务实体压缩结构.txt")
            # 调用生成测试结果的函数
            generate_test_result(test_excel_path, result_save_path, be_compress_path)
            break  # 执行完后跳出循环

        elif mode == "2":
            # 用户交互模式
            be_compress_path = os.path.join(current_dir, "业务实体压缩结构.txt")
            cmd_user_query_interface(be_compress_path)
            break  # 执行完后跳出循环

        elif mode == "3":
            be_compress_path = os.path.join(current_dir, "业务实体压缩结构.txt")
            # 使用Gradio界面进行交互
            import gradio as gr
            demo = gradio_user_query_interface(be_compress_path)  # 这里调用你定义的gradio界面函数
            demo.launch()
            print("\n感谢您的使用，期待下次再见！")
            break  # 执行完后跳出循环

        elif mode == "4":
            print("程序已退出。")
            break  # 退出程序

        else:
            # 输入无效，继续提示用户重新输入
            print("无效选择，请输入 1、2、3 或 4。")

# 调用 main 函数
if __name__ == "__main__":
    main()