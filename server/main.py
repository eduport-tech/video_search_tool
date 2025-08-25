"""My server runtime"""
from server.app import app
from server.routes.doubt_clearance import router as DoubtClearanceRoutes
from server.routes.conversation import router as ConversationRoutes
from server.routes.files import router as FilesRoutes

app.include_router(DoubtClearanceRoutes)
app.include_router(ConversationRoutes)
app.include_router(FilesRoutes)