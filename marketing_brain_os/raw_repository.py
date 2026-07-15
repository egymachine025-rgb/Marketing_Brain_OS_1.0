from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional

class RawRepository:
    """
    يقرأ رسائل التليجرام الخام المخزنة في النظام بواسطة TASK-005.
    """
    def __init__(self, base_dir: str = "data/raw_channels") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def get_all_channels(self) -> List[str]:
        if not os.path.exists(self.base_dir):
            return []
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def list_messages(self, channel: str) -> List[int]:
        channel_dir = os.path.join(self.base_dir, channel)
        if not os.path.exists(channel_dir):
            return []
        messages = []
        for f in os.listdir(channel_dir):
            if f.endswith(".json"):
                try:
                    messages.append(int(f.replace(".json", "")))
                except ValueError:
                    continue
        return sorted(messages)

    def load(self, channel: str, message_id: int) -> Optional[Dict[str, Any]]:
        filepath = os.path.join(self.base_dir, channel, f"{message_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)