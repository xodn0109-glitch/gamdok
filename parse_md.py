import re
import json

file_path = "0507 전국연합학력평가_감독배정표3학년.md"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

teacher_schedule = {}
classes = []
current_exam = ""

for line in lines:
    line = line.strip()
    if not line.startswith("|"):
        continue
    
    parts = [p.strip() for p in line.split("|")]
    # The split will have an empty string at parts[0] and parts[-1] due to the leading/trailing pipes
    if len(parts) < 4:
        continue
        
    parts = parts[1:-1] # Remove empty ends
    
    # Check if it's the header row
    if "3-1" in parts:
        classes = parts[3:]
        continue
    
    # Skip separator row
    if parts[0].startswith("---") or parts[1].startswith("---"):
        continue
        
    # Data row
    if parts[0]:
        current_exam = parts[0].replace("<br>", " ")
        
    time_text = parts[1]
    period_text = parts[2]
    
    if not time_text or time_text.startswith("08:00") or "쉬는" in time_text or "점심" in time_text:
        continue
        
    for i, cls_name in enumerate(classes):
        col_idx = 3 + i
        if col_idx < len(parts):
            teacher = parts[col_idx]
            if teacher and teacher.strip():
                if teacher not in teacher_schedule:
                    teacher_schedule[teacher] = []
                teacher_schedule[teacher].append({
                    "grade": "3학년",
                    "class": cls_name,
                    "exam": current_exam,
                    "time": time_text,
                    "period": period_text
                })

with open("schedule_data.js", "w", encoding="utf-8") as f:
    f.write("const scheduleData = " + json.dumps(teacher_schedule, ensure_ascii=False, indent=2) + ";")

print("Generated schedule_data.js")
