import copy

class StructuredMask:
    structuredMasks = []
    maskInterpreter = {
    # Start and End Character need to be different in case of SubGroup
    # type is a key word. Currently supported: subGroup, arrayCollection, raw
    # raw means stop character to store previous content into tree node
    # subGroup means all content encapsulated in defined character are put into sub tree node and that content is reinterpreted
    # arrayCollection means all symbols connected to that characters are assembled in an array in the node
    "<": { "type": "subGroup", "name": "object", "endCharacter": ">" },
    "{": { "type": "subGroup", "name": "repeatable", "endCharacter": "}" },
    "[": { "type": "subGroup", "name": "subSentence", "endCharacter": "]" },
    "|": { "type": "arrayCollection", "name": "alternative", "endCharacter": " " },
    " ": { "type": "raw" }
    }

    def CreateStructuredMask(self, rawMask, maskInterpreter):
        structuredMasks = []
        print('Call CreateStructuredMask with \'{}\''.format(rawMask))
        if type(rawMask[0]) != str:
            for mask in rawMask:
                print('Call CreateStructuredMask for \'{}\''.format(mask))
                # This is the highest mask level. Always starts with character zero.
                newStructuredMask = self.CreateStructuredMask(mask, maskInterpreter)
                print("Finished structuring mask with result: {}".format(newStructuredMask))
                structuredMasks = structuredMasks + [newStructuredMask]
                print("Content of structuredMasks now {}".format(structuredMasks))
            return structuredMasks
        else:
            processingValue = rawMask if type(rawMask) == str else rawMask[0]
            processingValue = processingValue.replace('?',' ?').replace('.',' .').replace('!',' !').replace(',',' ,')
            if processingValue.endswith(" ") == False:
                processingValue = processingValue + " " # Adding trail space character to force finish of last symbol
            print('Processing string \'{}\''.format(processingValue))
            initialState = 'raw' # Constant value to be set into searchState as initial and fallback
            characterBuffer = '' # Contains all characters buffered for next processing step
            bufferedSearchState = [initialState] # In case a stateJumps into a different state then this remembers the state before
            searchState = initialState # State control variable of maskBuilder
            bufferedStateContent = [{}]
            stateContent = {} # Store all state specific content here
            
            for singleCharacter in processingValue:
                if searchState == 'raw':
                    if singleCharacter in maskInterpreter:
                        if maskInterpreter[singleCharacter]['type'] == 'subGroup': 
                            # Buffer all following character until endCharacter and call in recursive function call
                            # SubGroup control values
                            stateContent = {
                                "subGroupName": maskInterpreter[singleCharacter]['name'],
                                "startCharacter": singleCharacter,
                                "endCharacter": maskInterpreter[singleCharacter]['endCharacter'],
                                "controlCharacterCounter": 1
                            }
                        elif maskInterpreter[singleCharacter]['type'] == 'raw':
                            print("Stop Symbol detected with content: {}".format(characterBuffer))
                            # Raw means next state will be raw. Store the last content into structured mask
                            # Create raw entry for current content
                            if type(characterBuffer) == str:
                                if characterBuffer != '':
                                    structuredMasks = structuredMasks + [('raw',characterBuffer)]
                            else:
                                structuredMasks = structuredMasks + characterBuffer
                        elif maskInterpreter[singleCharacter]['type'] == 'arrayCollection':
                            stateContent = {
                                "name": maskInterpreter[singleCharacter]['name'],
                                "arrayCollection": [('raw',characterBuffer)] if type(characterBuffer) == str else characterBuffer,
                                "collectionCharacter": singleCharacter,
                                "endCharacter": maskInterpreter[singleCharacter]['endCharacter']
                            }
                        characterBuffer = ''
                        searchState = maskInterpreter[singleCharacter]['type']
                    else:
                        # No control character add current character to buffer
                        characterBuffer = characterBuffer + singleCharacter
                elif searchState == 'subGroup':
                    # In SearchState 'subGroup'
                    if singleCharacter == stateContent['startCharacter']:
                        stateContent['controlCharacterCounter'] = stateContent['controlCharacterCounter'] + 1
                    elif singleCharacter == stateContent['endCharacter']:
                        stateContent['controlCharacterCounter'] = stateContent['controlCharacterCounter'] - 1
                    else:
                        characterBuffer = characterBuffer + singleCharacter

                    if stateContent['controlCharacterCounter'] == 0:
                        # End of subGroup
                        subContent = self.CreateStructuredMask(characterBuffer + " ", maskInterpreter)
                        print("Finished subCall with result {}".format(subContent))
                        characterBuffer = [(stateContent['subGroupName'], subContent)]
                        print("Finished subGroup: {}".format(characterBuffer))
                        # Reset subGroup control variables
                        stateContent = bufferedStateContent[len(bufferedSearchState) - 1]
                        searchState = bufferedSearchState[len(bufferedSearchState) - 1]
                        if bufferedSearchState[len(bufferedSearchState) - 1] != initialState:
                            print("Removing last buffered state {} with {}".format(bufferedSearchState, bufferedStateContent))
                            bufferedSearchState = bufferedSearchState[:-1]
                            bufferedStateContent = bufferedStateContent[:-1]
                            print("Result buffered state after removed entry {} with {}".format(bufferedSearchState, bufferedStateContent))
                elif searchState == 'arrayCollection':
                    # bufferedSearchState
                    if singleCharacter in maskInterpreter and maskInterpreter[singleCharacter]['type'] == 'subGroup':
                        # Buffer all following character until endCharacter and call in recursive function call
                        # Buffer last state
                        bufferedSearchState = bufferedSearchState + [searchState]
                        bufferedStateContent = bufferedStateContent + [stateContent]
                        # SubGroup control values
                        stateContent = {
                            "subGroupName": maskInterpreter[singleCharacter]['name'],
                            "startCharacter": singleCharacter,
                            "endCharacter": maskInterpreter[singleCharacter]['endCharacter'],
                            "controlCharacterCounter": 1
                        }
                        characterBuffer = ''
                        searchState = maskInterpreter[singleCharacter]['type']
                    else:
                        # In SearchState 'Array Collection'
                        if singleCharacter == stateContent['collectionCharacter']:
                            # Another alternative will follow
                            if type(characterBuffer) == str:
                                stateContent['arrayCollection'] = stateContent['arrayCollection'] + [('raw',characterBuffer)]
                            else:
                                stateContent['arrayCollection'] = stateContent['arrayCollection'] + characterBuffer
                            characterBuffer = ''
                        elif singleCharacter == stateContent['endCharacter']:
                            if type(characterBuffer) == str:
                                stateContent['arrayCollection'] = stateContent['arrayCollection'] + [('raw',characterBuffer)]
                            else:
                                stateContent['arrayCollection'] = stateContent['arrayCollection'] + characterBuffer 
                            structuredMasks = structuredMasks + [('alternative', stateContent['arrayCollection'])]
                            stateContent = bufferedStateContent[len(bufferedSearchState) - 1]
                            characterBuffer = ''
                            searchState = bufferedSearchState[len(bufferedSearchState) - 1]
                            if bufferedSearchState[len(bufferedSearchState) - 1] != initialState:
                                bufferedSearchState = bufferedSearchState[:-1]
                                bufferedStateContent = bufferedStateContent[:-1]
                        else:
                            characterBuffer = characterBuffer + singleCharacter

        if type(rawMask) != str and len(rawMask) > 1 and type(rawMask[1]) != str:
            return [rawMask[1], structuredMasks]
        else:
            return structuredMasks

        
    def CompareToMask(self, mask, sentence, objectContent):
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
                    subResult = self.CompareToMask([singleAlternative] + mask[mask_idx+1:], sentence[sentence_idx:],copy.deepcopy(objectContent))
                    if subResult[0]:
                        return subResult
                return (False, {})
            elif maskEntry[0] == 'repeatable':
                print("Recognized repeatable")
                # In case of repeatable there must be one sequence match and then either none or another sequence match
                # In order to map this we transform the masl to one entry that need to follow and then another sequence with alternative none (representation of optional)
                return self.CompareToMask(maskEntry[1] + [('alternative', [('subSentence',maskEntry[1])] + [('raw','')])] +  mask[mask_idx+1:], sentence[sentence_idx:],copy.deepcopy(objectContent))
            elif maskEntry[0] == 'subSentence':
                print("Recognized subsentence")
                # This is a subsentence. Unpack and add to rest of mask
                return self.CompareToMask(maskEntry[1] + mask[mask_idx+1:], sentence[sentence_idx:],copy.deepcopy(objectContent))
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

    def DrawStructuredMaskTree(self, structuredMask, level):
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


    def __init__(self, rawMasks):
        self.structuredMasks = self.CreateStructuredMask(rawMasks, self.maskInterpreter)