import argparse

from labs.lab02.task1 import demo as run_demo
from labs.lab02.task2 import analyze_logs


def main():
    parser = argparse.ArgumentParser(description="Lab 02 - Cybersecurity CLI Utilities")
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Доступні команди"
    )

    # Команда demo для Завдання 1
    subparsers.add_parser(
        "demo", help="Запустити демонстрацію ООП моделей (Завдання 1)"
    )

    # Команда analyze для Варіанта 1 (Завдання 2)
    analyze_parser = subparsers.add_parser(
        "analyze", help="Аналіз журналів веб-сервера (Завдання 2)"
    )
    analyze_parser.add_argument(
        "--log-file", default="labs/lab02/data/access.log", help="Шлях до access.log"
    )
    analyze_parser.add_argument(
        "--output",
        default="labs/lab02/data/web_analysis_report.json",
        help="Шлях до звіту",
    )
    analyze_parser.add_argument(
        "--min-status", type=int, default=400, help="Мінімальний статус помилки"
    )
    analyze_parser.add_argument(
        "--top", type=int, default=3, help="Кількість топ IP-адрес"
    )
    analyze_parser.add_argument(
        "--format", default="json", choices=["json", "csv"], help="Формат звіту"
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        analyze_logs(
            log_file=args.log_file,
            output_path=args.output,
            min_status=args.min_status,
            top_n=args.top,
            report_format=args.format,
        )


if __name__ == "__main__":
    main()
