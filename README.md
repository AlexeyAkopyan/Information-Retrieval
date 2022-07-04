# InformationRetrievalCourse
The Information Retrieval course practical tasks

## Requirements 
To execute the first task, a new [reddit app](https://www.reddit.com/prefs/apps) need to created. After getting the **client_id**, **client_secret** and **user_agent**, they need to be inserted in **config.yaml** file.
The required python packages are listed in `requirements.txt`.

## Step1
Realization of a web-crawler for document collecting from [Reddit](https://www.reddit.com/). Besides text of documents the additional metadata is required, e.g. the author's name, topic tags,
score and publication date. 

The collected documents need to be cleared of irrelevant data, e.g. the external links and punctuation marks. 

After preprocessing the required volume of collection is at least 100 000 unique documents. The text size for each document need to be at least 2000 characters.
##

Run `task1.py` to execute the task.

**In case of interrupting running** `task1.py`, after the new launch it will continue to collect documents starting from the first subreddit afther the last presented one in the data file. 

The code for collecting data can be found in `collect.py` file, for clearing collected data - in `preprocess.py` file. 
After execution both the raw data and the preprocessed data will be located in `./data/` directory. 

As document submissions and comments to a submission is considetered.

**Data collection field**: 
- author: the document author's name
- is_submission: whether the document is a submission instance or a comment one;
- is_submitter: for comment, whether the comment was posted by the author of submission that the comment belong to;
- num_comments: for submission, the number of comments on the submission;
- over_18: whether or not the document was marked as NSFW;
- tag: the name of tag that the document was marked or None otherwise;
- text: the text of the submission or comment;
- time_created: time the submission or comment was created;
- score: the number of upvotes for the document;
- subreddit: the name of the subreddit where document was created.

**Data**

The raw and preprocessed collections can be found [here](https://drive.google.com/drive/folders/1I5b56tboHt3DdMA8mvroL7GVvomEHBZ9?usp=sharing).
