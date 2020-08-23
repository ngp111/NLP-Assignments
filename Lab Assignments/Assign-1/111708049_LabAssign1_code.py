#!/usr/bin/env python
import string
import re

short_forms = {}
dates = []
clitics = {}
months = ["january", "february", "march", "april", "May", "june", "july", "august", "september", "october", "november", "december"]

def make_short_forms_dict() :
	short_forms['\\ u\\ '] = " you "
	short_forms['\\ r\\ '] = " are "
	short_forms['^U\\ '] = "You "
	short_forms["&amp"] = "and"

def make_datewords_list() :
	dates.append("1st|[23]1st")
	dates.append("2nd|22nd")
	dates.append("3rd|23rd")
	dates.append("[1]\dth|[012][4-9]th")

def make_clitics_dict() :
	clitics["won\'t"] = "will not"
	clitics["shan\'t"] = "shall not"
	clitics["an\'t"] = "an not"
	clitics["n\'t"] = " not"
	clitics["\'m"] = " am"
	clitics["[a-z]\'d"] = " would"
	clitics["\'re"] = " are"
	clitics["\'ll"] = " will"
	clitics["\'ve"] = " have"
	clitics["let\'s"] = "let us"
	clitics["Let\'s"] = "Let us"
	clitics["e\'s"] = "e is"
	clitics["t\'s"] = "t is"
	#possessive aposhtrophe
	clitics["s\'"] = "s 's"


"""Regexs"""
punctuation = "["+string.punctuation+"]"
hashtag = "#\w+"
user_reference = "@\w+"
emoji = "(?::|X|<|O:|B|\|=|;|\|)(?:-)?(?:\[|D|O|P|\(|\)|\]|!|>|\?|X|\*|\$|\||3)"
URL = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
eclipse = "[\.]+"
apostrophe = "\'s"
date1 = "\d{1,2}/\d{1,2}/\d{4}"
date2 = "\d{4}-\d{1,2}-\d{1,2}"
number = "\d{1,2},+\d{3}"
other = "\w+"
time = "[012]\d:[0-5]\d\\ [PApa][Mm]|\d:[0-5]\d\\ [PApa][Mm]|[1]\d\\ [PApa][Mm]|\d\\ [PapA][Mm]|[012]\d:[0-5]\d|\d[PapA][Mm]"
date = [date1, date2]
phone = "\d{4}\\ \d{3}\\ \d{3,4}"
floating_point = "\d+\.\d+"

def date_to_cfd(tokens, ele) :
    i = tokens.index(ele)
    if(re.match(date1, ele)) :
        first_pos = ele.find('/')
        second_pos = ele[first_pos+1:].find('/')+first_pos+1
        date = ele[:first_pos]
        month = ele[first_pos+1:second_pos]
        year = ele[second_pos+1:]
        cfd = "CF:D:"+year+"-"+month+"-"+date
        tokens[i] = cfd
    elif(re.match(date2, ele)) :
        cfd = "CF:D:"+ele
        tokens[i] = cfd
    elif(ele.lower() in months) :
        month = ele.lower()
        month = months.index(month)+1
        year = "????"
        date = "??"
        for j in range(4) :
            if(re.match("[12]\d{3}", tokens[i-j])) :
                year = tokens[i-j]
                tokens.remove(tokens[i-j])
                break
            elif(re.match("[12]\d{3}", tokens[i+j])) :
                year = tokens[i+j]
                tokens.remove(tokens[i+j])
                break
        for j in range(4) :
            found = 0
            for ele in dates :
                if(re.match(ele, tokens[i-j])) :
                    date = tokens[i-j][:-2]
                    tokens.remove(tokens[i-j])
                    found = 1
                    break
                elif(re.match(ele, tokens[i+j])) :
                    date = tokens[i+j][:-2]
                    tokens.remove(tokens[i+j])
                    found = 1
                    break
            if(found == 0) :
                if(re.match("[1-9]|0[1-9]|[12]\d|3[01]", tokens[i-j])) :
                    date = tokens[i-j]
                    tokens.remove(tokens[i-j])
                    break
                elif(re.match("[1-9]|0[1-9]|[12]\d|3[01]", tokens[i+j])) :
                    date = tokens[i+j]
                    tokens.remove(tokens[i+j])
                    break
              
        tokens[i] = "CF:D:"+str(year)+"-"+str(month)+"-"+str(date) 
    return tokens

def time_to_cft(tokens, ele) :
    i = tokens.index(ele)
    hrs = ele[0]
    if(ele.find(":") != -1) :
        pos = ele.find(":")
        hrs = int(ele[:pos])
        if(ele.find("PM")!=-1 or ele.find("pm")!=-1) :
            if(hrs//12 == 0) :
                hrs += 12
        mins = int(ele[pos+1:pos+3])
    elif(ele.find(" ")!=-1):
        hrs = int(ele[:ele.find(" ")])
        if(ele.find("PM")!=-1 or ele.find("pm")!=-1) :
            if(hrs//12 == 0) :
                hrs += 12
        mins = "00"
    else :
        if(ele.find("pm")!=-1) :
            pos = ele.find("pm") 
            hrs = int(ele[:pos])
            if(hrs//12 == 0) :
                hrs += 12
            mins = "00"
        elif(ele.find("am")!=-1) :
            pos = ele.find("am") 
            hrs = int(ele[:pos])
            mins = "00"
    if(hrs//10) :
        tokens[i] = "CF:T:"+str(hrs)+str(mins)+":IST"
    else :
        tokens[i] = "CF:T:0"+str(hrs)+str(mins)+":IST"
    return tokens

def main() :
	make_short_forms_dict()
	make_datewords_list()
	make_clitics_dict()

	token_specification = [hashtag, URL, emoji, user_reference, eclipse, apostrophe, floating_point, date1, date2, time, phone, number, punctuation, other]
	tok_regex = '|'.join('%s' % val for val in token_specification)	

	file = open("111708049_Assgn1Dataset-1.txt", "r")
	tweets = file.readlines()
	file.close()

	fileOp = open("output.txt", "w")
	for tweet in tweets :
		sent = tweet
		
		#Adding full stop
		if(sent[-2] != "." and sent[-2] != "?" and  sent[-2]!="!" and sent[-3].islower()) :
			sent = sent[:-1]
			sent += " .\n"
		
		fileOp.write(sent)
		
		#Normalizing clitics
		for regex, value in clitics.items() :
			sent = re.sub(re.compile(regex), value, sent)

		#Normalizing shortforms
		for regex, value in short_forms.items() :
			sent = re.sub(re.compile(regex), value, sent)
			tokens = re.findall(tok_regex, sent)
		
		#Tokenizing matching patterns
		for ele in tokens :
			if(re.match(date1, ele) or re.match(date2, ele) or ele.lower() in months) :
				tokens = date_to_cfd(tokens, ele)
			elif(re.match(time, ele)) :
			    	tokens = time_to_cft(tokens, ele)
		
		fileOp.write(str(len(tokens)))
		fileOp.write("\n")
		for token in tokens :   
			token += "\n"
			fileOp.write(token)
	fileOp.write("\n")
	fileOp.close()

if __name__=="__main__":
	main()
