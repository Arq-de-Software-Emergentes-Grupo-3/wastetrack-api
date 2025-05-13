from sqlalchemy import create_engine, MetaData

meta = MetaData()

engine = create_engine("mysql+pymysql://root:password@localhost:3306/wastetrackdb")

connection = engine.connect()