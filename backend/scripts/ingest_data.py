"""
Sahay AI - Data Ingestion Script
=================================

Standalone script to download and ingest scheme data into ChromaDB.

Usage:
    python scripts/ingest_data.py

Author: Jagadeep Mamidi
"""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Run the data ingestion pipeline."""
    from app.db.chroma import get_chroma_client
    from app.pipeline.ingester import get_collection_stats, ingest_all_datasets

    logger.info("=" * 50)
    logger.info("Sahay AI - Data Ingestion Pipeline")
    logger.info("=" * 50)

    chroma = get_chroma_client()
    logger.info(f"ChromaDB directory: {chroma.persist_dir}")
    logger.info(f"Collection: {chroma.collection_name}")

    current_count = chroma.count()
    logger.info(f"Current chunks in database: {current_count}")

    if current_count > 0:
        logger.info("Collection already has data. Skipping ingestion.")
        stats = get_collection_stats()
        logger.info(f"Total chunks: {stats['total_chunks']}")
        return

    logger.info("\nIngesting configured HuggingFace datasets...")
    try:
        results = await ingest_all_datasets()
        for name, count in results.items():
            logger.info(f"  {name}: {count} chunks")
    except Exception as e:
        logger.error(f"Failed to ingest some datasets: {e}")

    stats = get_collection_stats()
    logger.info("\n" + "=" * 50)
    logger.info("Ingestion Complete!")
    logger.info(f"Total chunks: {stats['total_chunks']}")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
