from pydantic import BaseModel, Field
from datetime import datetime

# Schema para exibir dados básicos do usuário em uma avaliação
class UsuarioSimples(BaseModel):
    userName: str

    class ConfigDict:
        from_attributes = True # Equivalente ao antigo orm_mode = True

# Schema base, com os campos comuns
class AvaliacaoBase(BaseModel):
    nota: float = Field(..., ge=1, le=5) # Garante que a nota seja entre 1 e 5
    comentario: str | None = None

# Schema para criar uma nova avaliação (o que o app envia)
class AvaliacaoCreate(AvaliacaoBase):
    hotelId: int
    usuarioId: str

# Schema para exibir uma avaliação (o que a API retorna)
class Avaliacao(AvaliacaoBase):
    id: str  # <-- ALTERADO DE int PARA str
    dataCriacao: datetime
    usuario: UsuarioSimples # Aninha as informações do usuário

    class ConfigDict:
        from_attributes = True

# Schema para as estatísticas
class HotelStats(BaseModel):
    notaMedia: float | None = 0.0
    totalAvaliacoes: int = 0

    # app/schemas/avaliacao.py

# ... outros schemas ...

class Avaliacao(AvaliacaoBase):
    id: str
    dataCriacao: datetime # <-- Este campo já existe e é obrigatório
    hotelId: int          # <-- ADICIONE ESTE CAMPO
    usuario: UsuarioSimples

    class ConfigDict:
        from_attributes = True