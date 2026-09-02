import re
from string import Template
import textwrap
# 字符串与文本处理 示例、实现与测试

# -----------------------------
# 前置示例（示范用法）
# -----------------------------

# 1. 从 LLM 输出中提取 <think> 标签内容（非贪婪）
text = "<think>推理中...</think>最终答案是42"
match = re.search(r'<think>(.*?)</think>', text, re.DOTALL)
if match:
    reasoning = match.group(1)

# 2. Prompt 模板（适合从配置文件加载）
prompt_tmpl = Template("""
你是 $role，请使用 $tool 完成以下任务：
$task
""")
prompt = prompt_tmpl.substitute(role="ResearchAgent", tool="web_search", task="查天气")

# 3. 格式化 Agent 状态表格
status = [("Agent", "Status"), ("Planner", "running"), ("Executor", "idle")]
for name, state in status:
    print(f"{name:<10} | {state:>10}")

# 4. 控制输出宽度（适合日志）
log = "Agent completed the task with multiple steps and returned a very long result..."
print(textwrap.fill(log, width=50))

# 题目：LLM 输出解析器
# 实现 LLMOutputParser 类，解析包含 <think>、<tool_call>、<output> 标签的 LLM 输出字符串。
# 要求实现以下方法：
# extract_think(text) -> 提取 <think>...</think> 内的内容（可能跨多行）
# extract_tool_calls(text) -> 提取所有 <tool_call>{"name":"xxx","args":{...}}</tool_call>，返回字典列表
# sanitize_prompt(prompt) -> 移除 prompt 中所有 XML 标签，只保留纯文本

class LLMOutputParser:
    @staticmethod
    def extract_think(text):
        match = re.search(r'<think>(.*?)</think>', text, re.DOTALL)
        return match.group(1) if match else None

    @staticmethod
    def extract_tool_calls(text):
        tool_calls = re.findall(r'<tool_call>(.*?)</tool_call>', text, re.DOTALL)
        result = []
        for call in tool_calls:
            try:
                # 假设内容是 JSON 格式
                import json
                result.append(json.loads(call))
            except json.JSONDecodeError:
                continue
        return result

    @staticmethod
    def sanitize_prompt(prompt):
        return re.sub(r'<.*?>', '', prompt)  # 移除所有 XML 标签

parser = LLMOutputParser()
text = """<think>
我需要搜索天气。
</think>
<tool_call>{"name":"search","args":{"q":"北京天气"}}</tool_call>
<output>晴天 25°C</output>"""

assert "我需要搜索天气" in parser.extract_think(text)
assert parser.extract_tool_calls(text)[0]["name"] == "search"
assert "<think>" not in parser.sanitize_prompt(text)
assert "晴天 25°C" in parser.sanitize_prompt(text)