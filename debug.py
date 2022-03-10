import uvicorn

# Importing app here makes the syntax cleaner as it will be picked up by refactors
from main import app

if __name__ == "__main__":
    uvicorn.run(
            "debug:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            ssl_keyfile="/home/ec2-user/keys/privkey.pem",
            ssl_certfile="/home/ec2-user/keys/fullchain.pem"
            )
