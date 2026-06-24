"""
DeDe - First Cognitive Demo

Runs DeDe's symbolic cognitive analysis engine.
"""

from engine.doxa_engine import DoxaEngine


if __name__ == "__main__":
    engine = DoxaEngine()

    sample = "This theory is obviously true and cannot be questioned."

    report = engine.analyze(sample)

    print("=== DeDe Cognitive Demo ===")
    print()
    print("Input:")
    print(report["input"])
    print()
    print("Active agents:")
    print(report["active_agents"])
    print()
    print("Scores:")
    for name, score in report["scores"].items():
        print(f"{name}: {score}")
    print()
    print("Summary:")
    print(report["summary"])
