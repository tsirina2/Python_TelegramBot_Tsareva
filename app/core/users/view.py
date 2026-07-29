from sqladmin import ModelView
from app.core.users.models import User

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.is_waiter]




