"""
Test script to verify data loading
سكريبت لاختبار تحميل البيانات
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent / "Data"

print("=" * 60)
print("🧪 اختبار تحميل البيانات | Data Loading Test")
print("=" * 60)

if not DATA_DIR.exists():
    print(f"❌ مجلد Data غير موجود: {DATA_DIR}")
    exit(1)

print(f"\n📂 مجلد البيانات: {DATA_DIR}\n")

total_students = 0

for file_path in sorted(DATA_DIR.glob("*.txt")):
    try:
        print(f"📄 {file_path.name}")
        students_count = 0
        locations = set()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row and 'كود الطالب' in row:
                    students_count += 1
                    if 'مكان الامتحان' in row:
                        locations.add(row['مكان الامتحان'])
        
        if students_count > 0:
            print(f"   ✅ عدد الطلاب: {students_count}")
            print(f"   📍 الأماكن: {', '.join(sorted(locations))}")
            total_students += students_count
        else:
            print(f"   ⚠️  لم يتم العثور على بيانات")
    
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

print("\n" + "=" * 60)
print(f"✅ إجمالي الطلاب: {total_students}")
print(f"✅ عدد المواد: {len(list(DATA_DIR.glob('*.txt')))}")
print("=" * 60)

if total_students > 0:
    print("\n✨ البيانات جاهزة للاستخدام!")
    print("اكتب: python bot.py")
else:
    print("\n⚠️  لم يتم العثور على بيانات. تأكد من ملفات Data")
