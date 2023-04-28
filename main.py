import __fast_api__
import uvicorn

app = __fast_api__.app
uvicorn.run(app, host="0.0.0.0", port=8080)
