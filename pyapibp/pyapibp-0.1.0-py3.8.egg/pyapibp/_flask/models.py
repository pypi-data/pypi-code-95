# Create your models here.

from app import db

from sqlalchemy import Column, Integer

class ExampleModel(db.Model):
    id = Column(Integer, primary_key=True)
