from random import choice

alphabet = '0123456789abcdef'

def gen_one(lengths, alphabet=alphabet, first_custom_alphabet=None):
    w = []
    for i, l in enumerate(lengths):
        if type(alphabet) == type(''):
            use_alpha = alphabet
        else:
            use_alpha = alphabet[i]
        
        if first_custom_alphabet is not None and type(first_custom_alphabet) != type(''):
            use_fca = first_custom_alphabet[i]
        else:
            use_fca = first_custom_alphabet

        if use_fca is not None:
            new_word = choice(use_fca)
            new_word += ''.join(choice(use_alpha) for _ in range(l - 1))
        else:
            new_word = ''.join(choice(use_alpha) for _ in range(l))
        
        w.append(new_word)
    return w

def bits_to_len(bits, alphabet=alphabet):
    n = len(bits)
    lengths = [0] * n
    fca = [None] * n

    for i, b in enumerate(bits):
        if b % 4 == 0:
            lengths[i] = b // 4
            fca[i] = None
        else:
            lengths[i] = (b // 4) + 1
            limit = 2 ** (b % 4)
            fca[i] = alphabet[:limit]
    
    return lengths, fca

def gen_words(n, lengths, out, alphabet=alphabet, first_custom_alphabet=None, filter=None, filter_retries=100):
    output = []
    for _ in range(n):
        if filter is not None:
            for fr in range(filter_retries+1):
                w = gen_one(lengths, alphabet, first_custom_alphabet=first_custom_alphabet)
                if filter(w):
                    break
                else:
                    continue
            if fr == filter_retries:
                print('Warning: Filter validation failed after {} retries'.format(filter_retries))
        else:
            w = gen_one(lengths, alphabet, first_custom_alphabet=first_custom_alphabet)
        output.append(w)

    if out is not None:
        with open(out, 'w') as f:
            for w in output:
                f.write(' '.join(w) + '\n')
    
    return output

if __name__ == '__main__':
    w = gen_words(10, [3, 4], 'words.txt', alphabet=['01', '0123456789abcdef'])
    print(w)
    print()

    w = gen_words(3, [3, 4], None)
    print(w)
    print()

    w = gen_words(4, [3, 4], None, first_custom_alphabet=[None, '01'])
    print(w)
