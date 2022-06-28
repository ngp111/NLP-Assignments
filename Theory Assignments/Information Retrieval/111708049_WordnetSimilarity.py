import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import matplotlib.pyplot as plt
from nltk.corpus import wordnet as wn
import networkx as nx
from nltk.corpus import wordnet_ic
from pywsd.lesk import simple_lesk as lesk

def closure_graph(fn, *argv):
    seen = set()
    graph = nx.Graph()

    for arg in argv :
        def recurse(s):
            if not s in seen:
                seen.add(s)
                graph.add_node(s.name())
                for s1 in fn(s):
                    graph.add_node(s1.name())
                    graph.add_edge(s.name(), s1.name())
                    recurse(s1)

        recurse(arg)
    return graph

brown_ic = wordnet_ic.ic('ic-brown.dat')
nickel = wn.synset('nickel.n.02')
dime = wn.synset('dime.n.01')
budget = wn.synset('budget.n.01')
richter = wn.synset('richter_scale.n.01')
coin = wn.synset('coin.n.01')
graph = closure_graph(lambda s: s.hypernyms(), nickel, dime, budget, richter)
nx.draw(graph, with_labels=True)

print("Path based similarity between nickel and coin:",nickel.path_similarity(coin))
print("Leacock-Chodorow similarity between nickel and coin:",nickel.lch_similarity(coin))
print("Resnik similarity between nickel and coin:", nickel.res_similarity(wn.synset('coin.n.01'), brown_ic))
print("Lin similarity between nickel and coin:", nickel.lin_similarity(coin, brown_ic))
print("Jiang-Conrath between nickel and coin:", nickel.jcn_similarity(coin, brown_ic))
sentences = ['I went to the bank to deposit my money.',  
'The river bank was full of dead fishes.']  
print ("Context-1:", sentences[0])  
answer = lesk(sentences[0],'bank')  
print ("Sense:", answer)  
print ("Definition : ", answer.definition())  
print ("Context-2:", sentences[1])  
answer = lesk(sentences[1],'bank')  
print ("Sense:", answer)  
print ("Definition : ", answer.definition())   

plt.show()
