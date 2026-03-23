"""
Sahay AI - Data Loader
=======================

Load datasets from HuggingFace for scheme data ingestion.

Author: Jagadeep Mamidi
"""

import logging
import re
from typing import Any, Dict, List

import pandas as pd
from datasets import Dataset, load_dataset
from huggingface_hub import hf_hub_download

logger = logging.getLogger(__name__)

DATASETS = {
    "indian_gov_schemes": {
        "repo_id": "abhisshek0077/Indian_government_Schemes_For_People",
        "format": "csv",
        "filename": "Indian_Govenment_Scheme.csv",
        "encoding": "latin1",
    },
}


def _clean_text(value: Any) -> str:
    """Normalize imported text into cleaner plain text."""
    if value is None:
        return ""

    text = str(value)
    if text.lower() == "nan":
        return ""

    # Remove common HTML and markdown noise present in the dataset.
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"[*_>`#]+", " ", text)

    # Collapse replacement-character noise into a rupee symbol when obvious.
    text = text.replace("ï¿½ï¿½ï¿½", "Rs. ")
    text = text.replace("ýýý", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _load_structured_csv_dataset(dataset_config: Dict[str, str]) -> Dataset:
    """Load a CSV-backed dataset repo from Hugging Face into a Dataset."""
    path = hf_hub_download(
        repo_id=dataset_config["repo_id"],
        filename=dataset_config["filename"],
        repo_type="dataset",
    )
    frame = pd.read_csv(path, encoding=dataset_config.get("encoding", "utf-8"))
    frame = frame.fillna("")
    logger.info(f"Loaded {len(frame)} rows from {dataset_config['repo_id']}")
    return Dataset.from_pandas(frame, preserve_index=False)


def load_huggingface_dataset(
    dataset_name: str = "indian_gov_schemes", split: str = "train"
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

    dataset_config = DATASETS[dataset_name]
    repo_id = dataset_config["repo_id"]
    logger.info(f"Loading dataset: {repo_id}")

    try:
        if dataset_config.get("format") == "csv":
            dataset = _load_structured_csv_dataset(dataset_config)
        else:
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
        scheme_name = _clean_text(
            item.get("scheme_name")
            or item.get("name")
            or item.get("title")
            or item.get("label")
        )
        brief_description = _clean_text(item.get("brief_description"))
        detailed_description = _clean_text(item.get("detailed_description"))
        eligibility = _clean_text(item.get("eligibility_criteria"))
        benefits = _clean_text(item.get("benefits"))
        application_process = _clean_text(item.get("application_process"))
        documents_required = _clean_text(item.get("documents_required"))
        category = _clean_text(
            item.get("category") or item.get("type") or item.get("category_name")
        )
        state = _clean_text(item.get("state"))
        level = _clean_text(item.get("level"))
        ministry = _clean_text(item.get("nodal_ministry"))
        implementing_agency = _clean_text(item.get("implementing_agency"))

        doc = {
            "id": f"{source_name}_doc_{idx}",
            "text": "",
            "metadata": {
                "source": "huggingface",
                "dataset": source_name,
                "index": idx,
            },
        }

        if source_name == "indian_gov_schemes":
            parts = [
                part
                for part in [
                    f"Scheme Name: {scheme_name}" if scheme_name else "",
                    f"Category: {category}" if category else "",
                    f"State: {state}" if state else "",
                    f"Level: {level}" if level else "",
                    f"Brief Description: {brief_description}"
                    if brief_description
                    else "",
                    f"Detailed Description: {detailed_description}"
                    if detailed_description
                    else "",
                    f"Eligibility: {eligibility}" if eligibility else "",
                    f"Benefits: {benefits}" if benefits else "",
                    f"Documents Required: {documents_required}"
                    if documents_required
                    else "",
                    f"Application Process: {application_process}"
                    if application_process
                    else "",
                    f"Nodal Ministry: {ministry}" if ministry else "",
                    f"Implementing Agency: {implementing_agency}"
                    if implementing_agency
                    else "",
                ]
                if part
            ]
            doc["text"] = "\n".join(parts)

            doc["metadata"]["scheme_name"] = scheme_name
            doc["metadata"]["scheme_id"] = re.sub(
                r"[^a-z0-9]+", "-", scheme_name.lower()
            ).strip("-")
            doc["metadata"]["category"] = category
            doc["metadata"]["state"] = state
            doc["metadata"]["level"] = level
            doc["metadata"]["ministry"] = ministry
            doc["metadata"]["implementing_agency"] = implementing_agency
            doc["metadata"]["eligibility"] = eligibility
            doc["metadata"]["eligibility_summary"] = eligibility[:240]
            doc["metadata"]["benefits"] = benefits
            doc["metadata"]["benefit_summary"] = benefits[:200]
            doc["metadata"]["application_process"] = application_process
            doc["metadata"]["documents_required"] = documents_required
            doc["metadata"]["source_url"] = _clean_text(
                item.get("Official Website")
                or item.get("Application Form")
                or item.get("Order/Notice")
            )
        else:
            if "text" in item:
                doc["text"] = _clean_text(item["text"])
            elif "description" in item:
                doc["text"] = _clean_text(item["description"])
            elif "content" in item:
                doc["text"] = _clean_text(item["content"])

            if scheme_name:
                doc["metadata"]["scheme_name"] = scheme_name
            if category:
                doc["metadata"]["category"] = category
            if "source_url" in item:
                doc["metadata"]["source_url"] = _clean_text(item["source_url"])
            if "official_link" in item:
                doc["metadata"]["source_url"] = _clean_text(item["official_link"])
            if eligibility:
                doc["metadata"]["eligibility"] = eligibility
            if benefits:
                doc["metadata"]["benefits"] = benefits
            if application_process:
                doc["metadata"]["application_process"] = application_process

        if doc["text"]:
            documents.append(doc)

    return documents
