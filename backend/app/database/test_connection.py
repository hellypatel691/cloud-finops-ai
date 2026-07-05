# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv
# import os

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# print("DATABASE URL FOUND:", DATABASE_URL is not None)

# if DATABASE_URL:
#     print(DATABASE_URL[:35] + "...")

# engine = create_engine(DATABASE_URL)

# # engine = create_engine(
# #     DATABASE_URL,
# #     connect_args={
# #         "connect_timeout": 10
# #     }
# # )

# try:
#     with engine.connect() as connection:

#         print("Connected!")

#         result = connection.execute(text("SELECT version();"))

#         print(result.fetchone())

# except Exception as e:
#     print(e)


from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))

        print("=" * 60)
        print("DATABASE CONNECTED SUCCESSFULLY")
        print("=" * 60)

        print(result.fetchone())

except Exception as e:
    print(e)