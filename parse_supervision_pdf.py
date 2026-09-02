"""시험감독 배정표 PDF를 웹앱용 ``scheduleData``로 변환한다.

PDF 표의 1·2·3학년 페이지를 읽어 교사별 배정으로 재구성한다. 원본 PDF에는
병합 셀과 줄바꿈이 있으므로, 현재 배정표의 학년별 반 목록을 명시해 열 손실을
방지한다.
"""
import argparse
import json
import re
from pathlib import Path

import pdfplumber


GRADE_CLASSES = {
    "1학년": [f"1-{number}" for number in range(1, 11)],
    "2학년": [f"2-{number}" for number in range(1, 10)],
    "3학년": [
        *[f"3-{number}" for number in range(1, 13)],
        "졸업생 4층 후동 PBL실2",
    ],
}
TIME_PATTERN = re.compile(r"^(\d{2}:\d{2}~\d{2}:\d{2})")
PERIOD_PATTERN = re.compile(r"(\d+교시\s*\(\s*\d+분\s*\))(?:\s*(담임|부담임))?")


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_period(value):
    """교시·시간과 담임/부담임 역할을 한 줄의 화면용 값으로 정리한다."""
    match = PERIOD_PATTERN.search(clean_text(value))
    if not match:
        return None
    period = re.sub(r"\s+", "", match.group(1))
    role = match.group(2)
    return f"{period} {role}" if role else period


def find_assignment_table(page):
    tables = page.extract_tables()
    candidates = [table for table in tables if len(table) >= 10]
    if len(candidates) != 1:
        raise ValueError(f"배정표를 하나로 식별하지 못했습니다: {len(candidates)}개")
    return candidates[0]


def add_assignment(schedule, teacher, assignment):
    if not teacher:
        return
    schedule.setdefault(teacher, []).append(assignment)


def build_schedule(pdf_path):
    schedule = {}
    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) != 3:
            raise ValueError(f"학년별 3쪽 배정표가 필요합니다. 현재 {len(pdf.pages)}쪽입니다.")

        for page, (grade, classes) in zip(pdf.pages, GRADE_CLASSES.items()):
            table = find_assignment_table(page)
            current_exam = ""

            for row_number, row in enumerate(table[1:], start=2):
                cells = [clean_text(cell) for cell in row]
                period = normalize_period(cells[2])
                if not period:
                    continue

                time_match = TIME_PATTERN.match(cells[1])
                if not time_match:
                    continue

                if cells[0]:
                    current_exam = cells[0]
                if not current_exam:
                    raise ValueError(f"{grade} {row_number}행에 시험명이 없습니다.")

                teachers = cells[3:]
                if len(teachers) != len(classes):
                    raise ValueError(
                        f"{grade} {row_number}행의 반 수({len(classes)})와 "
                        f"교사 칸 수({len(teachers)})가 다릅니다."
                    )

                for class_name, teacher_cell in zip(classes, teachers):
                    for teacher in teacher_cell.split():
                        add_assignment(
                            schedule,
                            teacher,
                            {
                                "grade": grade,
                                "class": class_name,
                                "exam": current_exam,
                                "time": time_match.group(1),
                                "period": period,
                            },
                        )
    return schedule


def write_schedule(schedule, output_path):
    output_path.write_text(
        "const scheduleData = "
        + json.dumps(schedule, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="시험감독 PDF를 schedule_data.js로 변환")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("schedule_data.js"))
    args = parser.parse_args()

    if not args.source.is_file():
        parser.error(f"PDF 원본을 찾지 못했습니다: {args.source}")

    schedule = build_schedule(args.source)
    write_schedule(schedule, args.output)
    total = sum(len(assignments) for assignments in schedule.values())
    print(f"OK: {len(schedule)}명, 총 {total}건 배정 -> {args.output}")


if __name__ == "__main__":
    main()
