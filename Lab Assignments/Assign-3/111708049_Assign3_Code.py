import os
import re
import numpy as np
from sklearn.preprocessing import normalize
import pandas as pd

def handle_sentends(tokens) :
    n = len(tokens)
    i = 0
    while(i < n) :
        token = tokens[i]
        for end in sent_ends :
            if end in token :
                if(len(token) != 1):
                    tokens[i] = token.replace(end, "") 
                    tokens.insert(i+1, end+"_SENT")
                    n += 1
                    i += 1
                else :
                    tokens[i] = end+"_SENT"
        i += 1
    return tokens

def preprocess(sent) :
    sent = re.sub(rep_regex, "", sent)
    sent = sent.replace("<s>P", "<s>")
    sent = sent.replace("<s> P", "<s>")
    sent = sent.replace("</s>P", "</s>")
    sent = sent.replace("<\s>", "</s>")
    sent = sent.replace("</s><s>", "</s> <s>")
    sent = sent.replace("|P", "")
    sent = sent.replace("aux", "AUX")
    sent = sent.replace(" WQ", "_WQ")
    sent = sent.replace(" QW", "_QW")
    sent = sent.replace(" UT", "_UT ")
    sent = sent.replace(" XC", "_XC")
    sent = sent.replace(" QF", "_QF")
    sent = sent.replace(" DEM", "_DEM")
    sent = sent.replace(" UT", "_UT")
    sent = sent.replace(" QO", "_QO")
    sent = sent.replace(" RDP", "_RDP")
    sent = sent.replace("SP", "_SP")
    sent = sent.replace("NST", "_NST")
    sent = sent.replace("fW", "FW")
    #sent = sent.replace("IN", "_IN")
    for tag in add_space :
        sent = sent.replace(tag, tag+" ")
    if(sent[0:3] == "<s>") :
        sent = "<s> "+sent[3:]
    elif(sent[1:4] == "<s>") :
        sent = "<s> "+sent[4:]
    else :
        sent = "<s> "+sent
    if(sent[-5:-1] == "</s>") :
        if(sent[-6] != " ") :
            sent = sent[:-5]+" </s>"
    elif(sent[-4:] == "</s>") :
        if(sent[-5] != " ") :
            sent = sent[:-4] +" </s>"
    else :
        sent = sent + " </s>"
    return sent

def get_words_and_tags(tokens) :
    words = []
    tags = []
    for sent_tokens in tokens :
        sent_words = []
        sent_tags = []
        for i in range(len(sent_tokens)) :
            token = sent_tokens[i]
            if(token.find("_") != -1) :
                pos = token.find("_")
                sent_words.append(token[:pos])
                sent_tags.append(token[pos+1:])
            elif(token == "<s>"):
                sent_words.append(token)
                sent_tags.append("START")
            elif(token == "</s>"):
                sent_words.append(token)
                sent_tags.append("END")   
            else :
                sent_words.append(token)
                sent_tags.append("UN")
        words.append(sent_words)
        tags.append(sent_tags)
    return words, tags
def get_ngrams(n, tokens) :
    ngrams = []
    for token in tokens :
        if(len(token) < n) :
            continue
        else :
            i = 0
            while(i < len(token)-n+1) :
                ngrams.append(token[i:i+n])
                i += 1
    return ngrams

def get_freq_dict(ngrams) :
    ngram_freq = {}
    for ngram in ngrams :
        key = ' '.join([str(elem) for elem in ngram])
        if key not in ngram_freq :
            ngram_freq[key] = 1
        else :
            ngram_freq[key] += 1
    return ngram_freq

def get_freq_freq(ngram_freq) :
    freq_freq = {}
    for ngram, freq in ngram_freq.items() :
        if freq in freq_freq :
            freq_freq[freq] += 1
        else :
            freq_freq[freq] = 1
    return freq_freq

def write_to_file(ngrams, fname) :
    f = open(fname, "w")
    to_write = ""
    for terms in ngrams :
        for term in terms :
            to_write += (term+" ")
        to_write = to_write[:-1]
        to_write += "\n"
    f.write(to_write)
    f.close()

def get_perplexity(test_data, hindi_words, ngram=2) :
    #Using good-turing
    test_ngrams = get_ngrams(ngram, test_data)
    hindi_ngrams = get_ngrams(ngram, hindi_words)
    N = len(test_ngrams)
    ngram_freq = get_freq_dict(hindi_ngrams)
    #print(ngram_freq)
    freq_freq = get_freq_freq(ngram_freq)
    #print(freq_freq)
    perp = 1
    for ngram in test_ngrams :
        ngram = ' '.join([str(elem) for elem in ngram])
        if ngram in ngram_freq :
            freq = ngram_freq[ngram]
            if freq+1 not in freq_freq :
                perp *= 1
            else :
                perp *= ((freq+1)*freq_freq[freq+1]/freq_freq[freq])
        else :
            perp *= (freq_freq[1]/N)
    if perp == 0 :
        return 999999999
    #print(perp)
    perp = 1/perp
    perp = pow(perp, 1/len(test_ngrams))
    return perp
def create_tag_transition_matrix(hindi_tags) :
    hindi_tags_list = [item for sublist in hindi_tags for item in sublist]
    tags = list(set(hindi_tags_list))

    tag_bigrams = get_ngrams(2, hindi_tags)
    tag_bigrams_freq = get_freq_dict(tag_bigrams)
    #print(tag_bigrams_freq)
    TTP = np.zeros((len(tags), len(tags)))
    for i in range(len(tags)) :
        for j in range(len(tags)) :
            tag_pair = tags[i]+" "+tags[j]
            if tag_pair in tag_bigrams_freq :
                TTP[i][j] = tag_bigrams_freq[tags[i]+" "+tags[j]]
    TTP = (TTP.T/TTP.sum(axis=1)).T
    return TTP

def create_word_emission_file(hindi_tags, hindi_words) :
    word_emission = {}
    tags_count = {}
    word_tags = {}
    tags_list = [item for sublist in hindi_tags for item in sublist]
    #print(len(tags_list))
    for tag in tags_list :
        if(tag not in tags_count) :
            tags_count[tag] = 1
        else :
            tags_count[tag] += 1
    for i in range(len(hindi_tags)) :
        for j in range(len(hindi_tags[i])) :
            key = hindi_words[i][j] +","+ hindi_tags[i][j]
            if key not in word_tags :
                word_tags[key] = 1
            else :
                word_tags[key] += 1
    for key, count in word_tags.items() :
        #print(key)
        pair = key.split(',')
        tag = pair[1]
        word_emission[key] = word_tags[key]/tags_count[tag]
        #print(word_tags[key], tags_count[tag], word_emission[key])
    return word_emission

references = "[?.,]*\[?[0१२३४५६७८९०][१२३४५६७८९०0]*\]"
extras = "[\)\(]"
eclipse = "\.+"
puncts = "[,\-']"
rep = [references, extras, puncts]
rep_regex = '|'.join('%s' % val for val in rep)
add_space = []
sent_ends = ["?", "!", ".", "।", "|"]
add_space = ["V_VB", "N_NN", "RD_PUNC", "JJ ", "NNP", "N_NNP"]

hindi_tokens = []
files = os.listdir("Labeled-Hindi-Corpus")
for file in files:
    name = file
    file = "Labeled-Hindi-Corpus/"+file
    f = open(file, "r")
    sents = f.readlines()
    for sent in sents :
        sent = sent.strip()
        sent = preprocess(sent)
        hindi_tokens.append(handle_sentends(sent.split()))
    f.close()

hindi_words, hindi_tags = get_words_and_tags(hindi_tokens)
hindi_tags_list = [item for sublist in hindi_tags for item in sublist]
hindi_words_list = [item for sublist in hindi_words for item in sublist]
tags = list(set(hindi_tags_list))
"""
fname = "unigram-output.txt"
unigrams = get_ngrams(1, hindi_words)
write_to_file(unigrams, fname)
fname = "bigram-output.txt"
bigrams = get_ngrams(2, hindi_words)
write_to_file(bigrams, fname)
fname = "trigram-output.txt"
trigrams = get_ngrams(3, hindi_words)
write_to_file(trigrams, fname)
fname = "4gram-output.txt"
4grams = get_ngrams(4, hindi_words)
write_to_file(4grams, fname)
fname = "5gram-output.txt"
5grams = get_ngrams(5, hindi_words)
write_to_file(5grams, fname)
"""
TTP = create_tag_transition_matrix(hindi_tags)
f = open("111708049-TTP.txt", "w")
for i in range(len(tags)) :
    for j in range(len(tags)) :
        f.write(tags[i]+" "+tags[j]+str(TTP[i][j])+"\n")
f.close()
word_emission = create_word_emission_file(hindi_tags, hindi_words) 
#print(word_emission)
f = open("111708049-WEP.txt", "w") 
for key, value in word_emission.items() :
    to_write = key+" "+str(value)+"\n"
    f.write(to_write)
f.close()   
f = open("test.txt", "r")
sents = f.readlines()
test_tokens = []
for sent in sents :
    sent = sent.strip()
    sent = preprocess(sent)
    test_tokens.append(sent.split())
perplexity = get_perplexity(test_tokens, hindi_words, ngram=1)
print("Perplexity of unigram model = "+str(perplexity))
perplexity = get_perplexity(test_tokens, hindi_words, ngram=2)
print("Perplexity of bigram model = "+str(perplexity))
perplexity = get_perplexity(test_tokens, hindi_words, ngram=3)
print("Perplexity of trigram model = "+str(perplexity))
perplexity = get_perplexity(test_tokens, hindi_words, ngram=4)
print("Perplexity of 4gram model = "+str(perplexity))
perplexity = get_perplexity(test_tokens, hindi_words, ngram=5)
print("Perplexity of 5gram model = "+str(perplexity))
