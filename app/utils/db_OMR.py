from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


from app.utils.general import get_cnf

business_set = get_cnf("conf/server.cnf", "business")
business_URL = "mysql+aiomysql://" + \
                business_set["user"] + \
               ":" + \
                business_set["password"] + \
               "@" + \
                business_set["host"] + \
               ":" + \
                business_set["port"] + \
               "/" + \
                business_set["database"]


business_engine = create_async_engine(
    business_URL, 
    echo=True
)

async_business_session_maker = sessionmaker(
    business_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_async_session():
    async with async_business_session_maker() as session:
        yield session