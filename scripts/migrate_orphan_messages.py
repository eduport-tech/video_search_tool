import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from beanie.operators import In

from server.config import CONFIG
from server.models.user import User, Message, Conversation


async def migrate_orphan_messages():
    print("Starting migration of orphan messages...")

    client = AsyncIOMotorClient(CONFIG.mongo_uri)
    db = client.doubt_clearance
    await init_beanie(
        database=db,
        document_models=[User, Message, Conversation],
    )

    orphan_user_ids = await Message.get_motor_collection().distinct(
        "user.$id", 
        {"conversation": None}
    )
    for user in orphan_user_ids:
        print(f"Processing user {user} ...")

        # Find messages for the user without a conversation link
        orphan_messages = await Message.find(
            Message.user.id == user, Message.conversation == None
        ).to_list()

        if orphan_messages:
            print(
                f"Found {len(orphan_messages)} orphan messages for user {user}."
            )
            new_conversation = Conversation(user=user, title="Previous Chats")
            await new_conversation.insert()
            for message in orphan_messages:
                message.conversation = new_conversation 
                await message.save()

    print("Migration completed successfully.")

if __name__ == "__main__":
    asyncio.run(migrate_orphan_messages())
