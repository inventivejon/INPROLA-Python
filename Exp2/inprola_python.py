#!/usr/bin/python
#-*- coding:utf-8 -*-

from FunctionCreator import FunctionCreator

functions: list = []

def startConsoleInterface():
    continueAsking = True
    while continueAsking:
        erg = input('Tippe etwas ein (q,h): ')
        if erg == 'q':
            print('End of Programm')
            continueAsking = False
        elif erg == 'h':
            print('''
                  lf - Liste alle Funktionen auf
                  f - neue Funktion
                  n - neues Requirement
        	      h - Hilfe
        	      q - Beenden
        	      ''')
        elif erg == 'lf':
            new_function = print('Hier ist die Liste aller Funktionen:')
            for single_function in functions:
                print("- {}".format(single_function.function_name))
                single_function.print()
        elif erg == 'f':
            new_function = input('Gib die neue Funktion ein:')
            if " " in new_function:
                print("Leerzeichen dürfen im Funktionsnamen nicht sein")
            else:
                functions.append(FunctionCreator(new_function))
                print('Neue Funktion {} wurde hinzugefügt'.format(new_function))
        elif erg == 'n':
            new_requirement = input('Gib das neue Requirement ein:')
            functions[-1].add_requirement(new_requirement)
            print('Neues Requirement {} wurde hinzugefügt'.format(new_function))
        else:
            pass