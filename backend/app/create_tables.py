from app.core.database import Base, engine
from app.models.user import User

print("Creating tables...")
Base.metadata.create_all(bind=engine)
