import os
import json
import shutil
from dotenv import load_dotenv

load_dotenv()

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

DOCS_DIR = os.path.join(os.path.dirname(__file__), "app", "data", "rpa_docs")
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

def load_documents_custom():
    documents = []
    
    if not os.path.exists(DOCS_DIR):
        print(f"Directory not found: {DOCS_DIR}")
        return documents

    for filename in os.listdir(DOCS_DIR):
        filepath = os.path.join(DOCS_DIR, filename)
        
        # Bỏ qua folder hoặc các file hệ thống
        if not os.path.isfile(filepath):
            continue

        # Xử lý file Markdown (.md)
        if filename.endswith(".md"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append(Document(page_content=text, metadata={"source": filename, "type": "markdown"}))
                print(f"✅ Loaded markdown file: {filename}")
                
        # Xử lý file JSON (.json)
        elif filename.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    # Nếu JSON là mảng (như file activitypackage.json của bạn)
                    if isinstance(data, list):
                        for item in data:
                            # Parse JSON object thành đoạn văn dễ hiểu cho AI Embedding
                            pkg_name = item.get("pkg", "Unknown Package")
                            template_id = item.get("templateId", "Unknown ID").replace('"', '')
                            desc = item.get("text", "")
                            keyword = item.get("keyword", "")
                            
                            content = f"Activity Package Name: {pkg_name}\n"
                            content += f"Template ID: {template_id}\n"
                            content += f"Description / Text: {desc}\n"
                            content += f"Keyword: {keyword}\n"
                            
                            req_args = item.get("requiredArgs", [])
                            if req_args:
                                args_details = [f"{arg.get('name')} (Type: {arg.get('type')})" for arg in req_args]
                                content += f"Required Arguments: {', '.join(args_details)}\n"
                            else:
                                content += "Required Arguments: None\n"
                                
                            documents.append(Document(
                                page_content=content, 
                                metadata={"source": filename, "templateId": template_id, "type": "activity_package"}
                            ))
                    print(f"✅ Loaded JSON file: {filename}")
                except Exception as e:
                    print(f"❌ Error parsing JSON {filename}: {e}")
                    
    return documents

def ingest_docs():
    print(f"Starting to load documents from {DOCS_DIR}...")
    documents = load_documents_custom()
    
    if not documents:
        print("No valid .md or .json documents found or loaded.")
        return

    print(f"Loaded {len(documents)} logic blocks/documents. Splitting text...")
    
    # Text splitter chỉ áp dụng chia nhỏ thêm cho các file markdown dài.
    # Các khối JSON nhỏ vốn đã được tạo riêng lẻ nên ít bị ảnh hưởng
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks. Creating embeddings and storing in Chroma Local DB...")
    
    if os.path.exists(DB_DIR):
        print("Clearing old database...")
        shutil.rmtree(DB_DIR)
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Store directly to local disk
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    vectorstore.persist()
    print("🚀 Ingestion complete. Vector DB saved to", DB_DIR)

if __name__ == "__main__":
    ingest_docs()
