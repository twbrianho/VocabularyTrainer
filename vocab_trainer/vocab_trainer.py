import csv
import requests
import random
from bs4 import BeautifulSoup

vocab_filename = 'vocab_list.txt'
import_filename = 'import_vocab.txt'
progress_filename = 'progress_data.csv'
headers = ["Word", "Appeared", "Correct", "Chain"]

dictionary_url = "https://www.dictionary.com/browse/{}?s=t"
sentence_url = "http://sentence.yourdictionary.com/{}"

vocab_list = []
vocab_dict = {}

undiscovered_q = []
unlearned_q = []
learned_q = []
mastered_q = []
queues = [undiscovered_q, unlearned_q, learned_q, mastered_q]
queue_names = ["Undiscovered", "Unlearned", "Learned", "Mastered"]


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(str):
    print(bcolors.HEADER + str + bcolors.ENDC)


def print_blue(str):
    print(bcolors.OKBLUE + str + bcolors.ENDC)


def print_green(str):
    print(bcolors.OKGREEN + str + bcolors.ENDC)


def print_warning(str):
    print(bcolors.WARNING + str + bcolors.ENDC)


def print_fail(str):
    print(bcolors.FAIL + str + bcolors.ENDC)


def print_bold(str):
    print(bcolors.BOLD + str + bcolors.ENDC)


def print_underline(str):
    print(bcolors.UNDERLINE + str + bcolors.ENDC)


class VocabWord():
    def __init__(self, word, definition):
        self.word = word
        self.definition = definition
        self.appearance_count = 0
        self.correct_count = 0
        self.chain_count = 0


def read_vocab_file():
    with open(vocab_filename, 'r') as f:
        for line in f:
            if ":" not in line:
                break
            word_def = line.strip()
            word = word_def.split(": ")[0].lower()
            definition = word_def.split(": ")[1]
            vocab_word = VocabWord(word, definition)
            vocab_list.append(vocab_word)
            vocab_dict[word] = vocab_word
    if vocab_list:
        print_green("[VOCABULARY LIST LOADED.]")
    else:
        print_warning("[NOTICE: EMPTY VOCABULARY LIST.]")


def add_to_vocab_file(vocab):
    with open(vocab_filename, 'a') as f:
        f.write("{}:{}\n".format(vocab.word.upper(), vocab.definition))


def read_progress_file():
    with open(progress_filename, 'r') as f:
        reader = csv.reader(f)
        try:
            next(reader)
            for row in reader:
                vocab = vocab_dict[row[0]]
                vocab.appearance_count = int(row[1])
                vocab.correct_count = int(row[2])
                vocab.chain_count = int(row[3])
            print_green("[PROGRESS LOADED.]")
        except:
            print_warning("[NOTICE: EMPTY PROGRESS FILE.]")


def write_progress_file():
    with open(progress_filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for vocab in vocab_list:
            writer.writerow([vocab.word, vocab.appearance_count, vocab.correct_count, vocab.chain_count])


def show_vocab_list():
    print("")
    for vocab in vocab_list:
        print_header(vocab.word.capitalize())
    print("")


def show_queue(qs):
    empty = True
    for q in qs:
        for vocab in q:
            empty = False
            print("")
            print_header(vocab.word.capitalize())
            print(vocab.definition)
    if empty:
        print_warning("\n[QUEUE IS EMPTY.]")


def show_progress():
    print_bold("\n[MODE: SHOW PROGRESS]")
    for q, name in zip(queues, queue_names):
        print("")
        print_blue("{} [total:{}]:".format(name.upper(), len(q)))
        if not q:
            print("[EMPTY.]")
        for vocab in q:
            print("\033[95m{:15}\033[0m {:02} / {:02} / {:02}".format(vocab.word.capitalize(), vocab.correct_count,
                                                                      vocab.appearance_count, vocab.chain_count))
    print("")


def create_queues():
    for vocab in vocab_list:
        if vocab.chain_count >= 3:
            mastered_q.append(vocab)
        elif vocab.appearance_count == 0:
            undiscovered_q.append(vocab)
        elif vocab.correct_count == 0:
            unlearned_q.append(vocab)
        else:
            learned_q.append(vocab)


def update_vocab_in_queue(vocab, original_queue):
    original_queue.remove(vocab)
    if vocab.chain_count >= 3:
        mastered_q.append(vocab)
    elif vocab.appearance_count == 0:
        undiscovered_q.append(vocab)
    elif vocab.correct_count == 0:
        unlearned_q.append(vocab)
    else:
        learned_q.append(vocab)


def vocab_stats_update(vocab, correct):
    vocab.appearance_count += 1

    if correct:
        vocab.correct_count += 1
        vocab.chain_count += 1

    else:
        vocab.chain_count = 0

    write_progress_file()


def pick_queue():
    while True:
        queue_choices = [undiscovered_q] * 5 + [unlearned_q] * 6 + [learned_q] * 7 + [mastered_q] * 1
        chosen_queue = random.choice(queue_choices)
        if chosen_queue:
            return chosen_queue


def review_mode():
    print_bold("\n[MODE: REVIEW VOCABULARY]\n")

    print(bcolors.OKBLUE + "--Choose what queue to review--")
    print("(0) Undiscovered")
    print("(1) Unlearned")
    print("(2) Learned")
    print("(3) Mastered")
    print("(4) All")
    print("(5) Undiscovered, Learned, & Unlearned")
    print("(6) Learned & Unlearned" + bcolors.ENDC)

    choice = input(">> Type the number: ")

    if choice == "0":
        show_queue([undiscovered_q])
    elif choice == "1":
        show_queue([unlearned_q])
    elif choice == "2":
        show_queue([learned_q])
    elif choice == "3":
        show_queue([mastered_q])
    elif choice == "4":
        show_queue([undiscovered_q, unlearned_q, learned_q, mastered_q])
    elif choice == "5":
        show_queue([undiscovered_q, unlearned_q, learned_q])
    elif choice == "6":
        show_queue([learned_q, unlearned_q])
    else:
        print_fail("[INVALID INPUT.]")


def quiz_mode():
    print_bold("\n[MODE: DEFINITION QUIZ]")

    while True:

        chosen_queue = pick_queue()
        chosen_vocab = random.choice(chosen_queue)

        print_blue("\nWhat is the definition of {}?".format(chosen_vocab.word.upper()))

        while True:
            all_choice_vocabs = random.sample(vocab_list, 4)
            if chosen_vocab not in all_choice_vocabs:
                break

        all_choice_vocabs.append(chosen_vocab)

        random.shuffle(all_choice_vocabs)

        for idx, choice_vocab in enumerate(all_choice_vocabs):
            print_blue("({}) {}".format(idx + 1, choice_vocab.definition))

        player_choice = int(input(">> Enter correct definition number (or 0 to leave): "))

        if player_choice == 0:
            return

        if all_choice_vocabs[player_choice - 1] == chosen_vocab:
            correct = True
            print_green("[CORRECT.]")

        else:
            correct = False
            print_fail("[INCORRECT.]")
            print_fail("The correct definition is: {}".format(chosen_vocab.definition))

        vocab_stats_update(chosen_vocab, correct)
        update_vocab_in_queue(chosen_vocab, chosen_queue)


def fill_mode():
    print_bold("\n[MODE: FILL-IN-THE-BLANK]\n")
    print_warning("Note: the sentences are a bit wonky, please use with caution.\n")

    while True:

        chosen_queue = pick_queue()
        chosen_vocab = random.choice(chosen_queue)
        chosen_word = chosen_vocab.word

        r = requests.get(sentence_url.format(chosen_word))

        if not r:
            continue

        soup = BeautifulSoup(r.content, "html.parser")

        soup_sentences = soup.find_all('li', attrs={'class': 'voting_li'})

        if not soup_sentences:
            continue

        sorted_soup_sentences = sorted(soup_sentences, key=lambda x: int(x['data-score']), reverse=True)

        best_sentence = sorted_soup_sentences[0]
        best_score = int(best_sentence['data-score'])

        if best_score <= 0:
            continue

        best_sentence = best_sentence.text

        print_blue(best_sentence.replace(chosen_word, "_______"))
        print_blue("Which word best fits the blank?")

        while True:
            all_choice_vocabs = random.sample(vocab_list, 4)
            if chosen_vocab not in all_choice_vocabs:
                break

        all_choice_vocabs.append(chosen_vocab)

        random.shuffle(all_choice_vocabs)

        for idx, choice_vocab in enumerate(all_choice_vocabs):
            print_blue("({}) {}".format(idx + 1, choice_vocab.word))

        player_choice = int(input(">> Enter correct definition number (or 0 to leave): "))

        if player_choice == 0:
            return

        if all_choice_vocabs[player_choice - 1] == chosen_vocab:
            correct = True
            print_green("[CORRECT.]")

        else:
            correct = False
            print_fail("[INCORRECT.]")
            print_fail("The correct word is: {}".format(chosen_vocab.word))

        vocab_stats_update(chosen_vocab, correct)
        update_vocab_in_queue(chosen_vocab, chosen_queue)


def add_word(new_word):
    try:
        vocab_dict[new_word]
        print_fail("[ERROR: WORD ALREADY EXISTS IN VOCABULARY LIST.]")
        return
    except:
        print_blue("Fetching word definition...")

    r = requests.get(dictionary_url.format(new_word))

    if not r:
        print_fail("[ERROR: WORD NOT FOUND IN DICTIONARY.]")
        return

    soup = BeautifulSoup(r.content, "html.parser")

    soup_ol = soup.find('ol')

    soup_definition = soup_ol.find('li', attrs={'value': '1'}).stripped_strings

    next(soup_definition)

    new_definition = ""
    for str in soup_definition:
        str = str.replace(":", "")
        if str == ":":
            continue
        elif new_word in str:
            continue
        elif str != ".":
            new_definition += " "
        new_definition += str

    if new_definition[-1] != ".":
        new_definition += "."

    print(new_definition)

    is_def = False
    for str in soup_definition:
        if str[0] == ".":
            is_def = True
        elif is_def == True:
            new_definition = str.strip(":")
            break

    new_vocab = VocabWord(new_word, new_definition)
    vocab_list.append(new_vocab)
    vocab_dict[new_word] = new_vocab
    add_to_vocab_file(new_vocab)
    undiscovered_q.append(new_vocab)

    print_green("[{} ADDED TO VOCABULARY LIST.]".format(new_word.upper()))


def add_mode():
    print_bold("\n[MODE: ADD VOCABULARY]")

    show_vocab_list()

    while True:
        print_blue("Total of {} words in vocabulary list.".format(len(vocab_list)))
        print_blue("Enter X to finish.")
        new_word = input(">> Add new word: ").lower()
        if new_word == 'x':
            break
        add_word(new_word)


def import_mode():
    print_bold("\n[MODE: IMPORT VOCABULARY LIST")
    with open(import_filename, 'r') as f:
        for line in f:
            new_word = line.strip().lower()
            print_blue("Adding new word: {}".format(new_word))
            add_word(new_word)

def clear_progress():
    print_fail("\nCLEARING ALL PROGRESS, THIS IS NOT REVERSIBLE!")
    choice = input("\033[91m>> Enter C to clear, or anything else to cancel: \033[0m").lower()
    if choice == 'c':
        for vocab in vocab_list:
            vocab.appearance_count = 0
            vocab.correct_count = 0
            vocab.chain_count = 0
            write_progress_file()
        print_fail("[CLEARED ALL PROGRESS.]")
    else:
        print_fail("[CLEAR CANCELLED.]")
    return

if __name__ == '__main__':

    print_header("VOCAB TRAINER 2018 v0.0.2 by twbrianho\n")
    read_vocab_file()
    read_progress_file()
    create_queues()

    while True:

        print(bcolors.OKBLUE + "\n--Choose an action--")
        print("(P)rogress")
        print("(R)eview")
        print("(D)efinition Quiz")
        print("(F)ill-In-The-Blank")
        print("(A)dd vocabulary")
        print("(I)mport vocabulary list")
        print("(C)lear progress")
        print("(S)ave and quit" + bcolors.ENDC)

        choice = input(">> Type the first letter: ").upper()

        if choice == "P":
            show_progress()
        elif choice == "R":
            review_mode()
        elif choice == "D":
            quiz_mode()
        elif choice == "F":
            fill_mode()
        elif choice == "A":
            add_mode()
        elif choice == "I":
            import_mode()
        elif choice == "C":
            clear_progress()
        elif choice == "S":
            break
        else:
            print_fail("[INVALID INPUT.]")

    write_progress_file()
    print_green("\n[PROGRESS SAVED.]")
    print("\nSeeya, slacker.\n\n")

    raise SystemExit
