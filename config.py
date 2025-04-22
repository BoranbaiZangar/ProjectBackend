import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # ⚠️ ЗАМЕНИ значения ниже на свои:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:748596@localhost:5432/persona_forge'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
