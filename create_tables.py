from database import engine, Base
from db_models import User

Base.metadata.create_all(bind=engine)

print("Tables created successfully")