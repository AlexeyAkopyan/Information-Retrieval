import logging
import os
import re
from typing import Dict, Any, List

import pandas as pd
import praw
from praw.models.listing.generator import ListingGenerator
from praw.models.reddit.comment import Comment
from praw.models.reddit.submission import Submission
from prawcore.exceptions import Forbidden

logger = logging.getLogger(__name__)


def parse_submission(submission: Submission) -> Dict[str, Any]:
    """
    Get the description of the submission

    Parameters
    ----------
    submission: praw.models.submission.Submission
        The submission to describe

    Return
    -------
    dict
        Dict describing the submission
    """
    return {
        "author": submission.author.name if submission.author is not None else None,
        "is_submission": True,
        "is_submitter": True,
        "num_comments": submission.num_comments,
        "over_18": submission.over_18,
        "tag": submission.link_flair_text,
        "text": re.sub(",", "", submission.title + " " + submission.selftext),
        "time_created": submission.created_utc,
        "score": submission.score,
        "subreddit": submission.subreddit.display_name,
    }


def parse_comment(comment: Comment) -> Dict[str, Any]:
    """
    Get the description of the comment

    Parameters
    ----------
    comment: praw.models.comment.Comment
        The comment to describe

    Return
    ------
    dict
        Dict describing the comment
    """
    return {
        "author": comment.author.name if comment.author is not None else None,
        "is_submission": False,
        "is_submitter": comment.is_submitter,
        "num_comments": None,
        "over_18": None,
        "tag": None,
        "text": re.sub(",", "", comment.body),
        "time_created": comment.created_utc,
        "score": comment.score,
        "subreddit": comment.subreddit.display_name,
    }


def get_subreddit_generators(reddit: praw.Reddit, subreddit_name: str, limit: int = 1000) -> List[ListingGenerator]:
    """
    Get the list of praw.models.listing.generator.ListingGenerator to pass through submissions and comments.
    Each generator returns limit number of submissions or comments sorted by specific way.
    Sort types: top, hot, new, gilded and controversial.

    Parameters
    ----------
    reddit: praw.Reddit
        The Reddit class instance providing access to Reddit's API
    subreddit_name: str
        The subreddit name to collect submissions and comments from
    limit: int
        The number of submissions and comments to get from each sort type. Max number - 1000

    Return
    ------
    praw.models.listing.generator.ListingGenerator
        The list of a submission or comment generators
    """
    limit = min(1000, limit)
    return [
        reddit.subreddit(subreddit_name).top(limit=limit),
        reddit.subreddit(subreddit_name).hot(limit=limit),
        reddit.subreddit(subreddit_name).new(limit=limit),
        reddit.subreddit(subreddit_name).gilded(limit=limit),
        reddit.subreddit(subreddit_name).controversial(limit=limit),
    ]


def collect_reddit_dataset(cfg: Dict) -> None:
    """
    Collect reddit submissions and comment from cfg[subreddit_names] subreddits

    Parameters
    ----------
    cfg: Dict
        The dict with configuration description
    """
    subreddit_names = cfg["subreddit_names"]

    reddit = praw.Reddit(client_id=cfg["reddit"]["client_id"],
                         client_secret=cfg["reddit"]["client_secret"],
                         user_agent=cfg["reddit"]["user_agent"])

    save_path = cfg["paths"]["save_raw_data"]

    min_length = cfg["min_length"]
    column_names = cfg["column_names"]
    total_n_submissions = 0
    if os.path.exists(save_path):
        prev_submissions = pd.read_csv(save_path)
        total_n_submissions = len(prev_submissions)
        prev_subreddit_names = prev_submissions["subreddit"].unique()
        if len(prev_subreddit_names):
            subreddit_names = subreddit_names[subreddit_names.index(prev_subreddit_names[-1]) + 1:]
        logger.info(f"File {cfg['paths']['save_raw_data']} exists."
                    f" Continue collecting from {subreddit_names[0]} subreddit")
        del prev_submissions
    else:
        pd.DataFrame(columns=column_names).to_csv(save_path, header=True, index=False)

    for subreddit_name in subreddit_names:
        new_submissions = {column_name: [] for column_name in column_names}
        subreddit_gens = get_subreddit_generators(reddit, subreddit_name)
        try:
            for subreddit_gen in subreddit_gens:
                for submission in subreddit_gen:
                    if isinstance(submission, Submission):
                        parsed_submission = parse_submission(submission)
                    elif isinstance(submission, Comment):
                        parsed_submission = parse_comment(submission)
                    else:
                        continue
                    if len(parsed_submission["text"]) > min_length:
                        for column_name in column_names:
                            new_submissions[column_name].append(parsed_submission[column_name])
        except Forbidden as err:
            logger.warning(f"Next error was caught: {err}")
        finally:
            if new_submissions["author"]:
                new_submissions = pd.DataFrame(new_submissions)
                new_submissions.drop_duplicates('text', keep='first', inplace=True)
                # new_submissions.to_csv(f"{save_path[:-4]}_{subreddit_name}.csv")
                new_submissions.to_csv(save_path, mode="a", header=False, index=False)
            logger.info(f"From {subreddit_name} collected {len(new_submissions['author'])} new submissions")
            total_n_submissions += len(new_submissions["author"])
            logger.info(f"Total number of collected submissions: {total_n_submissions}")
