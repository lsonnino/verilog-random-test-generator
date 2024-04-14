def inverse(words):
    return words[::-1]

def ntsf(words):
    """
    The algorithm works as follows:
    - Create a dictionary with the first letter of each word as key, containing all the indices that start with the given letter
    - Create a new list of words, where each word alternates between the different keys
    - Check the list to find if there are still duplicates (if a key has more indices than the others)
    - Replace those elements somewhere in the list so that the list is correctly ordered
    """

    # Extract main parameters
    is_list = type(words[0]) == type([])
    n = len(words)
    first = {}

    # Sort indices by first letter
    for i, w in enumerate(words):
        if is_list:
            f = w[0][0]
        else:
            f = w[0]
        
        if f not in first:
            first[f] = [i]
        else:
            first[f].append(i)
    
    # Prepare for first re-ordering
    new_words = [None] * n
    keys = list(first.keys())
    n_k = len(keys)

    # Place words in the new list
    current_key = 0
    for i in range(n):
        if current_key >= n_k:
            current_key = 0

        key = keys[current_key]
        while len(first[key]) == 0:
            current_key += 1
            if current_key >= n_k:
                current_key = 0
            key = keys[current_key]
        index = first[key].pop(0)
        new_words[i] = words[index]

        current_key += 1
    
    # Check the list for duplicates
    duplicates_indices = []
    duplicates = []
    for i in range(n-1):
        if is_list:
            f1 = new_words[i][0][0]
            f2 = new_words[i+1][0][0]
        else:
            f1 = new_words[i][0]
            f2 = new_words[i+1][0]
        
        if f1 == f2:
            duplicates_indices.append(i)
            duplicates.append(new_words[i])
    
    # Remove duplicates from the list
    for i in reversed(duplicates_indices):
        del new_words[i]
    
    # Find somewhere to place each duplicate
    for d in duplicates:
        nn = len(new_words)
        if is_list:
            f = d[0][0]
        else:
            f = d[0]
        placed = False

        for i in range(nn-1):
            if is_list:
                f1 = new_words[i][0][0]
                f2 = new_words[i+1][0][0]
            else:
                f1 = new_words[i][0]
                f2 = new_words[i+1][0]
            
            if f1 != f and f2 != f:
                new_words.insert(i+1, d)
                placed = True
                break
        
        if not placed:
            new_words.append(d)

    return new_words

def always_different(words, retries=10):
    """
    Re-order words so that the starting letter of the last element of each word has a different starting letter than the first element of the next word.
    """

    # If each word only contains one element, result will be the same as ntsf (which is faster)
    if type(words[0]) != type([]):
        return ntsf(words)

    # Extract main parameters
    n = len(words)

    # Prepare for re-ordering
    new_words = []
    new_words.append(words[0])
    done = [False] * n
    done[0] = True
    placed = 1

    # Place words in the new list
    for _ in range(retries):
        for i in range(1, n):
            if done[i]:
                continue

            for j in range(placed):
                if (new_words[j][-1][0] != words[i][0][0]) and (new_words[j+1][0][0] != words[i][-1][0] if j+1 < len(new_words) else True):
                    new_words.insert(j+1, words[i])
                    done[i] = True
                    placed += 1
                    break
    
        # Check if it's already done
        if placed == n:
            return new_words
    
    # Place the remaining words
    print(f'Warning: Could not reorder {n - placed} words in the list. Some words at the end will not meet the reordering condition')
    for i in range(1, n):
        if not done[i]:
            new_words.append(words[i])

    return new_words

if __name__ == '__main__':
    # Test the algorithms
    words = [['000', '100'], ['100', '200'], ['200', '300'], ['300', '000'], ['100', '000'], ['300', '200'], ['200', '100'], ['000', '300'], ['200', '000'], ['300', '100'], ['000', '200'], ['100', '300']]
    print('Original:', words)
    #print('Inverse:', inverse(words))
    #print('NTSF:', ntsf(words))
    print('Always Different:', always_different(words))
