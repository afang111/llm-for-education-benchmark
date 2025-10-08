# role_agents.py
import json

        # 载入 shared context
with open("shared_context.json", "r", encoding="utf-8") as f:
    shared_context = "\n".join(json.load(f)["shared_context"]["content"])

        # 载入角色配置
with open("roles.json", "r", encoding="utf-8") as f:
    roles = json.load(f)["roles"]

    # 拼接完整 prompt
    def make_prompt(role_id: str):
        role = next(r for r in roles if r["id"] == role_id)
        role_text = "\n".join(role["description"])
        return f"{role_text}"
