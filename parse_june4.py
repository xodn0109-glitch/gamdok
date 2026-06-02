"""6월 4일 전국연합학력평가 감독배정표(마크다운 HTML 표) → schedule_data.js 생성.

전학년(1,2,3학년) 동시시험. 각 학년 표의 셀에서 (교사 -> 감독 배정) 매핑을 만든다.
exam 열은 rowspan 으로 병합되어 있어 상태로 추적한다.
"""
import json
import re

SRC = "6월_4일목_전국연합학력평가_감독배정표_0602수정.md"
OUT = "schedule_data.js"

with open(SRC, encoding="utf-8") as f:
    content = f.read()


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


teacher_schedule = {}


def process_grade(grade_name, table_html):
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
                    "period": period_text,
                })


# 마크다운에서 학년별 표 추출
for grade in ["1학년", "2학년", "3학년"]:
    m = re.search(r"## " + grade + r".*?(<table>.*?</table>)", content, flags=re.S)
    process_grade(grade, m.group(1))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("const scheduleData = " + json.dumps(teacher_schedule, ensure_ascii=False, indent=2) + ";")

total = sum(len(v) for v in teacher_schedule.values())
print(f"OK: {len(teacher_schedule)}명, 총 {total}건 배정 -> {OUT}")
