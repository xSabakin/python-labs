import argparse
import csv
import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

print(f"Студент: {STUDENT_NAME} | Група {GROUP_NAME} | Варіант: {VARIANT_NUMBER}  ")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

logger = logging.getLogger(__name__)

LOG_PATTERN = re.compile(
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+-\s+-\s+"
    r"\[(?P<datetime>[^\]]+)\]\s+"
    r'"(?P<method>[A-Z]+)\s+(?P<uri>[^\s]+)\s+HTTP/[0-9.]+"\s+'
    r"(?P<status>\d{3})\s+"
    r"(?P<size>\d+)"
)

ATTACK_SIGNATURES = {
    "SQLi": re.compile(
        r"(\%27|'|\bOR\b.*=|\bUNION\b.*\bSELECT\b|--',?|1=1)", re.IGNORECASE
    ),
    "Directory Traversal": re.compile(
        r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow)", re.IGNORECASE
    ),
    "XSS": re.compile(r"(<script.*?>|alert\(.*?\))", re.IGNORECASE),
}


def parse_access_log(file_path: Path):
    entries = []
    if not file_path.exists():
        logger.error(f"Файл логу не знайдено за шляхом: {file_path}")
        return entries

    logger.info(f"Loading access log from {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = LOG_PATTERN.match(line.strip())
            if match:
                data = match.groupdict()
                data["status"] = int(data["status"])
                data["size"] = int(data["size"])
                entries.append(data)

    logger.info(f"Processed {len(entries)} log entries.")
    return entries


def analyze_logs(
    log_file: str, output_path: str, min_status: int, top_n: int, report_format: str
):
    path = Path(log_file)
    entries = parse_access_log(path)

    if not entries:
        return

    ip_errors = Counter()
    ip_status_breakdown = defaultdict(Counter)
    attack_alerts = []

    for entry in entries:
        ip = entry["ip"]
        status = entry["status"]
        uri = entry["uri"]
        method = entry["method"]

        if status >= min_status:
            ip_errors[ip] += 1
            ip_status_breakdown[ip][status] += 1

        full_request = f"{method} {uri}"
        for attack_type, pattern in ATTACK_SIGNATURES.items():
            if pattern.search(uri):
                attack_alerts.append(
                    {"ip": ip, "type": attack_type, "request": full_request}
                )

    print(f"\n=== Top-{top_n} IP Addresses with Error Statuses (4xx/5xx) ===")
    top_ips = ip_errors.most_common(top_n)
    for ip, total_err in top_ips:
        breakdown_str = ", ".join(
            [
                f"{status}: {count}"
                for status, count in sorted(ip_status_breakdown[ip].items())
            ]
        )
        print(f"{ip}")
        print(f"  {total_err} errors ({breakdown_str})")

    print("\n=== Detected Attack Signatures ===")
    unique_alerts = []
    seen = set()
    for alert in attack_alerts:
        identifier = (alert["ip"], alert["type"], alert["request"])
        if identifier not in seen:
            seen.add(identifier)
            unique_alerts.append(alert)
            print(
                f'[ALERT] Potential {alert["type"]} attack from {alert["ip"]}: "{alert["request"]}"'
            )

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    report_data = {
        "top_error_ips": [
            {"ip": ip, "errors": count, "breakdown": dict(ip_status_breakdown[ip])}
            for ip, count in top_ips
        ],
        "detected_attacks": unique_alerts,
    }
    try:
        if report_format.lower() == "json":
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)
        elif report_format.lower() == "csv":
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["IP", "AttackType", "Request"])
                for alert in unique_alerts:
                    writer.writerow([alert["ip"], alert["type"], alert["request"]])

        print(f"звіт успішно збережено{out_file}")

    except IsADirectoryError:
        print(f"Помилка: '{out_file}' є директорією, а не файлом.")
    except OSError as e:
        print(f"Помилка файлової системи (I/O) під час збереження: {e}")
    except (TypeError, ValueError) as e:
        print(f"Некоректні дані для збереження: {e}")

    logger.info(f"Analysis report saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Server Access Log Analyzer")
    parser.add_argument(
        "--log-file", default="labs/lab02/data/access.log", help="Шлях до файлу логу"
    )
    parser.add_argument(
        "--output",
        default="labs/lab02/data/web_analysis_report.json",
        help="Шлях для збереження звіту",
    )
    parser.add_argument(
        "--min-status", type=int, default=400, help="Мінімальний статус-код помилки"
    )
    parser.add_argument("--top", type=int, default=3, help="Кількість топ IP-адрес")
    parser.add_argument(
        "--format", default="json", choices=["json", "csv"], help="Формат звіту"
    )

    args = parser.parse_args()
    analyze_logs(args.log_file, args.output, args.min_status, args.top, args.format)
