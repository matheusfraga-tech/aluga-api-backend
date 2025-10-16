import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    alembic_cfg = Config("app/alembic.ini")  # caminho para seu alembic.ini
    try:
        print("Aplicando migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations aplicadas com sucesso!")
    except Exception as e:
        print("Erro ao aplicar migrations:", e)
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()

