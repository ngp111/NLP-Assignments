import nltk
from nltk.tag.util import untag
from sklearn_crfsuite import CRF
from sklearn_crfsuite import metrics

def features(sentence, index):
    word = sentence[index]
    
    is_numeric = sentence[index][0].isdigit()
    is_joint = '-' in sentence[index]
    
    is_first = index == 0
    is_last = index == len(sentence) - 1
    
    is_first = index==0
    is_last = index==len(sentence)-1
    
    is_capitalized = sentence[index][0].upper() == sentence[index][0]
    is_all_caps = sentence[index].upper() == sentence[index]
    is_all_lower = sentence[index].lower() == sentence[index]
    is_abbreviation = sentence[index][1:].lower() != sentence[index][1:]
    
    prefix1 = sentence[index][0]
    prefix2 = sentence[index][:2]
    prefix3 = sentence[index][:3]
    prefix4 = sentence[index][:4]
    
    suffix1 = sentence[index][-1]
    suffix2 = sentence[index][-2:]
    suffix3 = sentence[index][-3:]
    suffix4 = sentence[index][-4:]
    
    #1-gram
    prev_word = '' if index == 0 else sentence[index - 1]
    prev_prev_word = '' if index<2 else sentence[index-2]
    next_word = '' if index == len(sentence) - 1 else sentence[index + 1]
    next_next_word = '' if index > len(sentence) - 3 else sentence[index+2]
    
    #Bigrams
    prevToprev_prev = prev_prev_word+" "+prev_word
    prev_curr = prev_word+" "+word
    curr_next = word+" "+next_word
    next_nextTonext = next_word+" "+next_next_word
    
    #Trigrams
    prevToprev_prev_curr = prev_prev_word+" "+prev_word+" "+word
    prev_curr_next = prev_word+" "+word+" "+next_word
    curr_next_nextTonext = word+" "+next_word+" "+next_next_word
    
    #4-grams
    prevToprev_prev_curr_next = prev_prev_word+" "+prev_word+" "+word+" "+next_word
    prev_curr_next_nextTonext = prev_word+" "+word+" "+next_word+" "+next_next_word
    
    #5-grams
    context = prev_prev_word+" "+prev_word+" "+word+" "+next_word+" "+next_next_word
    
    #current word and history words
    prev_words = ['']*9
    j = 0
    for i in range(index-1, -1, -1) :
        prev_words[j] = sentence[i]
        j += 1
        if(j>8) :
            break
    word_prev1 = prev_words[0]
    word_prev2 = prev_words[1]
    word_prev3 = prev_words[2]
    word_prev4 = prev_words[3]
    word_prev5 = prev_words[4]
    word_prev6 = prev_words[5]
    word_prev7 = prev_words[6]
    word_prev8 = prev_words[7]
    word_prev9 = prev_words[8]
    
    #current word and future words
    next_words = ['']*9
    j = 0
    for i in range(index+1, len(sentence)) :
        next_words[j] = sentence[i]
        j += 1
        if(j>8) :
            break
    word_next1 = word+" "+next_words[0]
    word_next2 = next_words[1]
    word_next3 = next_words[2]
    word_next4 = next_words[3]
    word_next5 = next_words[4]
    word_next6 = next_words[5]
    word_next7 = next_words[6]
    word_next8 = next_words[7]
    word_next9 = next_words[8]
    
    return {
        'word': word,
        
        'is_numeric': is_numeric,
        'is_joint': is_joint,
        
        'is_first': is_first,
        'is_last': is_last,
        
        'is_capitalized': is_capitalized,
        'is_all_caps': is_all_caps,
        'is_all_lower': is_all_lower,
        'capitals_inside': is_abbreviation,
        
        'prefix-1': prefix1,
        'prefix-2': prefix2,
        'prefix-3': prefix3,
        'prefix-4': prefix4,
        'suffix-1': suffix1,
        'suffix-2': suffix2,
        'suffix-3': suffix3,
        'suffix-4': suffix4,
        
        'prev_word': prev_word,
        'prev_prev_word' : prev_prev_word,
        'next_word': next_word,
        'next_next_word' : next_next_word,
        
        'prevToprev_prev' : prevToprev_prev,
        'prev_curr' : prev_curr,
        'curr_next' : curr_next,
        'next_nextTonext' : next_nextTonext,
        
        'prevToprev_prev_curr' : prevToprev_prev_curr,
        'prev_curr_next' : prev_curr_next,
        'curr_next_nextTonext' : curr_next_nextTonext,
        
        'prevToprev_prev_curr_next' : prevToprev_prev_curr_next,
        'prev_curr_next_nextTonext' : prev_curr_next_nextTonext,
        
        'context' : context,
        
        'word_prev3' : word_prev3, 
        'word_prev4' : word_prev4,
        'word_prev5' : word_prev5, 
        
        'word_next3' : word_next3,
        'word_next4' : word_next4,
        'word_next5' : word_next5
    }

def sent_to_features(tagged_sentences):
    X, y = [], []
 
    for tagged in tagged_sentences:
        X.append([features(untag(tagged), index) for index in range(len(tagged))])
        y.append([tag for _, tag in tagged])
 
    return X, y

def get_precision_recall(y_pred, y_test) :
#TP = index 0
#FN = index 1
#FP = index 2
    totals = {}
    for j in range(len(y_pred)) :
        for i in range(len(y_pred[j])) :
            trueTag = y_test[j][i]
            guessTag = y_pred[j][i]
            if trueTag not in totals:
                totals[trueTag] = [0]*3
            if guessTag not in totals:
                totals[guessTag] = {}
            if trueTag == guessTag:
                totals[trueTag][0] += 1
            else:
                totals[trueTag][1] += 1
                totals[guessTag][2] += 1
    not_needed = totals.pop('X')
    return totals

if __name__ == '__main__' :
    tagged_sentences = nltk.corpus.brown.tagged_sents(tagset='universal')[:10000]
    tagset = []
    for sentence in tagged_sentences :
        for word, tag in sentence :
            tagset.append(tag)
    tagset = sorted(set(tagset))
    print("Total Tagged sentences: ", len(tagged_sentences))
    print("Tagset:", tagset)
    split = int(.75 * len(tagged_sentences))
    training_sentences = tagged_sentences[:split]
    test_sentences = tagged_sentences[split:]
    X_train, y_train = sent_to_features(training_sentences)
    print("Number of training sentences:", len(X_train))
    X_test, y_test = sent_to_features(test_sentences)
    print("Number of testing sentences:", len(X_test))
    model = CRF(all_possible_transitions=True)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    sentence = input("Input sentence: ").split()
    sentence_features = [features(sentence, index) for index in range(len(sentence))]
    print(model.predict([sentence_features]))
    print("Accuracy:", metrics.flat_accuracy_score(y_test, y_pred))
    prec_rec = get_precision_recall(y_pred, y_test)
    for tag, scores in prec_rec.items() :
        TP = scores[0]
        FN = scores[1]
        FP = scores[2]
        precision = TP/(TP+FP)
        recall = TP/(TP+FN)
        Fscore = 2*precision*recall/(precision+recall)
        print(tag, "Precision:", precision, "Recall:", recall, "Fscore:", Fscore)
