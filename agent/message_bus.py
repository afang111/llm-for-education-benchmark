from typing import List


class MessageBus:
    def __init__(self):
        self.history = []

    def post(self, speaker, content):
        self.history.append({"role": speaker, "content": content})

    def get_context(self) -> str:
        return "\n".join(f"{h['role']}: {h['content']}" for h in self.history)

    def get_message_list(self) -> List[dict]:
        # 返回符合 Claude SDK 的格式（不带 system）
        return [{"role": "user", "content": self.get_context()}]
