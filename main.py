import json
import random
CHANCE = 5
WORD_LENGTH = 5
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_ANS = {t: True for t in ALPHABET}
guess_list = []
Line = "-" * (WORD_LENGTH * 2 + 1) * 2
with open('voc.json') as f:
    word_list = json.load(f)['wordle']["vocab"]
    answer = random.choice(word_list)

def check(guess):
    r = []
    for i in range(WORD_LENGTH):
        if answer[i] == guess[i]:
            r.append("C")
        elif guess[i] in answer:
            r.append("P")
        else:
            ALPHABET_ANS[guess[i]] = False
            r.append("W")
    return r


def get_input():
    while True:
        guess = input(f"Guess one word (the length of the word = {WORD_LENGTH}: ")
        if len(guess) == WORD_LENGTH:
            return guess
        else:
            print(f"the length of the word should be {WORD_LENGTH}, input again")


def check_win(r):
    for c in r:
        if c != 'C':
            return False
    return True


def print_table(t):
    for g in game:
        print(g)

    if t < CHANCE - 1:
        print("You can still use")
        print(' '.join([k for k in ALPHABET_ANS.keys() if ALPHABET_ANS[k]]))
    else:
        print(Line)
        print("GAME OVER !!!")
        print("The Answer is",answer)


def game():
    game = [Line]
    for g in range(CHANCE):
        guess = get_input()
        r = check(guess)
        if check_win(r):
            print(f"congratulate you win the game\nThe answer is {answer}")
            print("Your Result")
            guess = "|" + '-'.join([c for c in guess]) + "|" + '-'.join([c for c in r]) + "|"
            game.append(guess)
            game.append(Line)
            for l in game:
                print(l)
            break
        guess = "|" + '-'.join([c for c in guess]) + "|" + '-'.join([c for c in r]) + "|"
        game.append(guess)
        # game.append(guess_result)
        # game.append(Line)
        print_table(g)