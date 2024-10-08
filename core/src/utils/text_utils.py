from typing import List, Callable
from collections import Counter
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
import math

def window_slide_split(text: str, step: int = 20, chunk_size: int = 200) -> List[str]:
    '''
        Split text into equal chunks by applying window sliding method

        @param text input string
        @param step the step size of each chunk
        @param chunk_size the size of each chunk
    '''
    slides = []
    words = text.split(" ")
    i = 0
    num_words = len(words)
    isRun = True
    while isRun:
        if i >= num_words:
            break
        if i+chunk_size > num_words:
            isRun = False
            lim = num_words
        else:
            lim = i+chunk_size
        str_tmp = " ".join(words[i: lim])
        slides.append(str_tmp)
        i += step
    return slides

def window_slide_chunks(text: str, step_ratio: float, chunks: int):
    '''
        Split text into number of "chunks" using window sliding method

        @param text: the input string
        @param step_ratio: the ratio of step
        @param chunks: the number of return elements
    '''
    text_size = len(text.split(" "))
    chunk_size = text_size // chunks
    step = chunk_size*step_ratio
    return window_slide_split(text=text, step=math.ceil(step), chunk_size=chunk_size-step)

def create_splitter(
        chunk_size: int = 460, overlap: int = 20, 
        word_len_func: Callable = None,
        separators: List[str]= None) -> RecursiveCharacterTextSplitter:
    """
        get an instance of a text splitter
    """
    if word_len_func == None:
        word_len_func = lambda e: len(e.split(" "))
    if separators == None:
        separators = ["\n\n\n","\n\n", "\n", "."]
    text_splitter = RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=chunk_size, chunk_overlap=overlap, 
        length_function=word_len_func, is_separator_regex=False
    )
    return text_splitter

def try_split_texts(texts: List[str], splitter: RecursiveCharacterTextSplitter):
    dist = []
    db = []
    lengths = []
    for txt in texts:
        docs = splitter.create_documents([txt])
        dist.append(len(docs))
        db.extend(docs)
        lengths.extend([len(d.page_content.split(" ")) for d in docs])
    dist_np = np.array(dist)
    print(f"From {len(texts)} texts -> {len(db)}")
    print(f"Distribution: {Counter(dist)}")
    print("== About the splits ==")
    print("The mean of the splits is:", np.mean(dist_np))
    print("The median of the splits is:", np.median(dist_np))
    print("The max of the split is:", np.max(dist_np))
    print("The min of the split is:", np.min(dist_np))
    # splits length
    print("== About the splits length ==")
    length_np = np.array(lengths)
    print("The max of the split length is:", np.max(length_np))
    print("The min of the split length is:", np.min(length_np))
    print("The mean of the split length is:", np.mean(length_np))
    print("The median of the split length is:", np.median(length_np))
    return db,dist_np,length_np