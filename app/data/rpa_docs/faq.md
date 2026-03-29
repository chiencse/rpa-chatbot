1. Tổng quan hệ thống
❓ RPA system là gì?

RPA (Robotic Process Automation) là hệ thống tự động hóa quy trình nghiệp vụ bằng cách sử dụng robot phần mềm để thực hiện các tác vụ lặp lại, rule-based và có tương tác với hệ thống khác.

Trong hệ thống này:

User thiết kế workflow bằng BPMN
AI hỗ trợ sinh workflow từ mô tả tự nhiên
Robot thực thi workflow trên hạ tầng cloud
❓ Hệ thống RPA gồm những thành phần nào?

Hệ thống gồm 4 thành phần chính:

AI-assisted Module
Sinh BPMN từ text
Gợi ý automation
Studio
Thiết kế workflow
Config robot
Orchestrator
Deploy & điều phối robot
Monitor & logging
Robot Infrastructure
Môi trường chạy robot (VM riêng)
❓ Workflow hoạt động của hệ thống là gì?
User input → AI generate BPMN → User chỉnh sửa → Generate code → Deploy → Run → Monitor
2. AI & Process Generation
❓ Làm sao để tạo workflow bằng AI?

User chỉ cần nhập mô tả quy trình bằng ngôn ngữ tự nhiên.

Ví dụ:

"Lấy file từ Google Drive → xử lý → upload lên Moodle"

Hệ thống sẽ:

Phân tích input
Sinh BPMN dạng JSON
Convert sang BPMN XML
Hiển thị cho user chỉnh sửa
❓ AI sinh BPMN như thế nào?

Pipeline:

Normalize input
Generate JSON BPMN
Validate
Convert → XML
Visualize
Feedback loop
❓ Tại sao dùng JSON thay vì BPMN XML?
Tránh lỗi syntax XML
Dễ validate
Dễ chỉnh sửa
Là intermediate layer trước khi convert sang XML
❓ AI chọn activity (automation action) như thế nào?

Dựa trên scoring:

S = 0.6 * semantic similarity
  + 0.3 * lexical similarity
  + 0.1 * rule-based score
Top-5 candidates được chọn
LLM quyết định activity phù hợp
User có thể override
❓ Có cần user kiểm tra AI output không?

Có. Hệ thống dùng human-in-the-loop:

User phải:
approve
chỉnh sửa
reject nếu sai
3. Studio (Thiết kế workflow)
❓ Studio dùng để làm gì?
Thiết kế BPMN workflow
Mapping activity
Config tham số
Generate robot code
❓ Có những cách nào để tạo workflow?

2 cách:

1. Manual
Drag & drop BPMN
Tự define logic
2. AI-generated
Nhập mô tả
AI sinh BPMN
User refine
❓ Làm sao để cấu hình task?
Double-click vào task
Mở property panel
Config:
input/output
biến
connection
parameters
❓ Variables dùng để làm gì?
Lưu dữ liệu trung gian
Truyền giữa các bước
Input/output cho activity
❓ Làm sao generate robot code?
Sau khi hoàn thành BPMN
Click generate
System:
parse BPMN
build execution code
attach dependencies
4. BPMN & Workflow Design
❓ BPMN là gì?

BPMN (Business Process Model and Notation) là chuẩn để mô hình hóa quy trình.

❓ Quy tắc thiết kế BPMN là gì?
Phải có:
Start Event
End Event
Gateway phải join lại
Không loop trực tiếp
Loop phải dùng subprocess
❓ Subprocess là gì?
Nhóm các task lại thành 1 block
Có Start + End riêng
Dùng cho:
loop
modularization
❓ Task types gồm những gì?
Undefined task: placeholder
Automated task: có activity
Manual task: không automation
5. Orchestrator (Điều phối robot)
❓ Orchestrator là gì?

Là thành phần quản lý robot:

Deploy
Schedule
Monitor
Logging
Resource allocation
❓ Deploy robot như thế nào?

Flow:

Robot code → Package → Allocate VM → Setup env → Run
❓ Robot được chạy ở đâu?
Trên VM riêng (EC2)
Mỗi robot 1 environment độc lập
❓ Có thể schedule robot không?

Có:

Manual run
Schedule theo thời gian
Trigger theo event
❓ Làm sao monitor robot?
Dashboard
Log streaming
Execution status
6. Execution & Runtime
❓ Robot chạy như thế nào?
Start → Load config → Execute BPMN → Call APIs → Output → Log
❓ Robot có retry khi lỗi không?
Có detect lỗi
Log lại
User chỉnh sửa workflow
❓ Robot có chạy song song không?

Có, vì:

Mỗi robot chạy trên VM riêng
Không conflict resource
7. Activity Packages
❓ Activity package là gì?

Là tập các action robot có thể thực hiện.

❓ Hệ thống hỗ trợ những package nào?
Google
Drive
Sheets
Gmail
Classroom
Moodle
Course
Quiz
Automation
Browser automation
Desktop automation
❓ Activity mapping là gì?
Gán BPMN node → action cụ thể
Ví dụ:
"Upload file" → Google Drive API
8. Storage & Data
❓ Dữ liệu được lưu ở đâu?
MySQL → main data
DynamoDB → robot status
MongoDB → process design
S3:
robot code
user files
❓ Log được lưu như thế nào?
Streaming từ robot
Lưu centralized
Dùng cho monitoring & debugging
9. System Architecture
❓ Backend dùng gì?
NestJS
NGINX (reverse proxy)
❓ AI system dùng gì?
Python service
LangGraph pipeline
LLM
Vector DB
❓ Event system hoạt động ra sao?
EventBridge → trigger event
Lambda → xử lý:
deploy
test
monitoring
10. Use Cases
❓ Những task nào phù hợp RPA?
Lặp lại nhiều
Có rule rõ ràng
Tương tác hệ thống
Khối lượng lớn
❓ Ví dụ use case?
Auto grading
Convert file
Data entry
Upload/download file
11. Troubleshooting
❓ Tại sao robot không chạy?
Chưa deploy
Sai config
Thiếu dependency
❓ Tại sao workflow sai?
BPMN sai logic
Activity mapping sai
Variable config sai
❓ Làm sao debug?
Check log
Check dashboard
Test từng subprocess
12. AI Chatbot Intent Mapping
❓ Các intent phổ biến
create process
design workflow
deploy robot
run robot
monitor robot
debug robot