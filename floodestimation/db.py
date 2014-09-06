from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from appdirs import AppDirs

Base = declarative_base()

DATA_FOLDER = AppDirs('fehdata', appauthor='OpenHydrology').user_data_dir
DB_FILE_PATH = os.path.join(DATA_FOLDER, 'fehdata.sqlite')
os.makedirs(DATA_FOLDER, exist_ok=True)

engine = create_engine('sqlite:///' + DB_FILE_PATH)
Session = sessionmaker(engine)


def create_new_db():
    global engine
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)