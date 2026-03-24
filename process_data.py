import json
import re

with open("extracted_tables.json", "r", encoding="utf-8") as f:
    tables = json.load(f)

# tables[0] is 1학년 title, tables[1] is 1학년 data
# tables[2] is 2학년 title, tables[3] is 2학년 data
# tables[4] is 3학년 title, tables[5] is 3학년 data

teacher_schedule = {}

def process_grade_data(grade_name, data_table):
    # Row 0 contains class names
    headers = data_table[0]
    classes = []
    class_indices = []
    for i, h in enumerate(headers):
        if h and "-" in h:
            classes.append(h)
            class_indices.append(i)
            
    current_exam = ""
    for row in data_table:
        if not row: continue
        
        # Exam name might be in col 0
        if row[0] and row[0].strip():
            current_exam = row[0].strip().replace('\n', ' ')
            
        time_text = row[1].strip() if row[1] else ""
        period_text = row[2].strip() if row[2] else ""
        
        if not time_text or time_text.startswith("08:00") or "쉬는" in time_text or "점심" in time_text:
            continue
            
        if "월요일 4교시" in period_text:
            period_text = period_text.replace("월요일 4교시\n(62분)", "7교시(62분)").replace("월요일 4교시 (62분)", "7교시(62분)")
            
        for cls_name, cls_idx in zip(classes, class_indices):
            if cls_idx < len(row):
                teacher = row[cls_idx]
                # Filter out empty values and class name references like "1-1"
                if teacher and teacher.strip() and not re.match(r'^\d+-\d+$', teacher.strip()):
                    teacher = teacher.strip()
                    if teacher not in teacher_schedule:
                        teacher_schedule[teacher] = []
                    teacher_schedule[teacher].append({
                        "grade": grade_name,
                        "class": cls_name,
                        "exam": current_exam,
                        "time": time_text.replace('\n', ' '),
                        "period": period_text.replace('\n', ' ')
                    })

process_grade_data("1학년", tables[1])
process_grade_data("2학년", tables[3])
process_grade_data("3학년", tables[5])

with open("schedule_data.js", "w", encoding="utf-8") as f:
    f.write("const scheduleData = " + json.dumps(teacher_schedule, ensure_ascii=False, indent=2) + ";")

print("Successfully generated schedule_data.js")
