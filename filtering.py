def pass_all(word):
    return True

def dffe(word):
    """
    Stands for "Different First of First Element"
    Takes the length of the first element of the word. Then takes all the other elements of the same size. The first letter of those elements must be different
    """

    n = len(word[0])

    for w in word[1:]:
        if (len(w) == n) and (w[0] == word[0][0]):
            return False
    
    return True
