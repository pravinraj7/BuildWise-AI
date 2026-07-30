import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath('.'))

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./buildwise.db")

from database import AsyncSessionLocal
from models.knowledge import KnowledgeDocument
from sqlalchemy import select
from services.rag_service import index_document

async def run():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(KnowledgeDocument))
        docs = res.scalars().all()
        print("Total documents in DB:", len(docs))
        for d in docs:
            print(f"ID: {d.id}, Title: {d.title}, file_name: {d.file_name}, file_path: {d.file_path}, is_indexed: {d.is_indexed}, chunk_count: {d.chunk_count}")
            # Try to index it now to see what exception it raises!
            if not d.is_indexed:
                print(f"Attempting to manually index document: {d.title} ({d.file_path})...")
                # Wait, where is the file located?
                if d.file_path and os.path.exists(d.file_path):
                    success = await index_document(d.id, d.file_path)
                    print("Indexing result:", success)
                else:
                    print(f"File path does not exist: {d.file_path}")

if __name__ == "__main__":
    asyncio.run(run())
