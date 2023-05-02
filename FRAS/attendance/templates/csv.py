from sqlalchemy import create_engine, Column, Date, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///.db', echo=True)
Base = declarative_base()
