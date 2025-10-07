import json
import os

print(os.environ.get("ANTHROPIC_API_KEY"))

from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# 确认 API Key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("❌ 没有检测到 ANTHROPIC_API_KEY，请先运行 export ANTHROPIC_API_KEY=sk-xxxx")

# === 1. 加载数据集 ===
with open("fractions_benchmark.json", "r") as f:
    dataset = json.load(f)

# === 2. 初始化 Claude 模型 ===
llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",   # 你用的模型名字
    temperature=0,
    max_tokens=512
)

# 定义一个统一的 prompt
prompt = ChatPromptTemplate.from_template(
    """你是一个分数计算老师。请解答下面的题目，并输出 JSON 格式结果。
题目: {question}

严格输出这个 JSON：
{{
  "answer": "...",
  "skills": ["α1","α4"],
  "explanation": "逐步写出解题过程，并指出用了哪些技能"
}}"""
)

# === 3. 调用智能体 ===
def solve(question: str):
    chain = prompt | llm
    resp = chain.invoke({"question": question})
    content = resp.content.strip()

    try:
        result = json.loads(content)
    except Exception:
        # 如果 Claude 没有输出 JSON，就包装一下
        result = {"answer": "", "skills": [], "explanation": content}

    return {
        "answer": result.get("answer", ""),
        "skills_used": result.get("skills", []),
        "explanation": result.get("explanation", "")
    }

# === 4. 评测函数 ===
def evaluate(example, result):
    expected_skills = set(example.get("skills", []))
    alt_skills = set(example.get("alt_skills", []))

    answer_ok = (result["answer"] == example.get("answer", None))
    skills_pred = set(result["skills_used"])
    skill_ok = (skills_pred == expected_skills) or (skills_pred == alt_skills)
    explanation_ok = all(s in result.get("explanation", "") for s in expected_skills)

    return {
        "id": example["id"],
        "question": example["question"],
        "expected_answer": example.get("answer", None),
        "model_answer": result["answer"],
        "expected_skills": list(expected_skills),
        "model_skills": result["skills_used"],
        "correct": answer_ok,
        "skill_ok": skill_ok,
        "process_ok": explanation_ok,
        "explanation": result.get("explanation", "")
    }

# === 5. 跑 benchmark ===
results = []
for ex in dataset:
    res = solve(ex["question"])
    results.append(evaluate(ex, res))

accuracy = sum(r["correct"] for r in results) / len(results)
skill_match = sum(r["skill_ok"] for r in results) / len(results)
process_match = sum(r["process_ok"] for r in results) / len(results)

print("\n📑 Detailed Results:")
for r in results:
    errors = []
    if not r["correct"]:
        errors.append("Answer Wrong")
    if not r["skill_ok"]:
        errors.append("Skill Wrong")
    if not r["process_ok"]:
        errors.append("Process Wrong")

    if not errors:
        status = "✅ PASS"
    else:
        status = "❌ FAIL (" + ", ".join(errors) + ")"

    print(f"\n{status} | {r['id']} | {r['question']}")
    print(f"  Expected Answer: {r['expected_answer']}")
    print(f"  Model Answer:   {r['model_answer']}")
    print(f"  Expected Skills: {r['expected_skills']}")
    print(f"  Model Skills:    {r['model_skills']}")
    print(f"  Explanation: {r['explanation']}")
