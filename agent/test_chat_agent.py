# test_chat_agent.py
from chat_agent import ChatAgent
from message_bus import MessageBus  # 假设你也实现了一个 MessageBus 类
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("❌ Missing ANTHROPIC_API_KEY in .env or environment")

def main():

    # 初始化总线
    bus = MessageBus()

    # 初始化 agent
    system_prompt = """
    You are a careful and honest college student who needs to solve a fraction subtraction problem. You will be given a fraction subtraction problem to solve.

<fraction_problem>
{{FRACTION_PROBLEM}}
</fraction_problem>

You need to accomplish two things:
1. Correctly solve the problem
2. Clearly identify which mathematical techniques you used in the solving process (choose only from α₁–α₅)

Here are the five available mathematical techniques:

α₁: Basic fraction subtraction — Subtracting fractions with the same denominator. Example: 3/5 − 2/5 = 1/5

α₂: Simplification or reduction — Converting fractions to simplest form, or converting improper fractions to mixed numbers. Example: 6/12 = 1/2, 17/5 = 3 2/5

α₃: Separating whole and fraction parts — Breaking mixed numbers into whole number and fraction components. Example: 3 2/5 − 1 3/5 = (3 − 1) + (2/5 − 3/5)

α₄: Borrowing — When the fraction part of the minuend is smaller, borrow 1 from the whole number part and convert it to a fraction. Example: 2 1/3 − 1 2/3 = 1 4/3 − 1 2/3

α₅: Converting whole numbers to fractions — Converting whole numbers to fraction form for easier calculation. Example: 1 − 1/8 = 8/8 − 1/8

---
Termination Protocol:

When you believe the discussion is sufficient, you may provide a <terminate> marker;

If two other participants in subsequent rounds each output <agree_terminate>, the discussion will immediately terminate;

All agents must still maintain JSON format structure in their output.

You must output your answer in **strict JSON format** containing the following three fields:

{
  "skills": ["skill1", "skill2", "skill3"],
  "thoughts": "First I ...",
  "answer": "answer",
  "action": "<terminate>" or "<agree_terminate>" (if you wish to terminate discussion, otherwise this field can be omitted)
}

⚠️ Output Requirements:
- Must be valid JSON format
- Cannot include Markdown, extra text, or explanations
- Do not add phrases like "Here's my answer" before or after
- Output should contain only the JSON object itself

"""
  


        
        
    agent = ChatAgent(name="MathTeacher", bus=bus, system_prompt=system_prompt)

    print(agent.system_prompt)
    # 发送初始问题
    initial_input = "Can you explain how to subtract 7/9 - 5/9?"
    bus.post("User", initial_input)

    # Agent 回应
    reply = agent.step(initial_input)

    print(f"\n🧠 {agent.name}'s reply:\n{reply}")

    # 查看总线内容
    print("\n🧾 MessageBus contents:")
    for entry in bus.history:
        print(f"{entry['role']}: {entry['content']}")

    print()
if __name__ == "__main__":
    main()
