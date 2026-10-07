from fastapi import FastAPI, Header, Cookie

app = FastAPI()

@app.get("/tracking")
def track_client(
    user_agent: str = Header(),         # Reads 'User-Agent' automatically
    session_id: str | None = Cookie(None) # Reads 'session_id' cookie
):
    return {"browser": user_agent, "session": session_id}