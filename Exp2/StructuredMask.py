
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

    def __init__(self, rawMasks):
        self.structuredMasks = self.CreateStructuredMask(rawMasks, self.maskInterpreter)