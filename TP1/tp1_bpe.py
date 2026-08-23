import re
from collections import Counter
from corpus import CORPUS_A, CORPUS_B
import time

def normalize(text: str):
    return re.findall(r"\b\w+\b", text)

def tokenize_corpus(text: str):
    words = normalize(text)
    tokens = []
    for w in words:
        tokens.extend(w)
        tokens.append("</w>")
    return tokens

def detail_corpus(text: str):
    words = normalize(text)
    print("Vocabulario inicial:")
    print(set(words))
    print(f"Cantidad total de palabras: {len(set(words))}")

def count_pairs(tokens):
    freqs = pairs_tokens(tokens)
    print("Frecuencia de pares de tokens:")
    for (p1, p2), count in freqs.items():
        print(f"('{p1}','{p2}') -> {count}")

def pairs_tokens(tokens):
    freqs = Counter()
    for i in range(len(tokens) - 1):
        if "</w>" in tokens[i]:
            continue
        pair = (tokens[i], tokens[i + 1])
        freqs[pair] += 1

    return freqs

def most_frequent_pair(tokens):
    freqs = pairs_tokens(tokens)
    print("Los 10 pares de tokens más frecuentes:")
    for (p1, p2), count in freqs.most_common(10):
        print(f"('{p1}','{p2}') -> {count}")

def merge_most_frequent_pair(tokens):
    freqs = pairs_tokens(tokens)
    if not freqs:
        print("No hay pares de tokens para fusionar.")
        return tokens, None
    
    (p1, p2), _ = freqs.most_common(1)[0]
    tokens_merged = merge_pair((p1, p2), tokens)

    print()
    print(f"El par más frecuente fusionado es: ({p1}{p2})\n")
    print(f"Corpus antes de la fusión:\n{tokens}\n")
    print(f"Corpus después de la fusión:\n{tokens_merged}\n")

    return tokens_merged, (p1, p2)

def merge_pair(pair_to_merge, tokens):
    p1, p2 = pair_to_merge
    new_tokens = []
    i = 0
    
    while i < len(tokens):
        if i < len(tokens) - 1 and tokens[i] == p1 and tokens[i + 1] == p2:
            new_tokens.append(p1 + p2)
            i += 2
        else:
            new_tokens.append(tokens[i])
            i += 1
            
    return new_tokens

def train_bpe(corpus, num_merges):
    total_tokens = len(tokenize_corpus(corpus))

    start_time = time.time()

    tokenized_corpus = tokenize_corpus(corpus)
    corpus = tokenized_corpus
    for i in range(num_merges):
        tokenized_corpus, pair = merge_most_frequent_pair(tokenized_corpus)
        if pair is None:
            print("No se pueden realizar más fusiones.")
            break
        p1, p2 = pair
        corpus.append(p1 + p2)
        print(f"Merge {i + 1}/{num_merges} completado.\n")

    elapsed_time = time.time() - start_time

    print("Entrenamiento BPE completado.")
    print(f"Tiempo de entrenamiento BPE: {elapsed_time:.2f} segundos")
    print("Cantidad total de tokens inicial:", total_tokens)
    total_tokens = len(tokenized_corpus)
    print("Cantidad total de tokens final:", total_tokens)
    cant_words = sum(1 for word in tokenized_corpus if word.endswith("</w>"))
    avg_tokens_per_word = total_tokens / cant_words
    print(f"Cantidad promedio de tokens por palabra: {avg_tokens_per_word:.2f}")
    vocabulario = set(tokenized_corpus)
    print("Tamaño del vocabulario final:", len(vocabulario))

    return sorted(set(corpus))

def apply_tokens(word: str, tokens):
    tokenized_word = tokenize_corpus(word)
    cant_tokens = len(tokenized_word)
    max_len = max(len(token) for token in tokens)
    result = []
    i = 0

    while i < cant_tokens:
        j = min(max_len, cant_tokens - i)
        while j > 0 and "".join(tokenized_word[i:i + j]) not in tokens:
            j -= 1
        
        if j == 0:
            result.append(tokenized_word[i])
            i += 1
        else:
            result.append("".join(tokenized_word[i:i + j]))
            i += j

    return result
    
def main():
    # "1)"
    # detail_corpus(CORPUS_A)
    # detail_corpus(CORPUS_B)
    # "2)"
    # print("corpus tokenizado:")
    # print(tokenize_corpus(CORPUS_A))
    # "3)"
    # count_pairs(tokenize_corpus(CORPUS_A))
    # most_frequent_pair(tokenize_corpus(CORPUS_A))
    # count_pairs(tokenize_corpus(CORPUS_B))
    # most_frequent_pair(tokenize_corpus(CORPUS_B))
    # "4)"
    # merge_most_frequent_pair(tokenize_corpus(CORPUS_A))
    # "5)"
    # train_bpe(CORPUS_A, 50)
    # "6"
    # train_bpe(CORPUS_A, 50)
    # train_bpe(CORPUS_A, 30)
    # train_bpe(CORPUS_A, 20)
    # train_bpe(CORPUS_A, 10)
    "7)"
    tokens = train_bpe(CORPUS_A, 30)
    print("tokens:", tokens)
    print("tokens aplicados:", apply_tokens("perritos y gato", tokens))

if __name__ == "__main__":
    main()
