from datetime import datetime
from app.database.database import SessionLocal
from app.database.models import Hotel, Quarto, Reserva

def main():
    db = SessionLocal()
    try:
        #Hotel
        hotel_nome = "Hotel Teste"
        hotel = db.query(Hotel).filter_by(nome=hotel_nome).first()
        if not hotel:
            hotel = Hotel(nome=hotel_nome)
            db.add(hotel)
            db.commit()
            db.refresh(hotel)

        #Quarto 
        quarto_numero = "101"
        quarto = (
            db.query(Quarto)
            .filter_by(numero=quarto_numero, hotel_id=hotel.id)
            .first()
        )
        if not quarto:
            quarto = Quarto(numero=quarto_numero, hotel_id=hotel.id)
            db.add(quarto)
            db.commit()
            db.refresh(quarto)

        #Reserva de exemplo
        data_checkin = datetime(2025, 9, 25, 14, 0)
        data_checkout = datetime(2025, 9, 27, 12, 0)
        reserva = (
            db.query(Reserva)
            .filter_by(quarto_id=quarto.id, data_checkin=data_checkin)
            .first()
        )
        if not reserva:            
            reserva = Reserva(
                quarto_id=quarto.id,
                cliente="Victor Teste",
                data_checkin=data_checkin,
                data_checkout=data_checkout
            )
            db.add(reserva)
            db.commit()
            db.refresh(reserva)

        print("Banco populado com sucesso!")
    except Exception as e:
        db.rollback()
        print("Erro ao popular banco:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
