"""시험감독 기준 Markdown의 HTML 표를 웹앱 데이터로 변환한다.

각 학년 표의 시험명 셀은 ``rowspan``으로 병합되어 있어 상태로 추적한다.
원본의 시간표 참고 문구는 보존하되, 교사에게 보이는 ``period`` 값은 실제
감독 구분(예: ``7교시(62분)`` 또는 ``부담임(33분)``)만 사용한다.
"""
import argparse
import json
import re
from pathlib import Path

DEFAULT_SOURCE = Path("6월_4일목_전국연합학력평가_감독배정표_0602최종수정.md")
DEFAULT_OUTPUT = Path("schedule_data.js")


def parse_cells(tr_html):
    """<tr> 안의 td/th 셀을 (텍스트, rowspan) 리스트로 반환."""
    cells = []
    for m in re.finditer(r"<t[dh]([^>]*)>(.*?)</t[dh]>", tr_html, flags=re.S):
        attrs, inner = m.group(1), m.group(2)
        rs = re.search(r'rowspan="(\d+)"', attrs)
        rowspan = int(rs.group(1)) if rs else 1
        text = re.sub(r"<br\s*/?>", " ", inner)
        text = re.sub(r"\s+", " ", text).strip()
        cells.append((text, rowspan))
    return cells


def split_teachers(cell_text):
    """한 셀에 두 명(주/부감독)이 있을 수 있어 공백으로 분리."""
    return [t for t in cell_text.split() if t]


def normalize_period(period_text):
    """화면에 표시할 감독 구분만 반환한다.

    Markdown 표에는 수업 시정 관련 메모가 줄바꿈 뒤에 이어질 수 있다. 이 메모는
    감독 배정의 시간·장소·시험 정보를 바꾸지 않으므로, 첫 감독 구분만 노출한다.
    """
    match = re.search(r"(?:\d+교시|부담임)\s*\(\s*\d+분\s*\)", period_text)
    if not match:
        return period_text
    return re.sub(r"\s+", "", match.group(0))


def process_grade(grade_name, table_html, teacher_schedule):
    rows = re.findall(r"<tr>(.*?)</tr>", table_html, flags=re.S)
    header = parse_cells(rows[0])
    # header: [전국연합시정표, 학교시정표, (빈칸), class1, class2, ...]
    class_names = [c[0] for c in header[3:]]

    exam_remaining = 0
    current_exam = ""
    for tr in rows[1:]:
        cells = parse_cells(tr)
        if not cells:
            continue
        if exam_remaining > 0:
            exam = current_exam
            time_text, period_text = cells[0][0], cells[1][0]
            class_vals = cells[3:]  # [time, period, 빈칸, classes...]
            exam_remaining -= 1
        else:
            current_exam = cells[0][0]
            exam_remaining = cells[0][1] - 1
            exam = current_exam
            time_text, period_text = cells[1][0], cells[2][0]
            class_vals = cells[4:]  # [exam, time, period, 빈칸, classes...]

        # 교시 시간이 아닌 행(담임/쉬는시간/점심)은 건너뜀.
        # 시간칸에 "영어듣기방송 13:07~13:35" 같은 주석이 붙어도 앞쪽 시간만 추출.
        tmatch = re.match(r"^(\d{2}:\d{2}~\d{2}:\d{2})", time_text)
        if not tmatch:
            continue
        time_clean = tmatch.group(1)

        for cls_name, cell in zip(class_names, class_vals):
            for teacher in split_teachers(cell[0]):
                teacher_schedule.setdefault(teacher, []).append({
                    "grade": grade_name,
                    "class": cls_name,
                    "exam": exam,
                    "time": time_clean,
                    "period": normalize_period(period_text),
                })


def build_schedule(content):
    """기준 Markdown 전체에서 교사별 감독 배정을 만든다."""
    teacher_schedule = {}
    for grade in ["1학년", "2학년", "3학년"]:
        match = re.search(
            rf"## {re.escape(grade)}.*?(<table>.*?</table>)", content, flags=re.S
        )
        if not match:
            raise ValueError(f"{grade} HTML 표를 찾지 못했습니다.")
        process_grade(grade, match.group(1), teacher_schedule)
    return teacher_schedule


def write_schedule(teacher_schedule, output_path):
    output_path.write_text(
        "const scheduleData = "
        + json.dumps(teacher_schedule, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="시험감독 Markdown을 schedule_data.js로 변환")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.source.is_file():
        parser.error(f"기준 원본을 찾지 못했습니다: {args.source}")

    teacher_schedule = build_schedule(args.source.read_text(encoding="utf-8"))
    write_schedule(teacher_schedule, args.output)

    total = sum(len(schedules) for schedules in teacher_schedule.values())
    print(f"OK: {len(teacher_schedule)}명, 총 {total}건 배정 -> {args.output}")


if __name__ == "__main__":
    main()
