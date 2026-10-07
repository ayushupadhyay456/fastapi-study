from fastapi import FastAPI, Header, Cookie,Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded  #pip install slowapi
from slowapi import _rate_limit_exceeded_handler


def get_api_key(request:Request):
    return request.headers.get("X-API-KEY") or request.client.host

limiter=Limiter(key_func=get_api_key)
app = FastAPI()

@app.get("/tracking")
def track_client(
    user_agent: str = Header(),         # Reads 'User-Agent' automatically
    session_id: str | None = Cookie(None) # Reads 'session_id' cookie
):
    return {"browser": user_agent, "session": session_id}

app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

@app.get("/tokens")
@limiter.limit("5/minute") 
async def get_date(request:Request):
    return {"status":"ok"}



