import uvicorn

from app.config import settings
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.agent_port,
                access_log=False, log_level="warning")
