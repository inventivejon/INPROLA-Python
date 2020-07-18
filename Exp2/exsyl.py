#!/usr/bin/python
#-*- coding:utf-8 -*-
import copy
import StructuredMask

predicates = {}
predicate_equals = {}
functions = []

def AddEqualsPredicate(eqPrName, predicate):
    global predicates
    global predicate_equals
    retVal = ""
    if predicate in predicates:
        for singleEqPrName in eqPrName:
            if singleEqPrName not in predicate_equals:
                predicate_equals[singleEqPrName] = predicate
                print('Equal Predicate added')
                retVal = "Ich habe die Beziehung zwischen den beiden Prädikaten hinzugefügt"
            else:
                print('Equal Predicate already known')
                retVal = "Diese Beziehung zwischen den beiden Prädikaten ist bereits bekannt"
    else:
        print('Predicate not found')
        retVal = "Ich konnte das Prädikat nicht finden"
    return retVal
        
def GetOrigPredicate(predicate):
    global predicate_equals
    retVal = predicate
    if predicate in predicate_equals:
        retVal = predicate_equals[predicate]
    return retVal

def AddDetailToPredicate(detail, predicate):
    retVal = ""
    global predicates
    if type(detail) == str:
        detail = [detail]
    predicate = GetOrigPredicate(predicate)
    if predicate in predicates:
        print('Prädikat gefunden')
        print('Prüfe ob Wissen bereits vorhanden.')
        for subdetail in detail:
            if subdetail in predicates[predicate]:
                print('Ja das weiß ich')
                retVal = retVal + "Ja das weiß ich" + "\n"
            else:
                predicates[predicate] = predicates[predicate] + [subdetail]
                retVal = retVal + "Verstanden" + "\n"
    else:
        print('Prädikat {} unbekannt'.format(predicate))
        predicates[predicate] = detail
        print('Prädikat wurde hinzugefügt')
        retVal = retVal + "Verstanden" + "\n"
    return retVal
        
def CheckDetailsInPredicate(details, predicate):
    global predicates
    retVal = 'Nein'
    predicate = GetOrigPredicate(predicate)
    print('Prüfe Prädikat {} mit Details {}'.format(predicate, details))
    if predicate in predicates:
        fulfilled = True
        for detail in details:
            if detail not in predicates[predicate]:
                fulfilled = False
                #print('Not found on predicate')
                # Check if this is in an array
                for dPredicate in predicates[predicate]:
                    #print('Check subarray {}'.format(dPredicate))
                    if detail in dPredicate:
                        fulfilled = True
                if fulfilled == False:
                    print('Detail {} ist nicht in Prädikat'.format(detail))
        if fulfilled:
            retVal = 'Ja'
    else:
        print('Prädikat {} unbekannt'.format(predicate))
        retVal = 'Weiß nicht'
    return retVal

def GetPredicateFromDetail(detail):
    if type(detail) is not str and len(detail) > 0:
        detail = detail[0]
    #print('Called GetPredicateFromDetail with {}'.format(detail))
    global predicates
    retVal = ''
    for predicate in predicates:
        #print("Prüfe Inhalt {} von {}".format(predicates[predicate], predicate))
        if detail in predicates[predicate]:
            retVal = predicate if retVal == '' else retVal + ' und ' + predicate
        for subpredicate in predicates[predicate]:
            if detail in subpredicate and type(subpredicate) is not str:
                retVal = predicate if retVal == '' else retVal + ' und ' + predicate
    #print("Processed. Return value {} now".format(retVal))
    return retVal

# Syntax
# <Keyword> Object (z.B. <Detail>)
# [] Optional (z.B. [ein]) 
# / alternativ (muss auch ans Ende der Alternative z.B. ein/eine/einer/)
# {} Kann sich beliebig oft wiederholen (z.B. {})

masks = []
# Smalltalk
masks = masks + [("[Guten Tag]|Hi|[Grüß Gott]|Hallo| <Detail>!|.|", lambda library: "Hallo!")]
masks = masks + [("[Wie geht es Dir heute| ]|[Wie gehts|geht's] ?", lambda library: "Danke Gut :)")]

# Fragesätze
masks = masks + [("Aber|Und| Ist|ist|Sind|sind ein|eine|der|die|das| <Detail> ein|eine|der|die|das| <Prädikat>?", lambda library: CheckDetailsInPredicate(library["Detail"], library["Prädikat"][0]) )]
masks = masks + [("Sind <Detail> {,|und <Detail>}| und <Detail> ein|eine|der|die|das| <Prädikat>?", lambda library: CheckDetailsInPredicate(library["Detail"], library["Prädikat"][0]) )]
masks = masks + [("Was ist ein|eine|der|die|das| <Detail>?", lambda library: "{} ist {}".format(library["Detail"][0], GetPredicateFromDetail(library["Detail"][0])) )]
# Aussagesätze
masks = masks + [("<Detail> ist|sind ein|eine|der|die|das| <Prädikat>.|", lambda library: AddDetailToPredicate(library["Detail"][0], library["Prädikat"][0]) )]
masks = masks + [("<Detail> {,|und|oder <Detail>} sind ein|eine|der|die|das| <Prädikat>.|", lambda library: AddDetailToPredicate(library["Detail"], library["Prädikat"][0]) )]
masks = masks + [("<Detail> {,|und|oder <Detail>} sind alle ein|eine|der|die|das| <Prädikat>.|", lambda library: AddDetailToPredicate(library["Detail"], library["Prädikat"][0]) )]
masks = masks + [("<Prädikat> {,|und|oder <Prädikat>} sind wie ein|eine|der|die|das| <OrigPrädikat>.|", lambda library: AddEqualsPredicate(library["Prädikat"], library["OrigPrädikat"][0]) )]
masks = masks + [("<Prädikat> ist wie ein|eine|der|die|das| <OrigPrädikat>.|", lambda library: AddEqualsPredicate(library["Prädikat"], library["OrigPrädikat"][0]) )]

structuredMaskInstance = StructuredMask.StructuredMask(masks)

def CompareToMask(mask, sentence, objectContent):
    # TODO: For now only one sentence option will be recognized.
    print("Call Compare sentence {} to Mask: {} with content {}".format(sentence, mask, objectContent))
    mask_idx = 0
    sentence_idx = 0
    while mask_idx < len(mask) and sentence_idx < len(sentence):
        maskEntry = mask[mask_idx]
        if maskEntry[0] == 'raw':
            print("Compare raw {} with word {}".format(maskEntry[1], sentence[sentence_idx]))
            if maskEntry[1] == '':
                mask_idx = mask_idx + 1
            elif maskEntry[1] == sentence[sentence_idx]:
                mask_idx = mask_idx + 1
                sentence_idx = sentence_idx + 1
            else:
                return (False, {})
        elif maskEntry[0] == 'object':
            print("Recognized object {}".format(sentence[sentence_idx]))
            if maskEntry[1][0][1] in objectContent:
                objectContent[maskEntry[1][0][1]] = objectContent[maskEntry[1][0][1]] + [sentence[sentence_idx]]
            else:
                objectContent[maskEntry[1][0][1]] = [sentence[sentence_idx]]
            mask_idx = mask_idx + 1
            sentence_idx = sentence_idx + 1
        elif maskEntry[0] == 'alternative':
            print("Recognized alternative")
            for singleAlternative in maskEntry[1]:
                subResult = CompareToMask([singleAlternative] + mask[mask_idx+1:], sentence[sentence_idx:],copy.deepcopy(objectContent))
                if subResult[0]:
                    return subResult
            return (False, {})
        elif maskEntry[0] == 'repeatable':
            print("Recognized repeatable")
            # In case of repeatable there must be one sequence match and then either none or another sequence match
            # In order to map this we transform the masl to one entry that need to follow and then another sequence with alternative none (representation of optional)
            return CompareToMask(maskEntry[1] + [('alternative', [('subSentence',maskEntry[1])] + [('raw','')])] +  mask[mask_idx+1:], sentence[sentence_idx:],copy.deepcopy(objectContent))
        elif maskEntry[0] == 'subSentence':
            print("Recognized subsentence")
            # This is a subsentence. Unpack and add to rest of mask
            return CompareToMask(maskEntry[1] + mask[mask_idx+1:], sentence[sentence_idx:],copy.deepcopy(objectContent))
        if mask_idx >= len(mask) and sentence_idx >= len(sentence):
            # Both at end. Definitely ok
            return (True, objectContent)
        elif sentence_idx >= len(sentence):
            # Sentence at end but still mask. Could still match due to optional entry.
            # Add additional empty word.
            sentence = sentence + [""]
        elif mask_idx >= len(mask):
            # Mask at end but still words. Check if only one word left and empty word. Otherwise no match
            if sentence[sentence_idx] == '':
                return (True, objectContent)
            else:
                return (False, {})
    return (False, {})

def DrawStructuredMaskTree(structuredMask, level):
    indentCounter = 0
    indentCharacters = "   "
    realIndent = ""
    while indentCounter < level:
        indentCounter = indentCounter + 1
        realIndent = realIndent + indentCharacters
    entryCounter = 0
    for singleEntry in structuredMask:
        if entryCounter == 0 and level > 0:
            realIndent = realIndent[:-2]
            realIndent = realIndent + "->"
        elif len(realIndent) > 0:
            realIndent = realIndent[:-2]
            realIndent = realIndent + "  "
        if type(singleEntry[1]) != str:
            print("{}|{}".format(realIndent, singleEntry[0]))
            DrawStructuredMaskTree(singleEntry[1], level + 1)
        else:
            print("{}|{}".format(realIndent, singleEntry[1]))
        entryCounter = entryCounter + 1

def startConsoleInterface():
    continueAsking = True

    while continueAsking:
        erg = input('Tippe etwas ein (q,h): ')

        if erg == 'q':
            print('End of Programm')
            continueAsking = False
        elif erg == 'h':
            print('''
        	      lp - Liste aller Prädikate
        	      leqp - Liste aller equal Prädikate
        	      p - Neues Prädikat
        	      lf - Liste aller Formeln
                  lm - Liste alle Masken auf
                  lsm - Liste alle strukturierten Masken auf
        	      f - Neue Formel
                  i - Interpreter
        	      h - Hilfe
        	      q - Beenden
        	      ''')
        elif erg == 'p':
            new_predicate = input('Gib das neue Prädikat ein: ')
            AddDetailToPredicate([], new_predicate)
            print('Neues Prädikat {} wurde hinzugefügt'.format(new_predicate))
        elif erg == 'lp':
            print('{}'.format(predicates))
        elif erg == 'leqp':
            print('{}'.format(predicate_equals))
        elif erg == 'f':
            new_function = input('Gib die neue Funktion ein:')
            functions = functions + [new_function]
            print('Neue Formel {} wurde hinzugefügt'.format(new_function))
        elif erg == 'lf':
            print('{}'.format(functions))
        elif erg == 'lm':
            print('{}'.format(masks))
        elif erg.startswith('lm '):
            splitErg = erg.split(" ")
            print('{}'.format(masks[int(splitErg[1])]))
        elif erg == 'lsm':
            print('{}'.format(structuredMaskInstance.structuredMasks))
        elif erg.startswith('lsm '):
            splitErg = erg.split(" ")
            print('{}'.format(structuredMaskInstance.structuredMasks[int(splitErg[1])]))
        elif erg.startswith('dsm '):
            splitErg = erg.split(" ")
            DrawStructuredMaskTree(structuredMaskInstance.structuredMasks[int(splitErg[1])][1], 0)
        else:
            ProcessNewInput(erg)

def ProcessNewInput(erg):
        satz = list(filter(lambda a: a != '', erg.replace('?', ' ?').replace('!', ' !').replace('.',' .').replace(',',' ,').split(" ")))
        for singleMask in structuredMaskInstance.structuredMasks:
            compResult = CompareToMask(singleMask[1], satz, {})
            if compResult[0]:
                print("Satz passt zur Maske: {} mit Ergebnis: {}".format(singleMask, compResult))
                result = singleMask[0](compResult[1])
                return dprint(result)
        return dprint("Wie bitte?")

def dprint(input):
    strinput = "{}".format(input)
    print(strinput)
    return strinput
