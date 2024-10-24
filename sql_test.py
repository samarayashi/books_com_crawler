from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 創建數據庫引擎
engine = create_engine('sqlite:///test.db', echo=True)

# 創建基類
Base = declarative_base()

# 定義模型
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

# 創建表
Base.metadata.create_all(engine)

# 創建會話
Session = sessionmaker(bind=engine)
session = Session()

# 添加數據
new_user = User(name='Alice', age=30)
session.add(new_user)
session.commit()

# 查詢數據
user = session.query(User).filter_by(name='Alice').first()
print(f"User: {user.name}, Age: {user.age}")

# 關閉會話
session.close()