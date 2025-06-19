# from sqlalchemy import Column, Integer, String
# # from app.database import Base

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     hashed_password = Column(String)

#     def __repr__(self):
#         return f"<User(id={self.id}, username={self.username})>"

#     # Additional methods for user-related operations can be added here
#     def get_user_info(self):
#         return {
#             "id": self.id,
#             "username": self.username
#         }