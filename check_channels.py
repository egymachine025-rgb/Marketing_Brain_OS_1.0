from pathlib import Path

raw_dir = Path("data/raw/telegram")
channels = [d for d in raw_dir.iterdir() if d.is_dir()]

print(f"Found {len(channels)} channels:")
for ch in channels:
    msgs = list(ch.glob("*.json"))
    print(f"  📁 {ch.name}")
    print(f"     Messages: {len(msgs)}")
    for m in msgs[:3]:
        print(f"       - {m.name}")