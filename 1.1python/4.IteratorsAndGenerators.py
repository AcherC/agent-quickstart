import itertools
import os
import fnmatch
import time

# 1. 流式读取大文件（处理超大规模日志）
def stream_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

# 2. 跳过历史消息前 10 条，取接下来 5 条
messages = [
    "Hello, how can I assist you today?",
    "I need help with my research.",
    "Sure, what topic are you researching?"]
history = iter(messages)
recent = list(itertools.islice(history, 10, 15))

# 3. 多级 Agent 输出委托
# def agent_orchestrator(query):
#     yield from intent_classifier(query)   # 子生成器
#     yield from tool_selector(query)       # 子生成器
#     yield from executor(query)            # 子生成器

# 4. 合并多个 Tool 返回的结果流
def merge_results(*result_streams):
    yield from itertools.chain(*result_streams)

# 5. 数据处理管道：查找所有 .log 文件并产出路径
def gen_find(filepat, top):
    for path, _, filelist in os.walk(top):
        for name in fnmatch.filter(filelist, filepat):
            yield os.path.join(path, name)

# 题目：Agent 流式响应处理器

# 实现一个 StreamingResponseHandler 类，模拟处理 LLM 的流式输出（逐字/逐句返回）。

# 要求：

# simulate_stream(text, chunk_size=5)：生成器函数，每次产出 chunk_size 个字符，模拟流式输出
# filter_thinking(stream)：生成器函数，接收上面的流，实时过滤掉 <think>...</think> 标签内的内容（假设标签可能跨多个 chunk），只产出非思考内容
# count_tokens(stream)：生成器函数，接收流，在产出每个 chunk 的同时，累计已输出的字符数，产出 (chunk, total_count)
# show_stream(stream)：辅助函数，接收流，打印每个 chunk 及累计字符数
class StreamingResponseHandler:
    @staticmethod
    def simulate_stream(text, chunk_size=5):
        for i in range(0, len(text), chunk_size):
            yield text[i:i + chunk_size]

    @staticmethod
    def filter_thinking(stream):
        buffer = ""
        inside_think = False
        start_tag = "<think>"
        end_tag = "</think>"

        for chunk in stream:
            buffer += chunk

            if inside_think:
                end_idx = buffer.find(end_tag)
                if end_idx != -1:
                    buffer = buffer[end_idx + len(end_tag):]
                    inside_think = False
                else:
                    # 只保留可能构成结束标签前缀的尾部字符，其余都属于已确认的思考内容
                    if len(buffer) > len(end_tag) - 1:
                        buffer = buffer[-(len(end_tag) - 1):]
                    continue

            while True:
                start_idx = buffer.find(start_tag)
                if start_idx != -1:
                    if start_idx > 0:
                        yield buffer[:start_idx]
                    buffer = buffer[start_idx + len(start_tag):]
                    inside_think = True
                    break

                # 保留最后 len(start_tag)-1 个字符，防止标签跨 chunk 分裂
                if len(buffer) > len(start_tag) - 1:
                    yield buffer[:-len(start_tag) + 1]
                    buffer = buffer[-(len(start_tag) - 1):]
                    break

                # 还不足以确定是否是标签前缀，先暂存，等后续 chunk 继续判断
                break

        # 处理流结束时残留的正常文本；如果仍处于思考状态，则丢弃残余内容
        if not inside_think and buffer:
            yield buffer

    @staticmethod
    def count_tokens(stream):
        total_count = 0
        for chunk in stream:
            total_count += len(chunk)
            yield (chunk, total_count)

    @staticmethod
    def show_stream(stream, delay=0.0, flush=True):
        """
        逐块展示流式输出，可设置每次输出后的间隔时间。
        支持两种输入：
        1. 直接是字符串 chunk 流
        2. 是 (chunk, total_count) 的二元组流
        """
        total_count = 0
        for item in stream:
            if isinstance(item, tuple):
                chunk, total_count = item
            else:
                chunk = item
                total_count += len(chunk)

            if delay > 0:
                time.sleep(delay)

            print(f"Chunk: {chunk}, Total Count: {total_count}", flush=flush)

#验证
handler = StreamingResponseHandler()
text = "Hello <think>这是内部思考</think> World!"

# 测试 1：流式分块
chunks = list(handler.simulate_stream(text, chunk_size=5))
assert "".join(chunks) == text

# 测试 2：过滤思考内容
filtered = "".join(handler.filter_thinking(handler.simulate_stream(text, chunk_size=3)))
assert "Hello " in filtered
assert "World!" in filtered
assert "内部思考" not in filtered
assert "<think>" not in filtered
assert "</think>" not in filtered
# 测试 3：计数
result = list(handler.count_tokens(handler.simulate_stream("ABC", chunk_size=1)))
assert result[-1] == ("C", 3)

# **加试测试 4：模拟流式输出，可设置输出间隔
handler.show_stream(handler.count_tokens(handler.simulate_stream("Agent stream demo", chunk_size=4)), delay=0.01)


