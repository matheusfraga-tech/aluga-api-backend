from app.database import Base, engine
from app.models.user import User  # Must import the model so SQLAlchemy sees it

Base.metadata.create_all(bind=engine)

print("Tables created.")