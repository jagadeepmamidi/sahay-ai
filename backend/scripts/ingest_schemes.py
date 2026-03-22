"""
Scheme Data Ingestion Script
=============================

Downloads the MyScheme dataset from HuggingFace and loads it into:
1. Supabase (structured data for API queries)
2. ChromaDB (embeddings for semantic search)

Usage:
    cd backend
    python -m scripts.ingest_schemes

Author: Jagadeep Mamidi
"""

import json
import logging
import os
import sys
import hashlib
import time

# Add backend directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_dataset_file(file_path: str):
    """Load scheme data from a local JSON or CSV file."""
    
    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, dict) and "rows" in data:
                return data["rows"]
            else:
                # Try to find any list of schemes in the dict
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        return value
                return [data]
    
    elif file_path.endswith(".csv"):
        import csv
        schemes = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                schemes.append(row)
        return schemes
    
    elif file_path.endswith(".parquet"):
        try:
            import pandas as pd
            df = pd.read_parquet(file_path)
            return df.to_dict("records")
        except ImportError:
            logger.error("Install pandas and pyarrow: pip install pandas pyarrow")
            return []
    
    else:
        logger.error(f"Unsupported file format: {file_path}")
        return []


def try_load_from_huggingface():
    """Download PDFs from HuggingFace and extract structured scheme data."""
    try:
        from huggingface_hub import list_repo_files, hf_hub_download
        import fitz  # PyMuPDF

        repo_id = "shrijayan/gov_myscheme"
        logger.info(f"Listing files from HuggingFace: {repo_id}...")

        all_files = list(list_repo_files(repo_id, repo_type="dataset"))
        # Only take unique PDFs (skip "copy" duplicates)
        pdf_files = [
            f for f in all_files
            if f.endswith(".pdf") and "copy" not in f.lower()
        ]
        logger.info(f"Found {len(pdf_files)} unique scheme PDFs")

        records = []
        errors = 0

        for i, pdf_path in enumerate(pdf_files):
            try:
                # Download PDF
                local_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=pdf_path,
                    repo_type="dataset"
                )

                # Extract text with PyMuPDF
                doc = fitz.open(local_path)
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
                doc.close()

                if not full_text.strip():
                    continue

                # Parse scheme info from text
                record = parse_scheme_from_text(full_text, pdf_path)
                if record and record.get("name"):
                    records.append(record)

                if (i + 1) % 50 == 0:
                    logger.info(f"  Processed {i + 1}/{len(pdf_files)} PDFs ({len(records)} schemes extracted)")

            except Exception as e:
                errors += 1
                if errors <= 5:
                    logger.warning(f"  Error processing {pdf_path}: {e}")

        logger.info(f"Extracted {len(records)} schemes from {len(pdf_files)} PDFs ({errors} errors)")
        return records if records else None

    except ImportError as e:
        logger.warning(f"Could not load from HuggingFace: {e}")
        logger.info("  Install: pip install huggingface-hub PyMuPDF")
        return None
    except Exception as e:
        logger.warning(f"Could not load from HuggingFace: {e}")
        return None


def parse_scheme_from_text(text: str, filename: str) -> dict:
    """Parse structured scheme data from raw PDF text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return {}

    # The first meaningful line is usually the scheme name
    name = lines[0][:200] if lines else os.path.basename(filename).replace(".pdf", "")

    # Try to extract sections by common headings
    sections = {
        "description": "",
        "eligibility": "",
        "benefits": "",
        "application_process": "",
        "documents": "",
    }

    current_section = "description"
    section_keywords = {
        "eligibility": ["eligibility", "who can apply", "eligible", "criteria"],
        "benefits": ["benefits", "benefit", "incentive", "financial assistance", "amount"],
        "application_process": ["application process", "how to apply", "apply online", "procedure"],
        "documents": ["documents required", "documents", "required documents"],
    }

    for line in lines[1:]:
        line_lower = line.lower()

        # Check if this line is a section header
        matched = False
        for section, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords) and len(line) < 80:
                current_section = section
                matched = True
                break

        if not matched:
            sections[current_section] += line + " "

    return {
        "name": name,
        "description": sections["description"][:2000].strip(),
        "Eligibility": sections["eligibility"][:2000].strip(),
        "Benefits": sections["benefits"][:2000].strip(),
        "Application Process": sections["application_process"][:2000].strip(),
        "Documents Required": sections["documents"][:2000].strip(),
    }


def normalize_scheme(raw: dict, index: int) -> dict:
    """
    Normalize a raw scheme record into our standard format.
    Handles various field names from different datasets.
    """
    # Generate a stable ID from scheme name
    name = (
        raw.get("Scheme Name") or
        raw.get("scheme_name") or
        raw.get("name") or
        raw.get("Name") or
        raw.get("title") or
        f"scheme-{index}"
    )
    
    scheme_id = hashlib.md5(name.lower().strip().encode()).hexdigest()[:12]
    
    description = (
        raw.get("Description") or
        raw.get("description") or
        raw.get("Details") or
        raw.get("details") or
        ""
    )
    
    benefits = (
        raw.get("Benefits") or
        raw.get("benefits") or
        raw.get("Benefit") or
        raw.get("benefit") or
        ""
    )
    
    eligibility = (
        raw.get("Eligibility") or
        raw.get("Eligibility Criteria") or
        raw.get("eligibility") or
        raw.get("eligibility_criteria") or
        raw.get("Eligibility criteria") or
        ""
    )
    
    application_process = (
        raw.get("Application Process") or
        raw.get("application_process") or
        raw.get("How to Apply") or
        raw.get("how_to_apply") or
        ""
    )
    
    category = (
        raw.get("Category") or
        raw.get("category") or
        raw.get("Scheme Category") or
        raw.get("Department") or
        "General"
    )
    
    apply_url = (
        raw.get("Official Link") or
        raw.get("official_link") or
        raw.get("URL") or
        raw.get("url") or
        raw.get("Apply URL") or
        ""
    )
    
    ministry = (
        raw.get("Ministry") or
        raw.get("ministry") or
        raw.get("Department") or
        raw.get("department") or
        ""
    )
    
    documents = (
        raw.get("Documents Required") or
        raw.get("documents_required") or
        raw.get("Documents") or
        ""
    )
    
    # Build documents_required as list
    docs_list = []
    if isinstance(documents, str) and documents.strip():
        # Split by common delimiters
        for doc in documents.replace("\n", ",").split(","):
            doc = doc.strip().strip("-").strip("•").strip()
            if doc and len(doc) > 2:
                docs_list.append({
                    "name": doc[:100],
                    "description": "",
                    "is_mandatory": True
                })
    elif isinstance(documents, list):
        docs_list = documents
    
    # Determine scheme type
    scheme_type = "central"
    name_lower = name.lower()
    if any(
        state.lower() in name_lower
        for state in ["telangana", "andhra", "karnataka", "tamil", "maharashtra", "kerala"]
    ):
        scheme_type = "state"
    
    return {
        "id": scheme_id,
        "name": name.strip()[:200],
        "name_hindi": raw.get("name_hindi", ""),
        "category": category.strip()[:50],
        "scheme_type": scheme_type,
        "ministry": str(ministry).strip()[:200],
        "description": str(description).strip(),
        "benefits": str(benefits).strip(),
        "benefit_amount": raw.get("benefit_amount", ""),
        "eligibility_summary": str(eligibility).strip()[:2000],
        "eligibility_criteria": [],
        "documents_required": docs_list[:10],
        "application_process": str(application_process).strip(),
        "apply_url": str(apply_url).strip()[:500],
        "helpline": raw.get("helpline", ""),
        "is_active": True
    }


def build_chunks(scheme: dict) -> list:
    """
    Create text chunks from a scheme for embedding into ChromaDB.
    Each chunk represents a different aspect of the scheme.
    """
    chunks = []
    name = scheme["name"]
    scheme_id = scheme["id"]
    
    # Main overview chunk
    overview = f"{name}. {scheme['description']}"
    if scheme.get("benefits"):
        overview += f" Benefits: {scheme['benefits']}"
    
    if overview.strip() and len(overview) > 20:
        chunks.append({
            "id": f"{scheme_id}-overview",
            "content": overview[:2000],
            "metadata": {
                "scheme_id": scheme_id,
                "scheme_name": name,
                "category": scheme.get("category", ""),
                "section": "overview",
                "benefit_summary": str(scheme.get("benefits", ""))[:200],
                "eligibility_summary": str(scheme.get("eligibility_summary", ""))[:200]
            }
        })
    
    # Eligibility chunk (if substantial)
    if scheme.get("eligibility_summary") and len(scheme["eligibility_summary"]) > 20:
        chunks.append({
            "id": f"{scheme_id}-eligibility",
            "content": f"{name} eligibility: {scheme['eligibility_summary']}"[:2000],
            "metadata": {
                "scheme_id": scheme_id,
                "scheme_name": name,
                "category": scheme.get("category", ""),
                "section": "eligibility"
            }
        })
    
    # Application process chunk (if substantial)
    if scheme.get("application_process") and len(scheme["application_process"]) > 20:
        chunks.append({
            "id": f"{scheme_id}-apply",
            "content": f"How to apply for {name}: {scheme['application_process']}"[:2000],
            "metadata": {
                "scheme_id": scheme_id,
                "scheme_name": name,
                "category": scheme.get("category", ""),
                "section": "application"
            }
        })
    
    return chunks


def ingest_to_supabase(schemes: list):
    """Insert normalized schemes into Supabase."""
    try:
        from app.db.supabase_client import get_supabase
        
        client = get_supabase()
        
        # Insert in batches of 50
        batch_size = 50
        inserted = 0
        
        for i in range(0, len(schemes), batch_size):
            batch = schemes[i:i + batch_size]
            
            # Prepare for Supabase (remove None values, convert lists)
            clean_batch = []
            for s in batch:
                clean = {k: v for k, v in s.items() if v is not None}
                # Convert list fields to JSON for Supabase
                if "eligibility_criteria" in clean:
                    clean["eligibility_criteria"] = json.dumps(clean["eligibility_criteria"])
                if "documents_required" in clean:
                    clean["documents_required"] = json.dumps(clean["documents_required"])
                clean_batch.append(clean)
            
            try:
                client.table("schemes").upsert(clean_batch).execute()
                inserted += len(clean_batch)
                logger.info(f"  Inserted batch {i // batch_size + 1}: {inserted} / {len(schemes)}")
            except Exception as e:
                logger.error(f"  Batch insert failed: {e}")
                # Try one by one
                for s in clean_batch:
                    try:
                        client.table("schemes").upsert(s).execute()
                        inserted += 1
                    except Exception as e2:
                        logger.error(f"  Failed to insert {s.get('name', '?')}: {e2}")
        
        logger.info(f"✅ Inserted {inserted} schemes into Supabase")
        return inserted
        
    except Exception as e:
        logger.error(f"❌ Supabase insertion failed: {e}")
        logger.info("  Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in .env")
        logger.info("  And that you've run supabase_schema.sql in your Supabase dashboard")
        return 0


def ingest_to_chromadb(schemes: list):
    """Create chunks and embed into ChromaDB."""
    try:
        from app.rag.hybrid_retriever import get_retriever
        
        retriever = get_retriever()
        
        # Clear existing data for clean re-ingestion
        retriever.clear_all()
        
        # Build chunks from all schemes
        all_chunks = []
        for scheme in schemes:
            chunks = build_chunks(scheme)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(schemes)} schemes")
        
        # Insert in batches
        batch_size = 20  # Small batches to avoid Gemini rate limits
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            retriever.add_documents_batch(batch)
            logger.info(f"  Embedded batch {i // batch_size + 1}: {min(i + batch_size, len(all_chunks))} / {len(all_chunks)}")
            
            # Small delay to respect Gemini API rate limits
            if i + batch_size < len(all_chunks):
                time.sleep(1)
        
        stats = retriever.get_stats()
        logger.info(f"✅ ChromaDB stats: {stats}")
        return len(all_chunks)
        
    except Exception as e:
        logger.error(f"❌ ChromaDB ingestion failed: {e}")
        return 0


def main():
    """Main ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("Sahay AI - Scheme Data Ingestion")
    logger.info("=" * 60)
    
    # Step 1: Load data
    raw_schemes = None
    
    # Check for local data files first
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "datasets")
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            filepath = os.path.join(data_dir, filename)
            if filename.endswith((".json", ".csv", ".parquet")):
                logger.info(f"Found local dataset: {filepath}")
                raw_schemes = load_dataset_file(filepath)
                if raw_schemes:
                    break
    
    # If no local file, try HuggingFace
    if not raw_schemes:
        logger.info("No local dataset found. Trying HuggingFace...")
        raw_schemes = try_load_from_huggingface()
    
    if not raw_schemes:
        logger.error(
            "❌ No data found!\n"
            "   Please either:\n"
            "   1. Download the dataset from https://huggingface.co/datasets/shrijayan/gov_myscheme\n"
            "      and place the JSON/CSV file in backend/data/datasets/\n"
            "   2. Or install 'datasets' library: pip install datasets\n"
            "      and we'll download it automatically"
        )
        return
    
    logger.info(f"📦 Loaded {len(raw_schemes)} raw scheme records")
    
    # Step 2: Normalize data
    logger.info("Normalizing scheme data...")
    schemes = []
    seen_ids = set()
    for i, raw in enumerate(raw_schemes):
        try:
            scheme = normalize_scheme(raw, i)
            # Skip duplicates
            if scheme["id"] not in seen_ids and scheme["name"]:
                seen_ids.add(scheme["id"])
                schemes.append(scheme)
        except Exception as e:
            logger.warning(f"  Skipping record {i}: {e}")
    
    logger.info(f"📋 Normalized {len(schemes)} unique schemes")
    
    # Show first few
    for s in schemes[:5]:
        logger.info(f"  - {s['name']} [{s['category']}]")
    if len(schemes) > 5:
        logger.info(f"  ... and {len(schemes) - 5} more")
    
    # Step 3: Ingest to Supabase
    logger.info("\n--- Ingesting to Supabase ---")
    supabase_count = ingest_to_supabase(schemes)
    
    # Step 4: Ingest to ChromaDB (embeddings)
    logger.info("\n--- Ingesting to ChromaDB ---")
    logger.info("(This will take a few minutes due to embedding generation...)")
    chromadb_count = ingest_to_chromadb(schemes)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("✅ INGESTION COMPLETE")
    logger.info(f"   Supabase: {supabase_count} schemes")
    logger.info(f"   ChromaDB: {chromadb_count} chunks")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
