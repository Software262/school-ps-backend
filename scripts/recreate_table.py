from sqlmodel import SQLModel, Session, text
from app.core.db import engine


def main():
    with Session(engine) as session:
        session.execute(text("DROP TABLE IF EXISTS detalleprueba;"))
        session.commit()
    SQLModel.metadata.create_all(engine)
    print("Table recreated.")


if __name__ == "__main__":
    main()
