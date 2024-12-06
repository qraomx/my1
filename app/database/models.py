from sqlalchemy import BigInteger, String, ForeignKey, Integer, Date 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sqlalchemy.ext.asyncio import AsyncAttrs,async_sessionmaker,create_async_engine

engine= create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session=async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__='users'

    id: Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    tg_id=mapped_column(BigInteger)


class Subject(Base):
    __tablename__='Subjects'

    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(50))
    visible: Mapped[int]=mapped_column(Integer(),default=1)
    ord: Mapped[int]=mapped_column(Integer())

class Olympiad(Base):
    __tablename__='Olympiads'

    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    level: Mapped[str]=mapped_column(String(10))
    url_path: Mapped[str]=mapped_column(String(100))
    description: Mapped[str]=mapped_column(String(400))
    visible: Mapped[int]=mapped_column(Integer(),default=1)
    ord: Mapped[int]=mapped_column(Integer())
    work_note: Mapped[str]=mapped_column(String(100))

class Sub_Olymp(Base):
    __tablename__='Sub_Olymps'

    id: Mapped[int]=mapped_column(primary_key=True)
    id_subject:Mapped[int]=mapped_column(ForeignKey('Subjects.id'))
    id_Olymp:Mapped[int]=mapped_column(ForeignKey('Olympiads.id'))
    profile: Mapped[str]=mapped_column(String(100))
    visible: Mapped[int]=mapped_column(Integer(),default=1)
    ord: Mapped[int]=mapped_column(Integer())

class Step_type(Base):
    __tablename__='StepTypes'

    id: Mapped[int]=mapped_column(primary_key=True)   
    name: Mapped[str]=mapped_column(String(100))
    step_type: Mapped[int]=mapped_column(Integer())    
   

class Step(Base):
    __tablename__='Steps'

    id: Mapped[int]=mapped_column(primary_key=True)
    id_SubOlymp:Mapped[int]=mapped_column(ForeignKey('Sub_Olymps.id'))  
    id_StepTypes:Mapped[int]=mapped_column(ForeignKey('StepTypes.id'))  
    date_type :Mapped[int]=mapped_column(Integer())
    date_from: Mapped[Date]=mapped_column(Date())
    date_to: Mapped[Date]=mapped_column(Date())

# Олимпиады пользователей  (какие олимпиады кто отслеживаниет)
class User_Olymp(Base):
    __tablename__='User_Olymps'
    id: Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    tg_id=mapped_column(BigInteger)
    id_sub_olymps:Mapped[int]=mapped_column(Integer())

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

 
class OlimpList:   
    def __init__(self, i,id,name,subscribed,id_subject):  
        self.i = i   
        self.id = id
        self.name=name
        self.subscribed=subscribed
        self.id_subject=id_subject


