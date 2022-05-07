import re


def preprocess_text(text: str) -> str:
    """
    Execute preprocessing of text. Return text consists only of lower litters, digits and white spaces.
    All links starting with "http" or "www" will be removed.
    The parts of the words around the apostrophe will be merged and the last will be removed.

    Parameters
    ----------
    text: str
        The string to preprocess

    Return
    ------
    str
        The preprocessed string
    """
    text = re.sub("(http|www\.)\S+", " ", text.lower())
    text = re.sub("[‘’‛']", '', text)
    text = re.sub("([\w!?.,]\'[^\w])|([^\w]\'\w)|(^\'\w)", '', text)
    text = re.sub("[^a-z0-9]", ' ', text)
    text = re.sub("\s+", ' ', text)
    return text.strip()
