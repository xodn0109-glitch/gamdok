"""웹앱용 시험감독 데이터의 구조와 중복 배정을 검사한다."""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED_FIELDS = ("grade", "class", "exam", "time", "period")
TIME_PATTERN = re.compile(r"^(\d{2}):(\d{2})~(\d{2}):(\d{2})$")
PERIOD_PATTERN = re.compile(r"^(?:\d+교시\(\d+분\)(?: (?:담임|부담임))?|부담임\(\d+분\))$")


def load_schedule(data_path):
    content = data_path.read_text(encoding="utf-8")
    match = re.search(r"const\s+scheduleData\s*=\s*(\{.*\})\s*;\s*$", content, re.S)
    if not match:
        raise ValueError("scheduleData JavaScript 객체를 찾지 못했습니다.")
    return json.loads(match.group(1))


def to_minutes(hour, minute):
    return int(hour) * 60 + int(minute)


def validate(schedule_data):
    issues = []
    total_assignments = 0
    intervals_by_teacher = defaultdict(list)

    if not isinstance(schedule_data, dict) or not schedule_data:
        return ["scheduleData가 비어 있거나 객체가 아닙니다."], total_assignments

    for teacher, schedules in schedule_data.items():
        if not isinstance(teacher, str) or not teacher.strip():
            issues.append("비어 있는 교사 이름이 있습니다.")
        if not isinstance(schedules, list) or not schedules:
            issues.append(f"{teacher}: 배정 목록이 비어 있거나 배열이 아닙니다.")
            continue

        for index, assignment in enumerate(schedules, start=1):
            total_assignments += 1
            if not isinstance(assignment, dict):
                issues.append(f"{teacher} #{index}: 배정 값이 객체가 아닙니다.")
                continue

            missing = [field for field in REQUIRED_FIELDS if not str(assignment.get(field, "")).strip()]
            if missing:
                issues.append(f"{teacher} #{index}: 필수값 누락 ({', '.join(missing)})")
                continue

            period = assignment["period"]
            if not PERIOD_PATTERN.fullmatch(period):
                issues.append(f"{teacher} #{index}: 잘못된 감독 구분 ({period})")

            time_match = TIME_PATTERN.fullmatch(assignment["time"])
            if not time_match:
                issues.append(f"{teacher} #{index}: 잘못된 시간 형식 ({assignment['time']})")
                continue

            start = to_minutes(time_match.group(1), time_match.group(2))
            end = to_minutes(time_match.group(3), time_match.group(4))
            if end <= start:
                issues.append(f"{teacher} #{index}: 종료 시각이 시작 시각보다 빠르거나 같습니다.")
                continue
            intervals_by_teacher[teacher].append((start, end, assignment["time"]))

    for teacher, intervals in intervals_by_teacher.items():
        intervals.sort()
        for (_, previous_end, previous_text), (start, _, current_text) in zip(intervals, intervals[1:]):
            if start < previous_end:
                issues.append(f"{teacher}: 감독 시간이 겹칩니다 ({previous_text} / {current_text})")

    return issues, total_assignments


def main():
    parser = argparse.ArgumentParser(description="시험감독 웹앱 데이터 검사")
    parser.add_argument("--data", type=Path, default=Path("schedule_data.js"))
    args = parser.parse_args()

    try:
        schedule_data = load_schedule(args.data)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    issues, total = validate(schedule_data)
    if issues:
        print(f"FAIL: {len(issues)}건의 데이터 문제가 있습니다.", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    print(
        f"PASS: 교사 {len(schedule_data)}명, 배정 {total}건, "
        "필수값·시간 형식·감독 시간 중복 이상 없음"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
