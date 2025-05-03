from handlers.admin.add_activist import AdminNewMemberRouter
from handlers.admin.default import AdminDefaultRouter
from handlers.admin.del_activist import AdminDelMemberRouter
from handlers.admin.event_creation import AdminEventCreatingRouter
from handlers.member.default import MemberDefaultRouter
from handlers.unknown import UnknownRouter


async def prepare_dispatcher(dp):
    dp.include_router(AdminNewMemberRouter)
    dp.include_router(AdminDelMemberRouter)
    dp.include_router(AdminEventCreatingRouter)
    dp.include_router(AdminDefaultRouter)
    dp.include_router(MemberDefaultRouter)


    dp.include_router(UnknownRouter)