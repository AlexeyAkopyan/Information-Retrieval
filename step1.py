import logging

import pandas as pd
import yaml

from collect_data import collect_reddit_dataset
from preprocess import preprocess_text

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)8.8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("./logs/task1.log")],
)

if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    # Collecting data
    logger.info("Starting collecting data")
    collect_reddit_dataset(cfg)
    logger.info(f"Data were successfully collected and stored in {cfg['save_raw_data']} file")

    # Preprocessing raw data
    logger.info("Starting preprocessing collected data")
    dataset = pd.read_csv(cfg["paths"]["save_raw_data"])
    logger.info(f"Before preprocessing there are {len(dataset)} unique documents")
    dataset["text"] = dataset["text"].apply(preprocess_text)
    dataset["tag"] = dataset["tag"].apply(str).apply(preprocess_text)
    dataset = dataset[dataset["text"].apply(len) > cfg["min_length"]]
    dataset["topic"] = dataset["subreddit"].map(cfg["subreddit_names"])
    dataset.drop_duplicates("text", keep="first", inplace=True)
    dataset.to_csv(cfg["paths"]["save_preprocessed_data"], header=True, index=False)
    logger.info(f"Preprocessed data were stored in {cfg['paths']['save_preprocessed_data']} file")
    logger.info(f"After preprocessing there are {len(dataset)} unique documents")

