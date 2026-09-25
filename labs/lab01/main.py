import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from labs.lab01 import task1, task2, task3


def main():
    print("=" * 24)
    print("ЗАВДАННЯ 1")
    print("=" * 24)
    task1.main()

    print("\n" + "=" * 24)
    print("ЗАВДАННЯ 2")
    print("=" * 24)
    task2.main()

    print("\n" + "=" * 24)
    print("ЗАВДАННЯ 3")
    print("=" * 24)
    task3.main()


if __name__ == "__main__":
    main()