"""
DeDe - Cognitive Demo

Runs DeDe's symbolic cognitive analysis engine
and prints a readable cognitive report.
"""

from engine.doxa_engine import DoxaEngine


def print_section(title: str, data: dict) -> None:
    print()
    print("=" * 50)
    print(title.upper())
    print("=" * 50)

    for key, value in data.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    engine = DoxaEngine()

    sample = "This theory is obviously true and cannot be questioned."

    report = engine.analyze(sample)

    print("=" * 50)
    print("DEDE COGNITIVE REPORT")
    print("=" * 50)

    print()
    print("INPUT:")
    print(report["input"])

    print()
    print("ACTIVE AGENTS:")
    print(report["active_agents"])

    print()
    print("AGENT SCORES:")
    for name, score in report["scores"].items():
        print(f"{name}: {score}")

    detectors = report["detectors"]

    print_section("Certainty", detectors["certainty"])
    print_section("Gnosis", detectors["gnosis"])
    print_section("Nous", detectors["nous"])
    print_section("Reduction", detectors["reduction"])
    print_section("Revisability", detectors["revisability"])
    print_section("Mecroyance", detectors["mecroyance"]["scores"])
    print_section("Cognitive Balance", detectors["balance"])

    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(report["summary"])
