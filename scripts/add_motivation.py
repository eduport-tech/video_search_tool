import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from server.config import CONFIG
from server.models.motivation import Motivation


async def add_motivational_videos():
    """
    Connects to the database and adds a list of motivational videos.
    """
    client = AsyncIOMotorClient(CONFIG.mongo_uri)
    db = client.doubt_clearance

    await init_beanie(
        database=db,
        document_models=[
            Motivation,
        ],
    )

    videos = [
        Motivation(video_url="https://www.youtube.com/watch?v=TQFf3OOs0Ec", class_name="DEFAULT", teacher_name="Akhil"),
        Motivation(video_url="https://www.youtube.com/watch?v=miMOxBEwG04", class_name="DEFAULT", teacher_name="Ajas"),
        Motivation(video_url="https://www.youtube.com/watch?v=FIgzeIU240Q", class_name="DEFAULT", teacher_name="Aida"),
        Motivation(video_url="https://www.youtube.com/watch?v=gDj4QfIG4tM", class_name="Class 10 SSLC Kerala", teacher_name="Aida"),
        Motivation(video_url="https://www.youtube.com/watch?v=uil0bjzkJKI", class_name="DEFAULT", teacher_name="DEFAULT"),
        Motivation(video_url="https://www.youtube.com/watch?v=SCPWuBptyC4", class_name="DEFAULT", teacher_name="Hashal"),
    ]

    await Motivation.insert_many(videos)

    print(f"Successfully added {len(videos)} motivational videos.")


if __name__ == "__main__":
    asyncio.run(add_motivational_videos())