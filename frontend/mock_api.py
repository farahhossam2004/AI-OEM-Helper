
from fastapi import FastAPI

app = FastAPI()


@app.post("/api/v1/lookup")
def mock_lookup(payload: dict):
    return {
        "status": "found",
        "response": "تم العثور على أرقام OEM مرشحة للاستخدام.",
        "catalog_result": {
            "status": "found",
            "parts": [
                {
                    "oem_number": "MOCK-4243178010",
                    "description": "Front Brake Disc - Mock Result",
                    "verification_status": "catalog_candidate",
                },
                {
                    "oem_number": "MOCK-4351233150",
                    "description": "Brake Disc - Mock Result",
                    "verification_status": "catalog_candidate",
                },
            ],
        },
    }
