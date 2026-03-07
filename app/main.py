from fastapi import FastAPI

app = FastAPI()


@app.get("/test/{path}")
async def root(path):
    return {"You are at path": path}
