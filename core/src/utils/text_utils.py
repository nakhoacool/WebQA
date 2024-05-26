from typing import List

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