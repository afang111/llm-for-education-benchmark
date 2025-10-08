# simulator.py
import os
import json
import random
from chat_agent import ChatAgent
from role_agent import make_prompt
from message_bus import MessageBus 
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("❌ Missing ANTHROPIC_API_KEY in .env or environment")

TERMINATE_SIGNAL = "<terminate>"
AGREE_TERMINATE = "<agree_terminate>"
MINIMUM_ROUNDS = 6  # 至少 6 轮之后才允许终止

def run_freeflow_panel(question):
    with open("shared_context.json", "r", encoding="utf-8") as f:
        shared_context = "\n".join(json.load(f)["shared_context"]["content"])

    with open("roles.json", "r", encoding="utf-8") as f:
        roles = json.load(f)["roles"]

    bus = MessageBus()

    student_prompt = make_prompt("mathstudent")
    teacher_prompt = make_prompt("mathteacher")
    scientist_prompt = make_prompt("cognitivescientist")

    student = ChatAgent(name="MathStudent", bus=bus, system_prompt=student_prompt)
    teacher = ChatAgent(name="MathTeacher", bus=bus, system_prompt=teacher_prompt)
    scientist = ChatAgent(name="CognitiveScientist", bus=bus, system_prompt=scientist_prompt)
    agents = [student, teacher, scientist]

    bus.post("System", f"Topic: {question}")
    print(f"\n🎩 Discussion topic: {question}")

    current_agent = random.choice(agents)
    termination_votes = {agent.name: False for agent in agents}

    for round_i in range(1, 15):  # 最多 15 轮防止死循环
        print(f"\n===== 🌀 Round {round_i}: {current_agent.name} =====")

        context = bus.get_context()
        reply = current_agent.step(
            f"""Based on the discussion so far, continue the conversation about: {question}
{context}, please output the answer in strict JSON format, containing the following three fields:
{{
  \"skills\": [\"skill1\", \"skill2\", \"skill3\"],
  \"thoughts\": \"First I ...\",
  \"answer\": \"answer\"
}}"""
        )

        print(f"\n{current_agent.name}: {reply}\n")
        bus.post(current_agent.name, reply)

        # 记录终止投票
        if TERMINATE_SIGNAL in reply or AGREE_TERMINATE in reply:
            termination_votes[current_agent.name] = True
        else:
            termination_votes[current_agent.name] = False

        votes = list(termination_votes.values())
        voter_names = [k for k, v in termination_votes.items() if v]

        # 检查是否满足终止条件
        if (
            votes.count(True) >= 2 and
            round_i >= MINIMUM_ROUNDS and
            any(name == "CognitiveScientist" for name in voter_names)
        ):
            print("\n🚀 Termination approved by majority (with expert consensus).")
            break

        next_agent = select_next_speaker(current_agent, agents, reply)
        current_agent = next_agent

    # 最后由 CognitiveScientist 生成总结
    summary_input = (
        f"Here is the full discussion history:\n{json.dumps(bus.history, indent=2)}\n\n"
        "Please summarize the discussion as JSON including consensus_skills, alt_skills, rationale.please output the answer in strict JSON format, containing the following three fields:"
"{{"
  "\"skills\": [\"skill1\", \"skill2\", \"skill3\"],"
  "\"thoughts\": \"First I ...\","
  "\"answer\": \"answer\""
"}}"
    )
    final_summary = scientist.step(summary_input)
    print("\n🧠 Final Summary:\n", final_summary)


def select_next_speaker(current_agent, agents, reply):
    if "student" in reply.lower():
        return next((a for a in agents if a.name == "MathStudent"), current_agent)
    if "teacher" in reply.lower():
        return next((a for a in agents if a.name == "MathTeacher"), current_agent)
    if "scientist" in reply.lower() or "expert" in reply.lower():
        return next((a for a in agents if a.name == "CognitiveScientist"), current_agent)
    candidates = [a for a in agents if a.name != current_agent.name]
    return random.choice(candidates) if candidates else current_agent


if __name__ == "__main__":
    run_freeflow_panel("7/9 - 2/9")
