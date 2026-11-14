
from handlers.start import router as start_router
from handlers.tags import router as tags_router
from handlers.single_tag import router as single_tag_router
from handlers.funny_tag import router as funny_tag_router
from handlers.clone import router as clone_router
from handlers.admin import router as admin_router
from handlers.tracking import router as tracking_router
from handlers.ban import router as ban_router


def register_handlers(dispatcher):
    dispatcher.include_router(start_router)
    dispatcher.include_router(ban_router)
    dispatcher.include_router(clone_router)
    dispatcher.include_router(tags_router)
    dispatcher.include_router(single_tag_router)
    dispatcher.include_router(funny_tag_router)
    dispatcher.include_router(admin_router)
    dispatcher.include_router(tracking_router)
