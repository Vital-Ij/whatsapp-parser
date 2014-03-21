from __future__ import division
import codecs
import date
import re
import operator
import sys
import json


class Chat():
    def __init__(self, filename):
        self.filename = filename
        self.raw_messages = []

        self.datelist = []
        self.timelist = []
        self.senderlist = []
        self.messagelist = []

    def open_file(self):
        arq = codecs.open(self.filename, "r", "utf-8-sig")
        content = arq.read()
        arq.close()
        lines = content.split("\n")
        lines = [l for l in lines if len(l) != 1]
        for l in lines:
            self.raw_messages.append(l.encode("utf-8"))

    def feed_lists(self):
        for l in self.raw_messages:
            search_obj = re.search(r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}', l)
            if search_obj:
                columns = l.split(": ")
                date, time = columns[0].split(" ")
                sender = columns[1]
                message = columns[2]
            else:
                message = l
            self.datelist.append(date)
            self.timelist.append(time)
            self.senderlist.append(sender)
            self.messagelist.append(message)

    def print_history(self, end=0):
        if end == 0:
            end = len(self.messagelist)
        for i in range(len(self.messagelist[:end])):
            print self.datelist[i], self.timelist[i],\
                self.senderlist[i], self.messagelist[i]

    def get_senders(self):
        senders_set = set(self.senderlist)
        return [e for e in senders_set]

    def count_messages_per_weekday(self):
        counter = dict()
        for i in range(len(self.datelist)):
            day, month, year = self.datelist[i].split("/")
            parsed_date = "%s-%s-%s" % (year, month, day)
            weekday = date.date_to_weekday(parsed_date)
            if weekday not in counter:
                counter[weekday] = 1
            else:
                counter[weekday] += 1
        return counter

    def count_messages_per_shift(self):
        shifts = {
            "latenight": 0,
            "morning": 0,
            "afternoon": 0,
            "evening": 0
        }
        for i in range(len(self.timelist)):
            hour = int(self.timelist[i].split(":")[0])
            if hour >= 0 and hour <= 6:
                shifts["latenight"] += 1

            elif hour > 6 and hour <= 11:
                shifts["morning"] += 1

            elif hour > 11 and hour <= 17:
                shifts["afternoon"] += 1

            elif hour > 17 and hour <= 23:
                shifts["evening"] += 1
        return shifts

    def count_messages_pattern(self, patternlist):
        counters = dict()
        pattern_dict = dict()
        senders = self.get_senders()
        for pattern in patternlist:
            counters[pattern] = dict()
            for s in senders:
                counters[pattern][s] = 0
            pattern_dict[pattern] = re.compile(re.escape(pattern), re.I)
        for i in range(len(self.messagelist)):
            for pattern in patternlist:
                search_result = pattern_dict[pattern].\
                    findall(self.messagelist[i])
                length = len(search_result)
                if length > 0:
                    if pattern not in counters:
                        counters[pattern][self.senderlist[i]] = length
                    else:
                        counters[pattern][self.senderlist[i]] += length
        return counters

    def print_patterns_dict(self, pattern_dict):
        for pattern in pattern_dict:
            print pattern
            for s in pattern_dict[pattern]:
                print s, ": ", pattern_dict[pattern][s]
            print ""

    def message_proportions(self):
        senders = self.get_senders()
        counter = dict()
        total = 0
        for i in ["messages", "words", "chars"]:
            counter[i] = dict()
            for s in senders:
                counter[i][s] = 0
        for i in range(len(self.senderlist)):
            counter["messages"][self.senderlist[i]] += 1
            counter["words"][self.senderlist[i]] += \
                len(self.messagelist[i].split(" "))
            counter["chars"][self.senderlist[i]] += len(self.messagelist[i])
            total += 1
        counter["total_messages"] = 0
        counter["total_words"] = 0
        counter["total_chars"] = 0
        for s in senders:
            counter["total_messages"] += counter["messages"][s]
            counter["total_words"] += counter["words"][s]
            counter["total_chars"] += counter["chars"][s]
        return counter

    def average_message_length(self):
        msg_prop = self.message_proportions()
        counter = dict()
        for s in self.get_senders():
            counter[s] = msg_prop["words"][s] / msg_prop["messages"][s]
        return counter

    def most_used_words(self, top=10, threshold=3):
        words = dict()
        for i in range(len(self.messagelist)):
            message_word = self.messagelist[i].split(" ")
            for w in message_word:
                if len(w) > threshold:
                    w = w.lower()
                    if w not in words:
                        words[w] = 1
                    else:
                        words[w] += 1
        sorted_words = sorted(words.iteritems(), key=operator.itemgetter(1),
                              reverse=True)
        counter = 0
        output = sorted_words[:top]
        return output


def main():
    if len(sys.argv) < 2:
        print "Run: python main.py <TextFileName>"
        sys.exit(1)
    c = Chat(sys.argv[1])
    #c = Chat("Moyrilia.txt")
    c.open_file()
    c.feed_lists()
    output = dict()
    output["patterns"] = \
        c.count_messages_pattern(['te amo', 'desculpa', 'beijos', 'amor',
                                 'coco', 'bom dia', 'bebe'])
    #c.print_patterns_dict(cdict)
    print c.message_proportions()
    output["proportions"] = c.message_proportions()

    print c.count_messages_per_shift()
    output["shifts"] = c.count_messages_per_shift()

    print c.count_messages_per_weekday()
    output["weekdays"] = c.count_messages_per_weekday()

    print c.average_message_length()
    output["lengths"] = c.average_message_length()

    output["senders"] = c.get_senders()

    print c.most_used_words(top=15, threshold=1)
    filename = sys.argv[1].split("/")[-1]
    print "./logs/"+filename+".json"
    arq = open("./logs/"+filename+".json", "w")
    arq.write(json.dumps(output))
    arq.close()

main()