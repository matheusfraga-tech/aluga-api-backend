# hotel_metrics_service.py
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.review import Review
from app.models.hotel import Hotel
from app.models.booking import Booking 

class HotelMetricsService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_and_update_metrics(self, hotel_id: int):
        
        # Calcular STARS (MÉTRICA DE QUALIDADE)
        avg_rating_result = self.db.query(func.avg(Review.rating)).filter(
            Review.hotel_id == hotel_id
        ).scalar()
        
        calculated_stars = 0.0
        if avg_rating_result is not None and avg_rating_result > 0:
            calculated_stars = round(avg_rating_result, 1)
            
        # Calcular POPULARIDADE (MÉTRICA DE ENGAGEMENT)
        
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        try:
            bookings_count = self.db.query(Booking).filter(
                and_(Booking.hotel_id == hotel_id, Booking.created_at >= thirty_days_ago)
            ).count()
        except Exception:
            bookings_count = 0 
        
        total_reviews = self.db.query(Review).filter(
            Review.hotel_id == hotel_id
        ).count() 
        
        stars_score = calculated_stars 
        
        # Fórmula: Popularity = (0.5 * Bookings_30d) + (0.3 * Total_Reviews) + (0.2 * Stars)
        popularity_score = round(
            (0.5 * bookings_count) + 
            (0.3 * total_reviews) + 
            (0.2 * stars_score), 
            1
        )
        
        # Atualizar o Hotel
        hotel_to_update = self.db.query(Hotel).filter(Hotel.id == hotel_id).first()
        
        if hotel_to_update:
            # Nota de arquitetura: em ambiente produtivo o ideal seria essa atualização ocorrer via job/batch para não onerar nenhum serviço.
            
            hotel_to_update.stars = calculated_stars
            hotel_to_update.popularity = popularity_score
            self.db.commit()

        return True