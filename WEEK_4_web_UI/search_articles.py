def read_file(file_name):
    with open(file_name, 'r', encoding='UTF-8') as f:
        file_chunk = f.read().replace('\n', ' ')    # replace all newline characters with single space
        documents = file_chunk.split('</article>')  # split the file(str) into list
        del documents[-1]                           # remove the last element, which is empty (which was caused by an </article> in the END of the document)
    return documents    # type: list of strings
