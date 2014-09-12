# Current package imports
from . import db
# Need to import all entities to create corresponding database tables
from .entities import Catchment, AmaxRecord, Comment, Descriptors

# Create database tables if they don't exist yet
db.Base.metadata.create_all(db.engine)

# import os.path as path
#
# import floodestimation.fehdata as fehdata
# import floodestimation.parsers as parsers
#
#
# def load_catchment(cd3_file_path):
#     am_file_path = path.splitext(cd3_file_path)[0] + '.AM'
#
#     catchment = parsers.Cd3Parser().parse(cd3_file_path)
#     catchment.amax_records = parsers.AmaxParser().parse(am_file_path)
#     return catchment
#
#
# def update_database(session):
#     fehdata.clear_cache()
#     fehdata.download_data()
#     fehdata.unzip_data()
#     for cd3_file_path in fehdata.cd3_files():
#         catchment = load_catchment(cd3_file_path)
#         session.add(catchment)
#     session.commit()