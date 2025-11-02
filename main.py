import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schemas import Idea, Plan
from database import create_document, get_documents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

# AI plan generation logic (simple deterministic draft)
def generate_plan(idea: str, industry: str, complexity: str) -> Plan:
    title = idea.strip() if idea.strip() else f"{industry} AI App"
    levels = {
        "سهل": ["واجهة بسيطة", "مصادقة أساسية", "صفحة واحدة أساسية"],
        "متوسط": ["لوحة إدارة", "تكامل API", "نظام صلاحيات"],
        "متقدم": ["بلوغينز", "زمن-حقيقي", "قابلية توسّع"],
    }

    pages = [
        "الصفحة الرئيسية",
        "التسجيل وتسجيل الدخول",
        "لوحة التحكم",
        "الملف الشخصي",
        "الإعدادات",
    ]

    features_base = [
        "منشئ نماذج سحب وإفلات",
        "توليد مكوّنات واجهة تلقائياً",
        "إنشاء مخطط قاعدة البيانات",
        "كتابة نقاط API تلقائية",
        "نشر بضغطة زر",
    ]

    stack = [
        "Frontend: React + Tailwind",
        "Backend: FastAPI",
        "Database: MongoDB",
        "Auth: JWT + OAuth",
        "CI/CD: GitHub Actions",
    ]

    extra = levels.get(complexity, levels["متوسط"])

    name = title if len(title) <= 40 else f"{title[:37]}..."
    pitch = (
        f"تطبيق {industry} يعتمد على الذكاء الاصطناعي لتحويل الأوامر النصية إلى واجهات، صفحات، ونقاط API كاملة، "
        f"مع نشر تلقائي وتهيئة للبنية التحتية."
    )

    return Plan(name=name, pitch=pitch, pages=pages, features=[*features_base, *extra], stack=stack)

@app.post("/api/plan", response_model=Plan)
def api_generate_plan(payload: dict):
    idea = payload.get("idea", ""); industry = payload.get("industry", "التقنية"); complexity = payload.get("complexity", "متوسط")
    return generate_plan(idea, industry, complexity)

@app.post("/api/ideas")
def create_idea(idea: Idea):
    try:
        inserted_id = create_document("idea", idea)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ideas", response_model=List[Idea])
def list_ideas(limit: int = 20):
    try:
        docs = get_documents("idea", limit=limit)
        # Remove Mongo-specific fields for response validation
        cleaned = []
        for d in docs:
            d.pop("_id", None)
            d.pop("created_at", None)
            d.pop("updated_at", None)
            cleaned.append(d)
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
