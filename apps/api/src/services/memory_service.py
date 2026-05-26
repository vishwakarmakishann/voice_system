import asyncio
import uuid
from datetime import datetime
from groq import AsyncGroq
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.config import settings
from src.models.memory import CoreMemory

# Initialize fastembed globally so we don't reload the ONNX model every time!
try:
    from fastembed import TextEmbedding
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
except ImportError:
    embedding_model = None
    print("Warning: fastembed not installed")

COLLECTION_NAME = "archival_memory"

def get_groq_client():
    if settings.GROQ_API_KEY:
        return AsyncGroq(api_key=settings.GROQ_API_KEY)
    return None

def get_qdrant_client():
    return AsyncQdrantClient(url=settings.QDRANT_URL)

async def init_qdrant():
    """Ensure the Qdrant collection exists."""
    try:
        qclient = get_qdrant_client()
        exists = await qclient.collection_exists(COLLECTION_NAME)
        if not exists:
            # We will use fastembed's default embedding size (384 for BAAI/bge-small-en-v1.5)
            await qclient.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")

async def extract_memories(user_id: str, transcript: list[dict], db: AsyncSession):
    """
    Background task to analyze a conversation transcript, 
    extract Core and Archival memories, and store them.
    """
    gclient = get_groq_client()
    if not gclient:
        print("GROQ_API_KEY not set in API, skipping memory extraction.")
        return

    # 1. Format the transcript
    chat_text = "\\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in transcript if msg['role'] != 'system'])
    if not chat_text.strip():
        return

    # 2. Extract Core Memory updates
    try:
        # Fetch existing memory first to provide to the LLM
        result = await db.execute(select(CoreMemory).where(CoreMemory.user_id == user_id))
        memory_record = result.scalars().first()
        existing_persona = memory_record.persona if memory_record else "No existing core facts."

        core_prompt = f"""
        You are an AI managing a user's "Core Persona" memory. 
        Your task is to merge any NEW permanent, identity-level facts from the recent conversation into the existing persona.
        
        Examples of core facts: name, age, profession, hobbies, dietary restrictions, personality traits, location, etc.
        DO NOT include specific conversational history, greetings, or temporary states.
        
        Rules:
        1. Resolve conflicts (e.g. if existing says "Lives in NY" but new says "Moved to LA", update it to "Lives in LA").
        2. Deduplicate facts.
        3. Do not add conversational filler like "No new facts" or "Assistant's name". Only output the consolidated bulleted list.
        4. If there are absolutely no core facts about the user to store, reply exactly with "NONE".
        5. Output ONLY the bulleted list. No conversational pleasantries.
        
        Existing Persona:
        {existing_persona}
        
        Recent Conversation:
        {chat_text}
        """
        
        core_res = await gclient.chat.completions.create(
            messages=[{"role": "user", "content": core_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2
        )
        new_persona = core_res.choices[0].message.content.strip()
        
        if new_persona and new_persona.strip().upper() != "NONE" and "no other core facts" not in new_persona.lower():
            if memory_record:
                memory_record.persona = new_persona
            else:
                memory_record = CoreMemory(user_id=user_id, persona=new_persona)
                db.add(memory_record)
            
            await db.commit()
    except Exception as e:
        print(f"Error extracting core memory: {e}")

    # 3. Extract Archival Memory (Specific events/topics)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archival_prompt = f"""
    Write a detailed, specific paragraph summarizing the events and topics discussed in this conversation.
    This will be used for semantic search later. Include specific details, questions asked, and answers given.
    Include the date/time context: {current_time}.
    If the conversation was purely a greeting with no substantive discussion, reply exactly with "NO_SUMMARY".
    
    Conversation:
    {chat_text}
    """
    try:
        archival_res = await gclient.chat.completions.create(
            messages=[{"role": "user", "content": archival_prompt}],
            model="llama-3.1-8b-instant"
        )
        summary = archival_res.choices[0].message.content.strip()
        
        if "no_summary" not in summary.lower() and len(summary) > 10 and embedding_model:
            # Fastembed returns a generator
            embeddings = list(embedding_model.embed([summary]))
            vector = embeddings[0].tolist()
            
            qclient = get_qdrant_client()
            await qclient.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "user_id": user_id,
                            "content": summary,
                            "timestamp": current_time
                        }
                    )
                ]
            )
    except Exception as e:
        print(f"Error extracting archival memory: {e}")

async def search_archival_memory(user_id: str, query: str, limit: int = 3) -> list[str]:
    """Search Qdrant for past memories relevant to a query."""
    try:
        if not embedding_model:
            return []
            
        embeddings = list(embedding_model.embed([query]))
        vector = embeddings[0].tolist()
        
        from qdrant_client.http import models
        qclient = get_qdrant_client()
        
        search_result = await qclient.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=limit,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            )
        )
        
        results = []
        for hit in search_result.points:
            timestamp = hit.payload.get("timestamp", "")
            content = hit.payload.get("content", "")
            results.append(f"[{timestamp}] {content}")
            
        return results
    except Exception as e:
        print(f"Error searching archival memory: {e}")
        return []
