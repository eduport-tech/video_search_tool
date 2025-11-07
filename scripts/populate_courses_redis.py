import asyncio
import redis.asyncio as redis

async def main():
    # Connect to Redis
    r = await redis.from_url("redis://127.0.0.1:6379", decode_responses=True)

    # Define course data
    courses = {
        "JEE Repeater 2026": {
            "class": "JEE India"
        },
        "NEET Repeater 2026": {
            "class": "NEET India"
        },
        "Plus Two CBSE (Fastrack Tuition) 2025-26": {
            "class": "Class 12 Science CBSE India"
        },
        "Plus Two CBSE (JEE) 2025-26": {
            "class": "JEE India"
        },
        "Plus Two CBSE (NEET) 2025-26": {
            "class": "NEET India"
        },
        "Plus Two JEE (2025-26)": {
            "class": "JEE India"
        },
        "Plus Two NEET (2025-26)": {
            "class": "NEET India"
        },
        "Plus Two KEAM + Board (2025-26)": {
            "class": "Class 12 Science Kerala"
        },
        "Plus Two Science Board (2025-26)": {
            "class": "Class 12 Science Kerala"
        },
        "Plus Two Science Board Fastrack (2025-26)": {
            "class": "Class 12 Science Kerala"
        },
        "Class 10 CBSE (Tuition) 2025-26": {
            "class": "Class 10 CBSE India"
        },
        "Class 10 CBSE (Tuition+Foundation) 2025-26": {
            "class": "Class 10 CBSE India"
        },
        "Maths Pro (Class 10 CBSE)": {
            "class": "Class 10 CBSE India"
        },
        "Scholarship Exams": {
            "class": "Class 10 SSLC Kerala"
        },
        "SSLC English Medium (2025-26) - Fastrack": {
            "class": "Class 10 SSLC Kerala"
        },
        "SSLC Foundation (2025-26) Kerala Board": {
            "class": "Class 10 SSLC Kerala"
        },
        "SSLC Malayalam Medium (2025-26) - Fastrack": {
            "class": "Class 10 SSLC Kerala"
        }
    }

    # Store data in Redis
    for course_name, data in courses.items():
        redis_key = f"course_{course_name}"
        await r.hset(redis_key, mapping=data)
        print(f"✅ Added {redis_key} → {data['class']}")

    await r.aclose()

if __name__ == "__main__":
    asyncio.run(main())