import json
import re

# Load raw JSON extracted from PDF
with open('extracted_tables.json', 'r', encoding='utf-8') as f:
    raw_tables = json.load(f)

# Load JS data
with open('schedule_data.js', 'r', encoding='utf-8') as f:
    js_content = f.read()
    
# Extract JSON from JS using regex
json_str = re.search(r'const scheduleData = (\{.*?\});', js_content, re.DOTALL).group(1)
js_data = json.loads(json_str)

# Count total assignments in JS data
total_js_assignments = 0
for teacher, schedules in js_data.items():
    # Only count actual teacher assignments, not the "1-1" style headers
    if not bool(re.match(r'\d+-\d+', teacher)):
        total_js_assignments += len(schedules)

print(f"Total teacher assignments in Web App Data: {total_js_assignments}")

# Let's count total valid teacher cells in the original raw tables
total_raw_assignments = 0

def process_table(table):
    global total_raw_assignments
    if not table or len(table) < 2: return
    
    headers = table[0]
    class_indices = [i for i, h in enumerate(headers) if h and "-" in h]
    
    for row in table:
        if not row: continue
        time_text = row[1] if len(row) > 1 and row[1] else ""
        
        # Skip header rows
        if not time_text or time_text.startswith("08:00") or "쉬는" in time_text or "점심" in time_text or "듣기방송" in time_text:
            # wait, '듣기방송' row actually contains teachers for 4교시 13:10~14:20
            if "듣기방송" not in time_text:
                continue
                
        for idx in class_indices:
            if idx < len(row):
                teacher = row[idx]
                if teacher and teacher.strip() and not bool(re.match(r'\d+-\d+', teacher)):
                    total_raw_assignments += 1

process_table(raw_tables[1]) # 1학년
process_table(raw_tables[3]) # 2학년
process_table(raw_tables[5]) # 3학년

print(f"Total teacher assignments found in raw PDF tables: {total_raw_assignments}")

if total_js_assignments == total_raw_assignments:
    print("SUCCESS: Count of assignments matches perfectly.")
else:
    print("WARNING: Discrepancy detected!")
    
# Let's check a specific teacher to be sure
sample_teacher = "김태완"
print(f"\nChecking sample teacher: {sample_teacher}")
if sample_teacher in js_data:
    for s in js_data[sample_teacher]:
        print(f"  - {s['grade']} {s['class']} | {s['exam']} | {s['time']}")
else:
    print("Teacher not found!")
