from app.database.database import Base, engine
from app.database.models import User  # importa o modelo, sem circularidade

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")