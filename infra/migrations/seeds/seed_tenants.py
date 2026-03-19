import os

from domain.models.tenant import Tenant
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Get URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback for local execution outside docker if necessary
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/webhooks"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def seed():
    print("Starting tenant seeding...")
    db: Session = SessionLocal()

    try:
        # Check if tenants already exist to avoid duplicates
        existing_count = db.query(Tenant).count()
        if existing_count > 0:
            print(f"Tenants already exist: {existing_count}. Skipping seed.")
            return

        tenant_a = Tenant(name="client_a", api_key="key-client-a")

        tenant_b = Tenant(name="client_b", api_key="key-client-b")

        db.add_all([tenant_a, tenant_b])
        db.commit()
        print("Tenants created successfully: client_a, client_b")

    except Exception as e:
        print(f"Error during seed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
