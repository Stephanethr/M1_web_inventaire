from fastapi import FastAPI

# /d:/Documents D/M1/DeveloppementWeb/fastAPI/M1_web_inventaire/api/init.py


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}