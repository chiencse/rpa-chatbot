from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import langchain
import logging

from app.api.chat import router as chat_router

# 🚀 Bật cờ debug toàn cục để thấy RÕ RÀNG mọi chữ, mọi text được nhồi vào model
langchain.debug = True

# Basic logging cho tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(title="RPA Copilot API", version="1.0.0")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "RPA Copilot API is running"}
