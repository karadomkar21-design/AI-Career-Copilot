from db import Base, engine
import models

print(Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)