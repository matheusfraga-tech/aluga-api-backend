from app.database.database import engine
from app.models import reserva 

def main():
    reserva.Base.metadata.create_all(bind=engine) 
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    main()