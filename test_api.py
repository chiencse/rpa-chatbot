import requests
import uuid

def chat_cli():
    url = "http://127.0.0.1:8000/api/v1/chat"
    # Tạo session id ngẫu nhiên để lưu context riêng biệt cho mỗi lần chạy CLI
    session_id = f"cli_user_{uuid.uuid4().hex[:6]}"
    
    print("="*60)
    print("🤖 RPA Copilot CLI Tester")
    print(f"🆔 Session ID hiện tại: {session_id}")
    print("💡 Nhập 'exit' hoặc 'quit' để thoát chương trình.")
    print("="*60)

    while True:
        try:
            question = input("\n👤 Bạn: ")
            
            # Lệnh thoát
            if question.strip().lower() in ['exit', 'quit']:
                print("👋 Tạm biệt!")
                break
                
            if not question.strip():
                continue

            payload = {
                "question": question,
                "session_id": session_id
            }
            
            print("🤖 Bot: ", end="", flush=True)
            
            # Gửi request và stream kết quả
            with requests.post(url, json=payload, stream=True) as r:
                if r.status_code == 200:
                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        if chunk:
                            print(chunk, end="", flush=True)
                    print() # Xuống dòng sau khi stream xong
                else:
                    print(f"\n[Lỗi server - Mã {r.status_code}]: {r.text}")
                    
        except KeyboardInterrupt:
            # Xử lý khi người dùng ấn Ctrl+C
            print("\n👋 Đã huỷ phiên chat. Tạm biệt!")
            break
        except requests.exceptions.ConnectionError:
            print("\n⚠️ Không thể kết nối đến server. Hãy chắc chắn rằng bạn đang bật 'uvicorn main:app --reload'.")
            break
        except Exception as e:
            print(f"\n⚠️ Lỗi không xác định: {e}")

if __name__ == "__main__":
    chat_cli()
