<div align="center">
  <h1>☁️ CloudPlus Quiz Practice</h1>
  <p><strong>แพลตฟอร์มฝึกทำข้อสอบ CompTIA Cloud+ แสนสะดวก ครบจบในที่เดียว</strong></p>
  
  [![Website](https://img.shields.io/badge/Website-Live-brightgreen?style=for-the-badge&logo=github)](https://sleepingsong.github.io/exam_test_cloudplus/)
  [![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://sleepingsong.github.io/exam_test_cloudplus/)
  [![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://sleepingsong.github.io/exam_test_cloudplus/)
  [![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://sleepingsong.github.io/exam_test_cloudplus/)
</div>

<br/>

เว็บฝึกทำข้อสอบ Cloud+ ที่ถูกสร้างขึ้นจากชุดไฟล์ PDF `cloud_quiz01` ถึง `cloud_quiz12` เพื่อเป็นเครื่องมือทบทวนความรู้ก่อนสอบ มาพร้อมกับระบบตรวจคำตอบทันที และคำอธิบายเฉลยที่เข้าใจง่าย

## 🚀 เริ่มต้นใช้งาน (Live Preview)

สามารถเข้าใช้งานเว็บได้ทันทีที่:  
🔗 **[https://sleepingsong.github.io/exam_test_cloudplus/](https://sleepingsong.github.io/exam_test_cloudplus/)**

---

## ✨ ความสามารถหลัก (Features)

- 📚 **ข้อสอบรวม 319 ข้อ**: นำมาจากไฟล์ PDF ต้นฉบับ พร้อมให้คุณฝึกฝน
- 🔀 **สุ่มคำถามและตัวเลือก (Shuffle)**: ตัวเลือกสุ่มลำดับได้แบบไม่จำเจ ช่วยลดความเคยชินกับตำแหน่งตัวเลือก
- 💡 **Tooltips คำศัพท์เฉพาะ**: ไฮไลท์คำศัพท์ยากหรือศัพท์เทคนิคในโจทย์ เมื่อชี้จะแสดงความหมายทันที!
- ⚡ **Auto-Submit & ตรวจคำตอบทันที**: แค่คลิกเลือกคำตอบ ระบบจะตรวจและแสดงผลเฉลยให้ทันที
- 🖼️ **รองรับรูปภาพ**: แสดงภาพที่ดึงจาก PDF โดยตรง สำหรับข้อที่ต้องดู Topology, Code หรือ Diagram
- 📝 **คำอธิบายตัวเลือก (Explanations)**: อธิบายเหตุผลของแต่ละตัวเลือก ไม่ใช่บอกแค่ว่าถูกหรือผิด
- 🌗 **Light/Dark Mode**: สลับธีมสว่างหรือมืดได้ตามใจชอบ โดยค่าเริ่มต้นคือ **Light Mode**
- 💾 **ระบบจดจำสถานะ**: จำผลการทำข้อสอบเก่าของคุณไว้ในเบราว์เซอร์ผ่าน `localStorage`

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

โปรเจกต์นี้เขียนด้วย **Vanilla HTML/CSS/JS** เพียว ๆ ไม่มี dependency ยุ่งยาก:

```text
.
├── index.html              # หน้าหลักของเว็บไซต์
├── styles.css              # ไฟล์ CSS รองรับ Light & Dark Theme อย่างสวยงาม
├── app.js                  # ไฟล์รวม Logic การทำงานของข้อสอบ การสุ่ม และ Tooltips
├── data/
│   └── questions.json      # ฐานข้อมูลข้อสอบทั้งหมดในรูปแบบ JSON
├── assets/
│   └── media/              # รูปภาพประกอบเฉพาะข้อที่ดึงมาจาก PDF
└── tools/
    └── build_quiz_data.py  # Python Script สำหรับสร้าง JSON และรูปภาพจากไฟล์ PDF
```

---

## ⚙️ การสร้างฐานข้อมูลใหม่ (Data Generation)

ข้อมูลในเว็บไซต์ถูกสร้างขึ้นจากไฟล์ในโฟลเดอร์ `Question/` แบบอัตโนมัติ (ไม่รวม `cloud_quiz_final.pdf`)  
*หมายเหตุ: โฟลเดอร์ Question/ ถูกละเว้นการ push ขึ้น GitHub เพื่อลดขนาด repository*

หากคุณแก้ไขหรือมีไฟล์ PDF ใหม่ ให้ทำการรันสคริปต์นี้เพื่ออัปเดตระบบข้อสอบ:

```powershell
# (ใช้ Python environment ของคุณ)
python .\tools\build_quiz_data.py
```

ผลลัพธ์ที่ได้คือไฟล์ `data/questions.json` และภาพในโฟลเดอร์ `assets/media/`

---

## 💻 การรันโปรเจกต์ในเครื่อง (Local Setup)

เปิด Local server ง่าย ๆ ได้ด้วย Python:

```powershell
python -m http.server 8000
```
จากนั้นเปิดเบราว์เซอร์ไปที่: 👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## ☁️ การ Deploy

โปรเจกต์นี้เป็น **Static Site** อย่างสมบูรณ์ จึงสามารถนำขึ้นโฮสต์ผ่าน **GitHub Pages** ได้โดยตรงจาก Branch `main` แบบไร้รอยต่อ

<div align="center">
  <br/>
  <p><i>สร้างมาเพื่อฝึกฝนและพิชิตใบรับรอง Cloud+ ไปด้วยกัน!</i> 🚀</p>
</div>
