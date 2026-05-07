import json
import re

# Load JS data
with open('schedule_data.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

json_str = re.search(r'const scheduleData = (\{.*?\});', js_content, re.DOTALL).group(1)
js_data = json.loads(json_str)

print("Starting full data validation...")
issues_found = 0

for teacher, schedules in js_data.items():
    for s in schedules:
        period = s['period']
        exam = s['exam']
        time_text = s['time']
        
        # Check for weird keywords in period
        if "요일" in period or "월" in period or "화" in period or "수" in period or "목" in period or "금" in period:
            if "교시" not in period:
                print(f"ANOMALY in period for {teacher}: {period}")
                issues_found += 1
            if "요일" in period:
                print(f"ANOMALY in period for {teacher}: {period} (contains 요일)")
                issues_found += 1
                
        # Check if period doesn't have "교시"
        if "교시" not in period:
            print(f"WARNING: period missing '교시' for {teacher}: {period}")
            issues_found += 1
            
        # Check exam text
        if not exam.strip():
            print(f"WARNING: Empty exam text for {teacher}")
            issues_found += 1
            
        # Check time text
        if not time_text.strip():
            print(f"WARNING: Empty time text for {teacher}")
            issues_found += 1

print(f"\nValidation complete. Total issues found: {issues_found}")
