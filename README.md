# CloudPlus Quiz Practice

เว็บฝึกทำข้อสอบ Cloud+ จากชุด PDF `cloud_quiz01` ถึง `cloud_quiz12` พร้อมระบบตรวจคำตอบและแสดงเฉลยจากไฟล์ต้นฉบับ

## เปิดใช้งาน

เข้าใช้งานเว็บได้ที่:

[https://sleepingsong.github.io/exam_test_cloudplus/](https://sleepingsong.github.io/exam_test_cloudplus/)

## ความสามารถหลัก

- รวมข้อสอบทั้งหมด 319 ข้อจากไฟล์ PDF ต้นฉบับ
- แสดงภาพคำถามที่ crop จาก PDF โดยตรง เหมาะกับข้อที่มีรูปภาพ ตาราง โค้ด หรือ layout พิเศษ
- ตรวจคำตอบได้ทันทีหลังเลือกตัวเลือก
- แสดงเฉลยเป็นข้อความ โดยอ้างอิงจากแถบเฉลยใน PDF ต้นฉบับ
- มีคำอธิบายตัวเลือกอื่นแบบสั้น ๆ ว่าทำไมไม่ใช่คำตอบที่ถูก
- เลือกชุดข้อสอบได้ตาม quiz
- ค้นหาข้อสอบด้วย keyword, คำตอบ หรือชื่อไฟล์ต้นทาง
- จำผลการทำข้อสอบไว้ใน browser ด้วย `localStorage`
- รองรับ Light Mode และ Dark Mode
- ใช้ฟอนต์ Sarabun สำหรับภาษาไทย และ Inter สำหรับภาษาอังกฤษ

## โครงสร้างโปรเจกต์

```text
.
├── index.html              # หน้าเว็บหลักสำหรับ GitHub Pages
├── styles.css              # สไตล์และธีม Light/Dark
├── app.js                  # logic ของเว็บฝึกทำข้อสอบ
├── data/
│   └── questions.json      # ฐานข้อมูลข้อสอบแบบ JSON
├── assets/
│   └── media/              # ภาพประกอบเฉพาะข้อที่ต้องใช้ภาพ
└── tools/
    └── build_quiz_data.py  # สคริปต์สร้าง JSON และภาพจาก PDF
```

## แหล่งข้อมูล

ข้อมูลข้อสอบถูกสร้างจากไฟล์ในโฟลเดอร์ `Question/`:

- ใช้เฉพาะ `cloud_quiz01.pdf` ถึง `cloud_quiz12.pdf`
- ไม่ใช้ `cloud_quiz_final.pdf`
- คำตอบที่ถูกต้องอ้างอิงจากแถบเฉลยใน PDF ต้นฉบับ

หมายเหตุ: โฟลเดอร์ `Question/` ไม่ถูก push ขึ้น GitHub เพราะเป็นไฟล์ต้นฉบับขนาดใหญ่และไม่จำเป็นต่อการเปิดเว็บ หลังจากสร้างข้อมูลแล้วเว็บใช้เพียง `data/` และ `assets/`

## การสร้างข้อมูลใหม่

หากมีการแก้ไขหรือเพิ่มไฟล์ PDF ต้นฉบับ สามารถ regenerate ข้อมูลได้ด้วยสคริปต์นี้:

```powershell
$py='C:\Users\prang\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py .\tools\build_quiz_data.py
```

ผลลัพธ์ที่ได้:

- `data/questions.json`
- `assets/media/*.png`

## การรันในเครื่อง

เปิด local server จากโฟลเดอร์โปรเจกต์:

```powershell
python -m http.server 8000
```

แล้วเปิด:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## การ deploy

โปรเจกต์นี้เป็น static site ทั้งหมด จึง deploy ผ่าน GitHub Pages ได้โดยตรงจาก branch `main`
