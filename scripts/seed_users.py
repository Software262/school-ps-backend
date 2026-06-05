from sqlmodel import Session, create_engine
from app.modules.auth.infrastructure.models import Usuario

engine = create_engine("postgresql://postgres:password@localhost:5433/postgres")


def seed_users():
    with Session(engine) as session:
        # Check if users already exist
        existing = session.query(Usuario).first()
        if existing:
            print("Users already exist.")
            return

        users = [
            Usuario(
                username="admin",
                contrasenia="admin123",
                rol="Administrador",
                estado=True,
            ),
            Usuario(
                username="rector", contrasenia="rector123", rol="Rector", estado=True
            ),
            Usuario(
                username="tesorero",
                contrasenia="tesorero123",
                rol="Tesorero",
                estado=True,
            ),
            Usuario(
                username="docente", contrasenia="docente123", rol="Docente", estado=True
            ),
            Usuario(
                username="inactivo",
                contrasenia="inactivo123",
                rol="Docente",
                estado=False,
            ),
        ]
        session.add_all(users)
        session.commit()
        print("Test users seeded successfully.")


if __name__ == "__main__":
    seed_users()
