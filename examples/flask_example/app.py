
from flask import Flask
from motor.motor_asyncio import AsyncIOMotorClient

from monglo import MongloEngine
from monglo.adapters.flask import create_flask_blueprint
from monglo.ui_helpers.flask import create_ui_blueprint

# ============= APPLICATION CODE =============

# 1. Setup MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_demo

# 2. Create Flask app
app = Flask(__name__)

# 3. Initialize Monglo
engine = MongloEngine(database=db, auto_discover=True)

@app.before_serving
async def startup():
    await engine.initialize()
    
    # Mount API routes
    api_bp = create_flask_blueprint(engine, url_prefix="/api/admin")
    app.register_blueprint(api_bp)
    
    # Mount UI routes - LIBRARY HANDLES EVERYTHING!
    ui_bp = create_ui_blueprint(engine, url_prefix="/admin")
    app.register_blueprint(ui_bp)
    
    print("\n" + "="*60)
    print("✅ Monglo Admin Ready!")
    print("="*60)
    print(f"📊 Discovered {len(engine.registry._collections)} collections")
    print(f"🌐 Admin UI:  http://localhost:5000/admin")
    print(f"📡 API:      http://localhost:5000/api/admin")
    print("="*60 + "\n")

# ============= That's it! =============

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
