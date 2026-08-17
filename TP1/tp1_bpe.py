import re
from collections import Counter
from corpus import CORPUS_A, CORPUS_B
import time

def normalize(text: str):
    return sorted(re.findall(r"\b\w+\b", text.lower()))

def tokenize_word(word: str):
    return list(word) + ["</w>"]

def tokenize_corpus(text):
    words = normalize(text)
    return [tokenize_word(w) for w in words]

def detail_corpus(text: str):
    words = normalize(text)
    print("Vocabulario inicial:")
    print(words)
    print(f"Cantidad total de palabras: {len(words)}")

def count_pairs(tokenized_words):
    freqs = pairs_tokens(tokenized_words)
    print("Frecuencia de pares de tokens:")
    for (p1, p2), count in freqs.items():
        print(f"('{p1}','{p2}') -> {count}")

def pairs_tokens(tokenized_words):
    freqs = Counter()
    for word_tokens in tokenized_words:
        for i in range(len(word_tokens) - 1):
            pair = (word_tokens[i], word_tokens[i + 1])
            freqs[pair] += 1

    return freqs

def most_frequent_pair(tokenized_words):
    freqs = pairs_tokens(tokenized_words)
    print("Los 10 pares de tokens más frecuentes:")
    for (p1, p2), count in freqs.most_common(10):
        print(f"('{p1}','{p2}') -> {count}")

def merge_most_frequent_pair(tokenized_words):
    freqs = pairs_tokens(tokenized_words)
    if not freqs:
        print("No hay pares de tokens para fusionar.")
        return tokenized_words, None
    
    (p1, p2), _ = freqs.most_common(1)[0]
    tokenized_words_merged = merge_pair((p1, p2), tokenized_words)

    print()
    print(f"El par más frecuente fusionado es: ({p1}{p2})\n")
    print(f"Corpus antes de la fusión:\n{tokenized_words}\n")
    print(f"Corpus después de la fusión:\n{tokenized_words_merged}\n")

    return tokenized_words_merged, (p1, p2)

def merge_pair(pair_to_merge, tokenized_words):
    p1, p2 = pair_to_merge
    new_token = p1 + p2
    new_tokenized_words = []

    for word_tokens in tokenized_words:
        new_word = []
        i = 0
        while i < len(word_tokens):
            if i < len(word_tokens) - 1 and word_tokens[i] == p1 and word_tokens[i + 1] == p2:
                new_word.append(new_token)
                i += 2
            else:
                new_word.append(word_tokens[i])
                i += 1
        new_tokenized_words.append(new_word)

    return new_tokenized_words

def train_bpe(corpus, num_merges):
    total_tokens = sum(len(word) for word in tokenize_corpus(corpus))

    start_time = time.time()

    merges = []
    tokenized_corpus = tokenize_corpus(corpus)
    for i in range(num_merges):
        tokenized_corpus, best_pair = merge_most_frequent_pair(tokenized_corpus)
        if best_pair is None:
            print("No se pueden realizar más fusiones.")
            break
        merges.append(best_pair)
        print(f"Merge {i + 1}/{num_merges} completado.\n")

    elapsed_time = time.time() - start_time
    
    print("Entrenamiento BPE completado.")
    print(f"Tiempo de entrenamiento BPE: {elapsed_time:.2f} segundos")
    print("Cantidad total de tokens inicial:", total_tokens)
    total_tokens = sum(len(word) for word in tokenized_corpus)
    print("Cantidad total de tokens final:", total_tokens)
    avg_tokens_per_word = total_tokens / len(tokenized_corpus)
    print(f"Cantidad promedio de tokens por palabra: {avg_tokens_per_word:.2f}")
    vocabulario = set(token for word in tokenized_corpus for token in word)
    print("Tamaño del vocabulario final:", len(vocabulario))

    return merges

def apply_merges(word: str, merges):
    tokens = tokenize_corpus(word)
    for pair in merges:
        tokens = merge_pair(pair, tokens)

    print()
    print(tokens)
    return tokens
    
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
    merges = train_bpe(CORPUS_A, 30)
    print("merges:", merges)
    apply_merges("perritos", merges)

if __name__ == "__main__":
    main()
