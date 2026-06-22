from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "questions.json"


CONCEPT_RULES: list[tuple[tuple[str, ...], str]] = [
    (("remediation", "address vulnerabilities", "mitigate", "patch"), "การแก้ไขช่องโหว่หลังพบความเสี่ยง เช่น ปิดการเชื่อมต่อที่เป็นอันตราย อัปเดตระบบ หรือปรับคอนฟิกเพื่อลดผลกระทบ"),
    (("identification", "detect vulnerabilities"), "การค้นหาและระบุสินทรัพย์ ช่องโหว่ หรือเหตุการณ์ที่ต้องนำไปประเมินต่อ"),
    (("assessment", "risk assessment"), "การประเมินความรุนแรง โอกาสเกิด และผลกระทบของความเสี่ยงก่อนตัดสินใจแก้ไข"),
    (("scanning scope", "scope"), "การกำหนดขอบเขตว่าระบบหรือเครือข่ายใดจะถูกสแกน ไม่ใช่ขั้นตอนการแก้ไข"),
    (("sensor",), "อุปกรณ์หรือซอฟต์แวร์ที่ใช้ตรวจจับสัญญาณและวัดค่าทางกายภาพ เช่น อุณหภูมิ แรงดัน หรือการเคลื่อนไหว"),
    (("beacon",), "สัญญาณบอกตำแหน่งหรือสถานะที่ส่งเป็นช่วง ๆ ไม่ได้ทำหน้าที่วัดค่าทางกายภาพโดยตรง"),
    (("gateway",), "ตัวกลางที่เชื่อมเครือข่ายหรือโปรโตคอลเข้าด้วยกัน ไม่ใช่อุปกรณ์ตรวจวัดหลัก"),
    (("paas", "platform as a service"), "PaaS ให้แพลตฟอร์มสำหรับรันและ deploy โค้ด โดยผู้ใช้ไม่ต้องดูแลระบบปฏิบัติการ เซิร์ฟเวอร์ และ runtime พื้นฐานเอง"),
    (("iaas", "infrastructure as a service"), "IaaS ให้เครื่องเสมือน เครือข่าย และสตอเรจที่ผู้ใช้ควบคุมระบบปฏิบัติการและซอฟต์แวร์ได้มากกว่า PaaS/SaaS"),
    (("saas", "software as a service"), "SaaS คือแอปพลิเคชันสำเร็จรูปที่ผู้ให้บริการดูแลแพลตฟอร์มและแอปให้ ผู้ใช้เพียงเข้าใช้งานผ่านเครือข่าย"),
    (("faas", "function as a service", "serverless"), "FaaS ใช้รันฟังก์ชันตามเหตุการณ์ โดยผู้ให้บริการจัดการโครงสร้างพื้นฐานและการ scale ให้"),
    (("dbaas", "database as a service"), "DBaaS เป็นบริการฐานข้อมูลแบบ managed service ที่ลดงานดูแลแพตช์ สำรองข้อมูล และ availability ของฐานข้อมูล"),
    (("xaas", "anything as a service"), "XaaS เป็นคำกว้างสำหรับบริการแบบ as-a-service จึงมักไม่แม่นเท่าชื่อโมเดลบริการเฉพาะ"),
    (("network security group", "security group"), "network security group ใช้กำหนดกฎอนุญาตหรือปฏิเสธทราฟฟิกของ resource ตามพอร์ต โปรโตคอล และแหล่งที่มา"),
    (("waf", "web application firewall"), "WAF ป้องกันทราฟฟิกระดับเว็บแอป เช่น SQL injection หรือ XSS แต่ไม่ได้แทนการกำหนดสิทธิ์เครือข่ายทั่วไปเสมอไป"),
    (("mfa", "multi-factor"), "MFA เพิ่มปัจจัยยืนยันตัวตนเพื่อลดความเสี่ยงจากรหัสผ่านรั่ว แต่ไม่ได้กำหนดเส้นทางหรือกฎเครือข่าย"),
    (("ids", "ips", "intrusion"), "IDS/IPS ใช้ตรวจจับหรือบล็อกพฤติกรรมโจมตีบนเครือข่าย แต่ไม่ใช่เครื่องมือกำหนดสิทธิ์การเข้าถึงตามตำแหน่งหรือกลุ่มผู้ใช้โดยตรง"),
    (("acl", "access control list"), "ACL เป็นรายการกฎอนุญาต/ปฏิเสธการเข้าถึง เหมาะกับการคุมทราฟฟิกหรือสิทธิ์แบบระบุรายการ"),
    (("firewall",), "ไฟร์วอลล์ใช้ควบคุมทราฟฟิกตามกฎเครือข่าย เช่น IP พอร์ต หรือโปรโตคอล"),
    (("reserved", "reservation"), "reserved resources เหมาะกับ workload ที่ใช้ต่อเนื่อง เพราะแลก commitment ระยะยาวกับราคาที่ต่ำลง"),
    (("spot", "preemptible"), "spot instance ใช้ capacity ส่วนเกินราคาถูก เหมาะกับงานยืดหยุ่นและทนต่อการถูกยกเลิกได้"),
    (("pay-as-you-go", "pay as you go"), "pay-as-you-go จ่ายตามการใช้งานจริง จึงยืดหยุ่นแต่ไม่ใช่ตัวลดต้นทุนสูงสุดสำหรับงานคงที่เสมอไป"),
    (("dedicated host",), "dedicated host ให้เครื่องกายภาพเฉพาะลูกค้า เหมาะกับข้อกำหนด licensing หรือ isolation แต่มักมีต้นทุนสูงกว่า"),
    (("turn off", "shut down", "shutdown", "outside of business hours", "cron", "schedule"), "การตั้งเวลาปิด resource นอกเวลางานช่วยลดค่าใช้จ่าย เพราะ cloud คิดค่าบริการจากเวลาหรือปริมาณการใช้งาน"),
    (("pull request",), "pull request เป็นขั้นตอนเสนอและตรวจทานการเปลี่ยนแปลงก่อน merge เข้าสาขาหลัก ช่วยควบคุมคุณภาพโค้ด"),
    (("merge",), "merge รวมการเปลี่ยนแปลงจากสาขาหนึ่งเข้าสู่อีกสาขา หลังผ่านการตรวจทานแล้ว"),
    (("rebase",), "rebase นำ commit ไปวางทับบนฐานใหม่เพื่อจัดประวัติ commit ไม่ใช่กระบวนการขอ review โดยตรง"),
    (("branch",), "branch แยกเส้นทางพัฒนาโค้ดเพื่อให้เปลี่ยนแปลงได้โดยไม่กระทบสายหลัก"),
    (("git push", "push"), "git push ส่ง commit จากเครื่อง local ไปยัง remote repository"),
    (("versioning", "code versioning", "version control"), "versioning เก็บประวัติการเปลี่ยนแปลง ทำให้ย้อนกลับ ตรวจสอบ และทำงานร่วมกันได้"),
    (("drift", "drift detection"), "drift detection ตรวจจับความแตกต่างระหว่างสถานะจริงกับสถานะที่นิยามไว้ใน configuration หรือ infrastructure as code"),
    (("repeatability",), "repeatability คือความสามารถในการทำกระบวนการซ้ำแล้วได้ผลลัพธ์สม่ำเสมอ เหมาะกับ automation และ IaC"),
    (("configuration as code", "infrastructure as code", "terraform", "cloudformation"), "infrastructure/configuration as code ใช้ไฟล์กำหนด resource เพื่อ deploy ซ้ำ ตรวจทาน และควบคุมเวอร์ชันได้"),
    (("ansible",), "Ansible เป็นเครื่องมือ automation/configuration management ที่ใช้ playbook อธิบายสถานะที่ต้องการของระบบ"),
    (("ci/cd", "pipeline"), "CI/CD pipeline ทำให้การ build, test และ deploy เป็นอัตโนมัติ ลดความผิดพลาดจากงาน manual"),
    (("event-based scaling", "event trigger"), "event-based scaling ขยายระบบตามเหตุการณ์ เช่น queue หรือ message แต่ถ้าไม่ดู resource load อาจ scale ไม่ตรงกับภาระงานจริง"),
    (("load trigger", "resource load"), "load-based trigger ใช้ตัวชี้วัดอย่าง CPU, memory หรือ request rate เพื่อ scale ตามภาระงานจริง"),
    (("vertical scaling", "increase the vm size", "more cpu", "more ram"), "vertical scaling เพิ่มขนาด resource ของเครื่องเดิม เช่น CPU/RAM เหมาะเมื่อแอปยังต้องรันบน node เดียว"),
    (("horizontal scaling", "adding a load balancer", "additional instances", "scale out"), "horizontal scaling เพิ่มจำนวน instance และมักใช้ load balancer กระจายทราฟฟิกเพื่อรองรับผู้ใช้มากขึ้น"),
    (("autoscaling", "auto scaling"), "autoscaling ปรับจำนวน resource อัตโนมัติตาม policy หรือ metric ที่กำหนด"),
    (("load balancer",), "load balancer กระจาย request ไปหลาย instance เพิ่ม availability และรองรับโหลดได้ดีกว่าเครื่องเดียว"),
    (("cloud bursting",), "cloud bursting ใช้ public cloud รองรับโหลดส่วนเกินชั่วคราวจากระบบหลักเมื่อ demand พุ่งสูง"),
    (("edge", "retail store", "point-of-sale"), "edge computing ประมวลผลใกล้แหล่งข้อมูลเพื่อลด latency และลดการส่งข้อมูลกลับ cloud ส่วนกลาง"),
    (("public cloud",), "public cloud เป็น resource ของผู้ให้บริการที่แบ่งใช้กับหลายองค์กรและเข้าถึงผ่านเครือข่ายสาธารณะ"),
    (("private cloud",), "private cloud ใช้ resource เฉพาะองค์กรเดียว เหมาะกับข้อกำหนดควบคุมหรือ compliance สูง"),
    (("hybrid",), "hybrid cloud ผสาน on-premises/private cloud กับ public cloud เพื่อย้ายหรือกระจาย workload ได้"),
    (("community",), "community cloud ใช้ร่วมกันระหว่างองค์กรที่มีข้อกำหนดร่วม เช่น ภาคอุตสาหกรรมหรือหน่วยงานที่อยู่ภายใต้กฎเดียวกัน"),
    (("multi-cloud", "multicloud"), "multi-cloud ใช้บริการจากผู้ให้บริการ cloud มากกว่าหนึ่งรายเพื่อหลีกเลี่ยง vendor lock-in หรือเพิ่ม resilience"),
    (("object storage",), "object storage เก็บข้อมูลเป็น object พร้อม metadata เหมาะกับไฟล์จำนวนมาก static content และข้อมูล unstructured"),
    (("block storage",), "block storage ให้ volume ระดับ block เหมาะกับ VM และฐานข้อมูลที่ต้องการ latency ต่ำ"),
    (("file storage", "nas"), "file storage/NAS ให้ shared filesystem ผ่านโปรโตคอลไฟล์ เหมาะกับการแชร์ไฟล์ระหว่างระบบ"),
    (("san", "storage area network"), "SAN ให้ storage ระดับ block ผ่านเครือข่ายเฉพาะ มักใช้กับงานประสิทธิภาพสูง"),
    (("snapshot",), "snapshot บันทึกสถานะ point-in-time ของ volume หรือ VM เพื่อกู้คืนหรือ clone ได้รวดเร็ว"),
    (("backup", "restore"), "backup/restore ใช้สำรองข้อมูลและกู้คืนเมื่อข้อมูลเสียหายหรือระบบล่ม"),
    (("hot",), "hot site/storage พร้อมใช้งานเร็วที่สุด แต่มีต้นทุนสูงกว่าเพราะเตรียม resource ไว้ตลอด"),
    (("warm",), "warm site/storage เตรียมบางส่วนไว้แล้ว กู้คืนได้เร็วปานกลางและต้นทุนต่ำกว่า hot"),
    (("cold",), "cold site/storage มี resource น้อยหรือไม่มีล่วงหน้า ต้นทุนต่ำแต่ใช้เวลาฟื้นตัวนานกว่า"),
    (("archive", "retention"), "archive/retention เหมาะกับข้อมูลที่ต้องเก็บนาน เข้าถึงไม่บ่อย และต้องคุมอายุการเก็บตามนโยบาย"),
    (("iops", "ssd", "high-performance"), "IOPS/SSD เกี่ยวกับประสิทธิภาพดิสก์ เหมาะเมื่อปัญหาอยู่ที่ throughput หรือ latency ของ storage"),
    (("encryption at rest", "encrypt", "aes"), "การเข้ารหัสปกป้องข้อมูลด้วย key โดย AES เป็นอัลกอริทึม symmetric ที่ใช้แพร่หลายสำหรับข้อมูล at rest"),
    (("encryption in transit", "tls", "https"), "การเข้ารหัส in transit ปกป้องข้อมูลระหว่างส่งผ่านเครือข่าย เช่น TLS/HTTPS"),
    (("client id", "secret key", "api key", "secret"), "client ID และ secret key เป็น credential สำหรับแอปหรือ service account ใช้ยืนยันตัวตนกับ API"),
    (("rbac", "least privilege", "permissions", "privilege", "service account"), "การกำหนดสิทธิ์ควรยึด least privilege ให้สิทธิ์เท่าที่จำเป็นต่อบทบาทหรือ service เท่านั้น"),
    (("privilege escalation",), "privilege escalation คือการได้สิทธิ์สูงขึ้นกว่าที่ควร ทำให้ผู้โจมตีเข้าถึงระบบหรือข้อมูลได้มากขึ้น"),
    (("leaked credentials",), "leaked credentials คือรหัสผ่านหรือ secret รั่วไหล แต่ยังไม่จำเป็นต้องหมายถึงการยกระดับสิทธิ์สำเร็จ"),
    (("cryptojacking",), "cryptojacking คือการใช้ resource ของระบบไปขุด cryptocurrency โดยไม่ได้รับอนุญาต"),
    (("defaced",), "website defacement คือการเปลี่ยนหน้าเว็บเพื่อแสดงข้อความหรือภาพที่ผู้โจมตีต้องการ"),
    (("ddos",), "DDoS ทำให้บริการล่มหรือช้าด้วยทราฟฟิกจำนวนมากจากหลายแหล่ง"),
    (("sql injection",), "SQL injection แทรกคำสั่ง SQL ผ่าน input เพื่ออ่านหรือแก้ไขข้อมูลโดยไม่ได้รับอนุญาต"),
    (("cross-site scripting", "xss"), "XSS แทรกสคริปต์ให้รันใน browser ของผู้ใช้ เหมาะกับโจทย์ที่พูดถึง script ฝั่งเว็บ"),
    (("ransomware",), "ransomware เข้ารหัสหรือยึดข้อมูลเพื่อเรียกค่าไถ่ จึงต้องเน้น backup และ recovery"),
    (("cvss",), "CVSS เป็นระบบให้คะแนนความรุนแรงช่องโหว่เพื่อช่วยจัดลำดับการแก้ไข"),
    (("soc 2", "soc2"), "SOC 2 เป็นรายงานการควบคุมด้าน security, availability, processing integrity, confidentiality และ privacy ของผู้ให้บริการ"),
    (("log aggregation", "log collection", "logstash"), "log aggregation รวม log จากหลายระบบไว้ศูนย์กลาง เพื่อค้นหา วิเคราะห์ แจ้งเตือน และทำ troubleshooting ได้ง่ายขึ้น"),
    (("network flow", "flow log"), "network flow log แสดง metadata ของทราฟฟิก เช่น ต้นทาง ปลายทาง พอร์ต และปริมาณข้อมูล เหมาะกับวิเคราะห์การสื่อสารเครือข่าย"),
    (("dashboard", "graphs"), "dashboard/graph ใช้แสดงผล metric หรือ log หลังมีข้อมูลแล้ว แต่ไม่ใช่การรวบรวมข้อมูลตั้งต้น"),
    (("tracing",), "distributed tracing ใช้ติดตาม request ข้าม service เพื่อหาคอขวดหรือจุดผิดพลาดในระบบกระจาย"),
    (("monitoring", "observability", "alert"), "monitoring/observability เก็บ metric, log และ trace เพื่อมองเห็นสถานะระบบและแจ้งเตือนเมื่อผิดปกติ"),
    (("dns",), "DNS แปลงชื่อโดเมนเป็น IP และช่วยกำหนดเส้นทางการเข้าถึงบริการด้วย record ต่าง ๆ"),
    (("cdn",), "CDN กระจาย static content ไปใกล้ผู้ใช้เพื่อลด latency และลดโหลดที่ origin"),
    (("vpn",), "VPN สร้างอุโมงค์เข้ารหัสระหว่างเครือข่ายหรือผู้ใช้กับ cloud เพื่อเข้าถึง resource อย่างปลอดภัย"),
    (("vpc peering", "peering"), "VPC peering เชื่อม virtual network เข้าหากันแบบ private เพื่อให้ resource สื่อสารกันได้"),
    (("bgp",), "BGP ใช้แลกเปลี่ยน route ระหว่างเครือข่าย เหมาะกับการเชื่อมต่อหลายเครือข่ายหรือ hybrid connectivity"),
    (("route table", "routing"), "route table กำหนดเส้นทางว่า packet จะออกไปทาง gateway, peering หรือ next hop ใด"),
    (("nat",), "NAT ช่วยให้ private resource ออกอินเทอร์เน็ตได้โดยไม่ต้องมี public IP ตรง"),
    (("mqtt",), "MQTT เป็น protocol แบบ publish/subscribe ที่เบา เหมาะกับ IoT และอุปกรณ์ bandwidth ต่ำ"),
    (("websocket", "web socket"), "WebSocket เปิด connection สองทางแบบต่อเนื่อง เหมาะกับงาน real-time"),
    (("graphql",), "GraphQL ให้ client ระบุข้อมูลที่ต้องการได้ละเอียด ลดการรับข้อมูลเกินจำเป็นเมื่อเทียบกับ REST บางกรณี"),
    (("api throttling", "rate limiting"), "API throttling/rate limiting จำกัดจำนวน request เพื่อป้องกัน overload และควบคุมการใช้งาน API"),
    (("container image", "image registry", "private container", "repository"), "container image registry เก็บและแจกจ่าย image โดย private repository ต้องยืนยันสิทธิ์ก่อนเข้าถึง"),
    (("container",), "container แพ็กแอปพร้อม dependency ให้รันได้สม่ำเสมอบน environment ต่าง ๆ โดยใช้ kernel ร่วมกับ host"),
    (("cluster", "kubernetes"), "cluster คือกลุ่ม node ที่ทำงานร่วมกันเพื่อรัน workload เช่น container orchestration"),
    (("blue-green",), "blue-green deployment มี environment สองชุดและสลับทราฟฟิกไปชุดใหม่ ช่วย rollback ได้เร็ว"),
    (("canary",), "canary deployment ปล่อยเวอร์ชันใหม่ให้ผู้ใช้ส่วนน้อยก่อนเพื่อลดความเสี่ยง"),
    (("rolling",), "rolling deployment ค่อย ๆ แทนที่ instance เดิมด้วยเวอร์ชันใหม่โดยไม่หยุดระบบทั้งหมด"),
    (("in-place",), "in-place deployment อัปเดตบน environment เดิม จึงง่ายแต่ rollback และ downtime อาจเสี่ยงกว่า"),
    (("active-active",), "active-active ให้หลาย site หรือหลาย instance รับงานพร้อมกัน เพิ่ม availability และลด downtime"),
    (("active-passive",), "active-passive มีระบบสำรองรอรับงานเมื่อระบบหลักล่ม ต้นทุนต่ำกว่า active-active แต่ failover ช้ากว่า"),
    (("rto",), "RTO คือเวลาสูงสุดที่ยอมให้บริการหยุดได้ก่อนต้องกู้คืน"),
    (("rpo",), "RPO คือปริมาณข้อมูลหรือช่วงเวลาข้อมูลสูญหายสูงสุดที่ยอมรับได้"),
    (("regulatory", "regulations"), "ข้อกำหนด regulatory บังคับวิธีจัดเก็บ ประมวลผล หรือปกป้องข้อมูลตามกฎหมาย/อุตสาหกรรม"),
    (("contractual",), "ข้อผูกพัน contractual เกิดจากสัญญาหรือ SLA ที่องค์กรตกลงกับลูกค้าหรือผู้ให้บริการ"),
    (("availability", "highly available", "self-healing"), "high availability ออกแบบให้ระบบยังให้บริการได้เมื่อ component บางส่วนล้มเหลว โดยใช้ redundancy และ health checks"),
    (("cost-effective", "cost effective"), "cost-effective design เลือกบริการและขนาด resource ให้พอเหมาะ ลดต้นทุนที่ไม่จำเป็นโดยยังคงตอบ requirement"),
    (("text-to-voice", "text to speech", "speech"), "text-to-speech แปลงข้อความเป็นเสียงพูดด้วยบริการ AI/ML"),
    (("sentiment",), "sentiment analysis วิเคราะห์อารมณ์หรือทัศนคติจากข้อความ"),
    (("chat", "chatbot"), "chatbot ใช้ NLP/AI เพื่อตอบโต้กับผู้ใช้ในรูปแบบสนทนา"),
    (("three-tier", "3-tier"), "three-tier web application แยก presentation, application และ data tier ช่วยลดภาระดูแลเมื่อใช้ managed services ที่เหมาะสม"),
    (("health", "unsuccessful code", "status code"), "health check ใช้ตรวจสถานะแอปจากผลตอบกลับ เช่น HTTP status code แล้วสั่ง remediation อย่างหยุดหรือ restart VM เมื่อไม่ healthy"),
    (("volume storage size", "100gb", "storage size"), "สคริปต์จัดการ volume ต้องตรวจขนาดปัจจุบันก่อน แล้วค่อยเพิ่มขนาดเมื่อค่าต่ำกว่า threshold ที่กำหนด"),
    (("public-facing website", "static website"), "เว็บ public-facing ที่ต้องประหยัดและ available สูงมักใช้บริการ managed/static hosting, CDN, HTTPS และ health/self-healing แทนการดูแล VM เอง"),
]


SPECIAL_EXPLANATIONS = {
    "cloud_quiz01_q008": "เฉลยคือ Option A เพราะสคริปต์ที่ถูกต้องต้องตรวจขนาด volume ก่อน แล้วจึงสั่งขยายเฉพาะเมื่อขนาดต่ำกว่า 100GB เพื่อหลีกเลี่ยงการเปลี่ยน resource โดยไม่จำเป็น",
    "cloud_quiz05_q013": "เฉลยคือ Option A เพราะสคริปต์ health check ต้องอ่านผลตอบกลับของแอป เช่น HTTP status code แล้วหยุด VM เมื่อพบรหัสที่บอกว่าแอปทำงานไม่สำเร็จ",
    "cloud_quiz10_q007": "เฉลยคือ Option B เพราะโจทย์ต้องการ three-tier web application ที่ operational overhead ต่ำ จึงควรเลือก template ที่ใช้บริการ managed แยก web/app/data tier และลดงานดูแลเซิร์ฟเวอร์เอง",
    "cloud_quiz12_q005": "เฉลยคือ Option D เพราะ requirement ต้องการเว็บสาธารณะที่ประหยัด highly available self-healing และปลอดภัย จึงเหมาะกับ template ที่ใช้ managed/static hosting ร่วมกับ CDN/HTTPS และกลไกตรวจสุขภาพมากกว่า VM เดี่ยว",
}


SPECIAL_CHOICE_HINTS = {
    "cloud_quiz01_q008": "ให้เทียบ logic ในภาพว่า option ใดตรวจขนาด volume ก่อนและขยายเฉพาะเมื่อขนาดต่ำกว่า 100GB",
    "cloud_quiz05_q013": "ให้เทียบ logic ในภาพว่า option ใดตรวจ health/status code แล้วหยุด VM เมื่อได้ผลลัพธ์ไม่สำเร็จ",
    "cloud_quiz10_q007": "ให้เทียบ template ในภาพว่า option ใดลดงานดูแลด้วย managed services และยังแยก web/app/data tier ครบ",
    "cloud_quiz12_q005": "ให้เทียบ template ในภาพว่า option ใดรองรับเว็บ public-facing แบบประหยัด ทนทาน และปลอดภัยที่สุด",
}


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def concept_for(*parts: str) -> str:
    haystack = normalize(" ".join(part for part in parts if part))
    for patterns, explanation in CONCEPT_RULES:
        if any(pattern in haystack for pattern in patterns):
            return explanation
    return "ตัวเลือกนี้ตอบเงื่อนไขหลักของโจทย์ได้ตรงที่สุดเมื่อเทียบกับตัวเลือกอื่น โดยพิจารณาจากหน้าที่ของบริการ cloud, security, operations หรือ deployment ที่โจทย์ระบุ"


def split_correct_answers(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in re.split(r"\s*,\s*", text) if part.strip()]


def build_question_explanation(question: dict) -> str:
    if question["id"] in SPECIAL_EXPLANATIONS:
        return SPECIAL_EXPLANATIONS[question["id"]]

    correct_text = question.get("correctAnswerText") or ", ".join(question.get("correctAnswers", []))
    parts = split_correct_answers(correct_text)
    concept = concept_for(correct_text, question.get("prompt", ""))
    if len(parts) > 1:
        return f"เฉลยคือ {correct_text} เพราะตัวเลือกเหล่านี้ทำงานร่วมกันตรงกับเงื่อนไขของโจทย์: {concept}"
    return f"เฉลยคือ {correct_text} เพราะ {concept}"


def build_choice_explanation(question: dict, choice: dict) -> str:
    correct_labels = set(question.get("correctLabels") or [])
    correct_text = question.get("correctAnswerText") or ", ".join(question.get("correctAnswers", []))
    choice_text = choice.get("text") or f"Option {choice.get('label')}"
    is_correct = choice.get("label") in correct_labels

    if question["id"] in SPECIAL_CHOICE_HINTS:
        hint = SPECIAL_CHOICE_HINTS[question["id"]]
        if is_correct:
            return f"ถูก เพราะ option นี้ตรงกับเงื่อนไขสำคัญของโจทย์: {hint}"
        return f"ยังไม่เหมาะ เพราะ option นี้ขาดบางเงื่อนไขสำคัญเมื่อเทียบกับเฉลย ({correct_text}); {hint}"

    if is_correct:
        return f"ถูก เพราะ {concept_for(choice_text, correct_text, question.get('prompt', ''))}"

    wrong_concept = concept_for(choice_text)
    correct_concept = concept_for(correct_text, question.get("prompt", ""))
    return f"ยังไม่เหมาะ เพราะตัวเลือกนี้เกี่ยวกับ {wrong_concept} แต่โจทย์ต้องการ {correct_concept}"


def main() -> None:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    payload["answerSource"] = "Correct answers are OCR-extracted from the visible answer strips in the source PDFs; answer images are not displayed in the web app."
    payload["explanationSource"] = (
        "Thai helper explanations are generated from vendor-neutral Cloud+ concepts, including NIST cloud characteristics/service models, "
        "CompTIA Cloud+ domains, and major cloud provider documentation. They explain the concept; the answer key still follows the source PDFs."
    )
    payload["explanationReferences"] = [
        "https://csrc.nist.gov/pubs/sp/800/145/final",
        "https://www.comptia.org/en-us/certifications/cloud/",
        "https://www.ibm.com/think/topics/iaas-paas-saas",
        "https://cloud.google.com/learn/paas-vs-iaas-vs-saas",
    ]

    for question in payload["questions"]:
        question["explanation"] = build_question_explanation(question)
        question["choiceExplanations"] = {
            choice["label"]: build_choice_explanation(question, choice)
            for choice in question.get("choices", [])
        }

    DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(payload['questions'])} questions")


if __name__ == "__main__":
    main()
