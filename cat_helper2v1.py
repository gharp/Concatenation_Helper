
import re
import sys
import csv
import os
#import pandas as pd
import math

speaker_pattern = re.compile('([^\.]+):\s+')

def get_input_from(prompt, allowed):
    command = input(prompt)
    if command == 'quit':
        sys.exit()
    while command not in allowed:
        if command == 'quit':
            sys.exit()
        print("Input not accepted. Please enter one of these values: ")
        print(allowed)
        command = input(prompt)
    return command

def process_text(text):
    return text.replace(u"\u2018", "").replace(u"\u2019", "").replace(u"\u201c","").replace(u"\u201d", "").replace("\t","")

class Statement:
    def __init__(self, s="", t="", v=1):
        self.speaker = s
        self.text = t
    def __str__(self, char_limit=None):
        if char_limit == None:
            return "{0}:\n{1}\n".format(self.speaker, self.text)
        else:
            return "{0}:\n{1}\n".format(self.speaker, self.text[0:char_limit])

class Interview:
    def __init__(self):
        self.statements = []
        self.successors = []
    def __str__(self):
        r = ""
        for s in self.statements:
            r += str(s)
        return r
    def from_file(self, input_file):
        current = Statement()
        for line in input_file:
            line = process_text(line)
            match = speaker_pattern.match(line)
            if match:                
                if current.text != "":
                    current.text = current.text.strip()
                    self.statements.append(current)
                    current = Statement(match.group(1).strip())
                else:
                    current.speaker = match.group(1).strip()
            else:
                if line.strip() != "":
                    current.text += line.strip() + " "
        if self.statements == []:
            print("Couldn't find any statements in \"Speaker: Response...\" format. Is the file formatted correctly? Exiting now...")
            exit(1)
    def speakers(self):
        r = []
        for s in self.statements:
            if s.speaker not in r:
                r.append(s.speaker)
        return r
    def write_csv(self, target):
        # assumes 2 speakers
        f = open(target, 'w', newline='')
        w = csv.writer(f, dialect='excel')
        w.writerow(self.speakers())
        for i in [j*2 for j in range(math.floor(len(self.statements)/2))]:
            w.writerow([self.statements[i].text, self.statements[i+1].text])
        f.close()
    # in case we switch to a more wysiwyg paradigm:
    #    def append_to_answer(self, i, text):
    #        (q,a) = self.dialogue[i]
    #        self.dialogue[i] = (q,a + text)
    # these next two functions don't need to be a part of the class
    def concatenate_questions(self):
        new_statements = []
        for i in [j*2 for j in range(math.floor(len(self.statements)/2))]:
            if new_statements == []:
                print(self.statements[i])
                print(self.statements[i+1])
                print("Would you like to [d]elete this first question or [n]ot?")
                command = get_input_from('-> ', ['d','n'])
                if command == 'd':
                    pass
                else:
                    new_statements.append(self.statements[i])
                    new_statements.append(self.statements[i+1])
            else:
                print(self.statements[i])
                print(self.statements[i+1])
                print("Is this [n]ew or [s]ame question? Or [d]elete? Or [dq]?")
                command = get_input_from('-> ', ['d', 'dq', 'n', 's'])
                if command == 'd':
                    pass
                elif command == 'dq':
                    s = new_statements.pop()
                    s.text += " {0}".format(self.statements[i+1].text)
                elif command == 'n':
                    new_statements.append(self.statements[i])
                    new_statements.append(self.statements[i+1])
                elif command == 's':
                    previous = new_statements.pop()
                    previous.text += " << {0} >> {1}".format(self.statements[i].text, self.statements[i+1].text)
                    new_statements.append(previous)
        self.statements = new_statements
    def fast_edit_questions(self):
        p = re.compile(r"\.([^\.]+)\?")
        interviewer = self.speakers()[0]
        for (i, match) in enumerate([p.search(s.text) for s in self.statements]):
            if match and self.statements[i].speaker == interviewer:
                # maybe abstact this out as clean_question
                meat = match.group(0).strip('. \n')
                meat = meat.replace("May I ask, ", "")
                meat = meat[0].upper() + meat[1:]
                print("Original:\n    " + self.statements[i].text)
                print("New:\n    " + meat)
                print("\nDo you approve of this change? [y] or [n]")
                if get_input_from("-> ", ['y','n']) == 'y':
                    self.statements[i].text = meat
    def write_interview(self, target):
        f = open(target, 'w', encoding='utf-8')
        for s in self.statements:
            f.write(str(s))
            f.write('\n')
        f.close()

def main(argv):
    battery = []
    
    for name in os.listdir('./Altered'):
        if name[-4:] == '.txt':
            battery.append(name)
#    battery = ['2908_SPARC.txt']
    if len(argv) >= 1 and argv[0] == "csv":
         for source in battery:
            target = source[0:4] + '.csv'
            print("Reading '" + source + "'...")
            f = open('./Altered/' + source, encoding='utf-8')
            d = Interview()
            d.from_file(f)
            print("Writing '" + target + "'...")
            d.write_csv('./Altered/' + target)
            f.close()
            print("Done!")
    else:
        for source in battery:
            f = open('./Altered/' + source, encoding='utf-8')
            d = Interview()
            print("Reading '" + source + "'...")
            d.from_file(f)
            print(d.speakers())
            print("======================")
            print("Concatenate Questions:")
            print("======================")
            d.concatenate_questions()
#            print("===============")
#            print("Edit Questions:")
#            print("===============")
#            d.fast_edit_questions()
            print("Writing 'new" + source + "...")
            d.write_interview('./Altered/new' + source)
            f.close()
            del d
            print("Done!")

if __name__ == "__main__":
    main(sys.argv[1:])