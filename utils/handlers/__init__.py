from .admin import admin_router
from .delete import delete_router
from .user import user_router

routers_list = [
        admin_router,
        delete_router,
        user_router,
        ]
