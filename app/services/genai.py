import logging
from typing import List, Dict
from transformers import pipeline, Pipeline
logging.basicConfig(level=logging.INFO)
# Set up logger
logger = logging.getLogger(__name__)

# Initialize the text generation pipeline once
def get_summarizer() -> Pipeline:
    """
    Initialize and return the text generation pipeline.
    """
    return pipeline("text-generation", model="distilgpt2")

summarizer: Pipeline = get_summarizer()


def format_asset_summary(data: List[Dict[str, float]]) -> str:
    """
    Create a summary text from a list of asset metric dictionaries.
    """
    return " ".join(
        f"{asset['symbol']} had a {asset['change_percent_24h']}% change in the last 24 hours, "
        f"with a weekly average price of ${asset['average_price_7d']}."
        for asset in data
    )


def generate_summary(data: List[Dict[str, float]]) -> str:
    """
    Generate a summary based on the asset metrics using a text generation model.

    Args:
        data: A list of dictionaries, each containing asset metrics.

    Returns:
        A generated summary string.
    """
    try:
        logger.info("Generating summary from asset data.")

        input_text: str = format_asset_summary(data)
        max_tokens: int = 200

        results = summarizer(
            input_text,
            max_length=max_tokens,
            min_length=50,
            length_penalty=2.0,
            no_repeat_ngram_size=3,
        )

        logger.info("Summary generation successful.")
        return results[0]["generated_text"]

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise ValueError("Error generating summary.") from e
