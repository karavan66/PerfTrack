#!/usr/bin/python
import xml.dom.minidom

import os, sys

def enum(**enums):
    return type('Enum', (), enums)
CountableType = enum(BINARY="binary", MODULE="module", SYMBOL="symbol")

def print_countable(indent, countable):
    print "%s%s counted %s (%s)" % ("  " * indent, countable.name, countable.count, countable.type)
    [print_countable(indent +1, x) for x in countable.subs]

def find_binary(countables, binary):
    if countables == None:
        return None

    for c in countables:
        if (c.getName().endswith('/' + binary)):
            return c
        found = find_binary(c.subs, binary)
        if found != None:
            return found
    
    return None
    
class Countable:
    def __init__(self, name, type):
        self.name = str(name)
        self.type = type
        self.subs = []
        self.count = dict()

    def getName(self):
        return self.name

    def addSub(self, sub):
        self.subs.append(sub)

    def addCount(self, events, class_id, count):
        self.count[events[class_id]] = int(count)

class ParseOprof:
    def __init__(self):
        self.events = dict()
        self.symboltable = None

    def getChildrenByTagName(self, node, tagName):
        result = []

        for child in node.childNodes:
            if child.nodeType==child.ELEMENT_NODE and (tagName=='*' or child.tagName==tagName):
                result.append(child)

        return result

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc).strip()

    def handleCountable(self, countable):
        type = CountableType.BINARY
        name = ""
        if (countable.tagName == "binary"):
            type = CountableType.BINARY
            name = countable.attributes['name'].value
        elif(countable.tagName == "symbol"):
            type = CountableType.SYMBOL
            symbol_id_ref = countable.attributes['idref'].value
            this_symbol = None
            for sd in self.symboltable.getElementsByTagName("symboldata"):
                if (sd.attributes['id'].value == symbol_id_ref):
                    this_symbol = sd
                    break
            name = this_symbol.attributes['name'].value
        elif(countable.tagName == "module"):
            type = CountableType.MODULE
            name = countable.attributes['name'].value
        else:
            raise Exception("Unknown Countable Type %s" % countable.nodeType)

        new_count = Countable(name, type)
        counts = self.getChildrenByTagName(countable, 'count')
        for c in counts:
            count = self.getText(c.childNodes)
            new_count.addCount(self.events, c.attributes['class'].value, count)

        for c in self.getCountableChildren(countable):
            sub_count = self.handleCountable(c)
            new_count.addSub(sub_count)
            #actual_count += sub_count.count

        #sometimes the count value is ommitted and expected to be the summation
        #of the child elements
        #if (actual_count > 0 and count == -1):
        #    new_count.updateCount(actual_count)
        return new_count

    def getCountableChildren(self, node):
        countable = self.getChildrenByTagName(node, "binary")
        countable.extend(self.getChildrenByTagName(node, "module"))
        countable.extend(self.getChildrenByTagName(node, "symbol"))
        return countable

    def handleProfile(self, profile):
        # You will need to change this parser if the schema changes
        assert(profile.attributes['schemaversion'].value == "3.0") 

        events_dom = profile.getElementsByTagName("eventsetup")
        classes_dom = profile.getElementsByTagName("class")
        self.events = dict()
        for c in classes_dom:
            event_found = False
            for e in events_dom:
                if (e.attributes['id'].value == c.attributes['event'].value):
                    event_found = True
                    self.events[c.attributes['name'].value] = e.attributes['eventname'].value
                    break
            assert(event_found)

        self.symboltable = profile.getElementsByTagName("symboltable")[0]

        return [self.handleCountable(b) for b in self.getCountableChildren(profile)]
    
    def processOPROF(self, fname):
        file = open(fname)
        dom = xml.dom.minidom.parse(file).getElementsByTagName("profile")[0]
        countables = self.handleProfile(dom)
        # [print_countable(0, c) for c in countables]
        return countables



