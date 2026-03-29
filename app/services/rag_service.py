import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationalRetrievalChain
except ImportError:
    from langchain_classic.memory import ConversationBufferMemory
    from langchain_classic.chains import ConversationalRetrievalChain
from app.services.llm_service import get_llm, get_qa_prompt
from app.core.config import settings

# Trỏ về database ở thư mục gốc (chroma_db)
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")

# Lưu state memory tạm trên RAM (Trong prod có thể đổi sang Redis)
session_memories = {}

class SafeGoogleEmbeddings(GoogleGenerativeAIEmbeddings):
    def embed_query(self, text: str) -> list[float]:
        print(f"\n--- [DEBUG] VĂN BẢN ĐƯỢC ĐEM ĐI TÌM KIẾM VECTOR: '{text}' ---\n")
        # Xử lý chuỗi rỗng
        if not text or not text.strip():
            print("--- [WARNING] AI TẠO RA CÂU HỎI RỖNG, GHI ĐÈ 'RPA' ĐỂ TRÁNH TRỤC TRẶC ---")
            text = "RPA"
            
        try:
            return super().embed_query(text)
        except Exception as e:
            # Bắt lỗi 500 từ Google khi text chứa chuỗi bị blacklist hoặc bị server reject
            print(f"--- [ERROR] GOOGLE API TỪ CHỐI CHUỖI NÀY VỚI MÃ LỖI: {e}. GHI ĐÈ BẰNG TỪ KHOÁ AN TOÀN 'RPA'. ---")
            return super().embed_query("RPA")

def get_retriever():
    embeddings = SafeGoogleEmbeddings(
        model="models/gemini-embedding-001", 
        google_api_key=settings.GEMINI_API_KEY
    )
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 3})

def get_memory(session_id: str):
    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    return session_memories[session_id]

from langchain_core.prompts import PromptTemplate

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
    "Dưới đây là lịch sử trò chuyện và một câu hỏi tiếp theo của người dùng.\n"
    "Nhiệm vụ của bạn là viết lại câu hỏi tiếp theo thành một câu hỏi độc lập, đầy đủ ngữ cảnh bằng tiếng Việt.\n"
    "Tuyệt đối KHÔNG trả lời câu hỏi, chỉ viết lại câu hỏi.\n\n"
    "Lịch sử:\n{chat_history}\n\n"
    "Câu hỏi tiếp theo: {question}\n\n"
    "Câu hỏi độc lập:"
)

def answer_question(question: str, session_id: str) -> str:
    llm = get_llm()
    retriever = get_retriever()
    memory = get_memory(session_id)
    
    # Lấy lịch sử từ biến 'chat_history' dạng chữ
    history_vars = memory.load_memory_variables({})
    chat_history = history_vars.get("chat_history", "")
    
    # Nếu có lịch sử dạng danh sách message, convert sang chữ
    if isinstance(chat_history, list):
        history_str = ""
        for msg in chat_history:
            role = "Human" if getattr(msg, "type", "") == "human" else "AI"
            history_str += f"{role}: {getattr(msg, 'content', str(msg))}\n"
        chat_history = history_str
    
    # 1. Condense Question (Viết lại câu hỏi nếu có lịch sử)
    if chat_history and chat_history.strip():
        prompt_val = CONDENSE_QUESTION_PROMPT.format(chat_history=chat_history, question=question)
        res = llm.invoke(prompt_val)
        standalone_question = res.content if hasattr(res, "content") else str(res)
    else:
        standalone_question = question
        
    print(f"\n--- [RAG NATIVE] STANDALONE QUESTION: '{standalone_question}' ---\n")
    
    # 2. Lấy tài liệu
    docs = retriever.invoke(standalone_question)
    context = "\n\n".join([d.page_content for d in docs])
    
    # Nếu context rỗng thì có thể set câu mặc định
    if not context.strip():
        context = "Xin lỗi, phần này Chatbot chưa được cập nhật, sẽ bổ sung trong thời gian tới"
        
    # 3. Đưa vào Model trả lời
    qa_prompt = get_qa_prompt()
    qa_prompt_val = qa_prompt.format(context=context, question=standalone_question, chat_history=chat_history)
    
    ans_res = llm.invoke(qa_prompt_val)
    answer = ans_res.content if hasattr(ans_res, "content") else str(ans_res)
    
    # Lưu vào memory cho các lượt hỏi sau
    memory.save_context({"question": question}, {"answer": answer})
    
    return answer
