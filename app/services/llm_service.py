from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=settings.GEMINI_API_KEY,
        streaming=True
    )

def get_qa_prompt():
    template = """Bạn là trợ lý AI chuyên môn cao hỗ trợ người dùng sử dụng nền tảng RPA.
Hãy trả lời câu hỏi dựa TRÊN tài liệu ngữ cảnh được cung cấp.
Nếu không tìm thấy thông tin trong tài liệu, hãy nói: 'Tôi chưa có thông tin chính xác về vấn đề này trong tài liệu hiện tại'. Tuyệt đối không tự bịa ra các tính năng hoặc node không tồn tại.

Ngữ cảnh:
{context}

Lịch sử trò chuyện:
{chat_history}

Câu hỏi người dùng:
{question}

Câu trả lời của bạn:"""
    
    return PromptTemplate(
        template=template,
        input_variables=["context", "chat_history", "question"]
    )
