import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from app.services.rag_service import answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    session_id: str = "default_session"

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        async def generate_response():
            # Sử dụng run_in_executor để chạy hàm đồng bộ answer_question trong ThreadPool
            # Điều này giúp loại bỏ triệt để lỗi 500 khi dùng asyncio của thư viện Langchain
            loop = asyncio.get_event_loop()
            answer = await loop.run_in_executor(None, lambda: answer_question(request.question, request.session_id))
            
            # Giả lập streaming cho UX do ConversationalRetrievalChain cũ sẽ sync
            # Note: dùng LLM Chain LCEL trong tương lai để stream thực sự
            words = answer.split(" ")
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
                await asyncio.sleep(0.01) # Small delay for smooth streaming
                
        return StreamingResponse(generate_response(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
