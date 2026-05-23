import asyncio
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

async def main():
    client = AsyncQdrantClient("localhost", port=6333)
    try:
        results = await client.query_points(
            collection_name="archival_memory",
            query=[0.1]*384,
            limit=3,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value="user-2161")
                    )
                ]
            )
        )
        print("SUCCESS", results)
    except Exception as e:
        print(f"FAILED: {e}")

asyncio.run(main())
