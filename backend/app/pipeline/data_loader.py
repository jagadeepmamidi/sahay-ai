"""
Sahay AI - Data Loader
=======================

Load datasets from HuggingFace for scheme data ingestion.

Author: Jagadeep Mamidi
"""

import logging
from typing import Any, Dict, List, Optional

from datasets import Dataset, load_dataset

logger = logging.getLogger(__name__)

DATASETS = {
    "gov_myscheme": "shrijayan/gov_myscheme",
    "scholarships": "NetraVerse/indian-govt-scholarships",
    "ap_scholarships": "vyshnaviprasad/scholarship_dataset",
}


def load_huggingface_dataset(
    dataset_name: str = "gov_myscheme", split: str = "train"
) -> Dataset:
    """
    Load a dataset from HuggingFace.

    Args:
        dataset_name: Name of the dataset (see DATASETS dict)
        split: Dataset split (train, test, validation)

    Returns:
        HuggingFace Dataset object
    """
    if dataset_name not in DATASETS:
        raise ValueError(
            f"Unknown dataset: {dataset_name}. Available: {list(DATASETS.keys())}"
        )

    repo_id = DATASETS[dataset_name]
    logger.info(f"Loading dataset: {repo_id}")

    try:
        dataset = load_dataset(repo_id, split=split)
        logger.info(f"Loaded {len(dataset)} examples")
        return dataset
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise


def get_all_datasets() -> Dict[str, Dataset]:
    """
    Load all available scheme datasets.

    Returns:
        Dict mapping dataset name to Dataset object
    """
    result = {}
    for name in DATASETS:
        try:
            result[name] = load_huggingface_dataset(name)
        except Exception as e:
            logger.warning(f"Failed to load {name}: {e}")
    return result


def dataset_to_documents(
    dataset: Dataset, source_name: str = "huggingface"
) -> List[Dict[str, Any]]:
    """
    Convert a HuggingFace dataset to document format for RAG.

    Args:
        dataset: HuggingFace Dataset

    Returns:
        List of document dicts with text and metadata
    """
    documents = []

    for idx, item in enumerate(dataset):
        doc = {
            "id": f"{source_name}_doc_{idx}",
            "text": "",
            "metadata": {
                "source": "huggingface",
                "dataset": source_name,
                "index": idx,
            },
        }

        if "text" in item:
            doc["text"] = item["text"]
        elif "description" in item:
            doc["text"] = item["description"]
        elif "content" in item:
            doc["text"] = item["content"]

        for key in ["scheme_name", "name", "title", "label"]:
            if key in item:
                doc["metadata"]["scheme_name"] = item[key]
                break

        for key in ["category", "type", "category_name"]:
            if key in item:
                doc["metadata"]["category"] = item[key]
                break

        if "source_url" in item:
            doc["metadata"]["source_url"] = item["source_url"]
        if "official_link" in item:
            doc["metadata"]["source_url"] = item["official_link"]

        if "eligibility_criteria" in item:
            doc["metadata"]["eligibility"] = item["eligibility_criteria"]
        if "benefits" in item:
            doc["metadata"]["benefits"] = item["benefits"]
        if "application_process" in item:
            doc["metadata"]["application_process"] = item["application_process"]

        if doc["text"]:
            documents.append(doc)

    return documents
