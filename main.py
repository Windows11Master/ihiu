from flask import Flask, render_template, redirect, url_for, request, jsonify
app = Flask(__name__)

def get_letters(side):
  let = request.args.get(side)
  let = ''.join(filter(str.isalpha, let))
  let_list = list(let.upper())
  return dict((s, side) for s in let_list)

def clean_letters(l, t, r, b):
    left = get_letters(l)
    top = get_letters(t)
    right = get_letters(r)
    bottom = get_letters(b)
    pos = {**left, **top, **right, **bottom}
    return pos

#### This cleaning is previously applied to the word txt files
## def clean_words(file):
##     with open(file) as word_file:
##         actual_words = list(word.strip().upper() for word in word_file)
##         valid_words = [w for w in actual_words if len(w)>=3]
##
##         toss = []
##         for word in valid_words:
##             ## make sure letters don't repeat
##             letters = list(word)
##             num = 1
##             while num < len(letters):
##                 if (letters[num] == letters[num-1]):
##                     toss.append(word)
##                     num = len(letters)
##                 else:
##                     num += 1
##         return [w for w in valid_words if w not in toss]

def get_words(file, pos, chars):
    with open(file) as word_file:
        actual_words = list(word.strip().upper() for word in word_file)
        valid_words = [w for w in actual_words if set(w)-chars==set()]

        toss = []
        for word in valid_words:
            ## make sure letters aren't adjacent and don't repeat
            letters = list(word)
            num = 1
            while num < len(letters):
                if (pos[letters[num]] == pos[letters[num-1]]):
                    toss.append(word)
                    num = len(letters)
                else:
                    num += 1
        return [w for w in valid_words if w not in toss]

# helper function
def to_base(str):
    return ''.join(sorted(set(str)))

# find one word solutions
def one_word_solution(word_list, chars):
    return [w for w in word_list if set(w) == chars]

# find two word solutions
def two_word_solution(word_list, chars):
    output = []
    for word in word_list:
        last = word[len(word)-1]
        matches = [w for w in word_list if w[0] == last and w!= word]
        for m in matches:
            pair = word + m
            if set(pair) == chars:
                output.append([word,m])
    return output

# find three word solutions
def three_word_solution(word_list, chars):
    ab = [a+b for a in word_list for b in word_list if a[-1]==b[0]]
    candidates = list(set([to_base(a)+a[-1] for a in ab]))
    solutions = {a:b for a in candidates for b in word_list if set(a+b)==chars and a[-1]==b[0]}
    ext = [[a+'-'+b,to_base(a+b)+b[-1]] for a in word_list for b in word_list if a!=b and a[-1]==b[0]]
    vals = ['-'.join([e[0],solutions[e[1]]]) for e in ext if e[1] in solutions.keys()]
    return [v.split('-') for v in vals]

num_map = {'1': {'text': 'one', 'function': one_word_solution},
           '2': {'text': 'two', 'function': two_word_solution},
           '3': {'text': 'three', 'function': three_word_solution}}


def display_answers(sets, num):
    if sets == []:
        return "No " + num_map[num]['text'] + "-word solutions found!"
    else:
        output = ""
        for s in sets:
            output += "<ul>" + " ??? ".join(s) + "</ul>"
        return "<span>" + output + "</span>"

def solve_puzzle(pos, num, wordfile, exclude = []): # optionally exclude a list of answers

    chars = set(pos.keys())

    wordset = get_words(wordfile, pos, chars)
    answers = num_map[num]['function'](wordset, chars)
    answers = [x for x in answers if x not in exclude]

    return answers, num

def get_html(pos, number, wordfile, exclude = []):
    if len(pos)==12:
        answers, num = solve_puzzle(pos, number, wordfile, exclude)
        result = display_answers(answers,num)
        return jsonify({'html': str(result)})
    else:
        return jsonify({'html': "Please input 3 distinct letters per side!"})

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/transform')
def transform():
    number = request.args.get('number')
    pos = clean_letters('left','top','right','bottom')
    return get_html(pos, number, "words_easy.txt")

@app.route('/transform_hard')
def transform_hard():
    number = request.args.get('number')
    pos = clean_letters('left','top','right','bottom')
    easy_answers, num = solve_puzzle(pos, number, "words_easy.txt")
    return get_html(pos, number, "words_hard.txt", exclude=easy_answers)

if __name__ == "__main__":
    app.run(debug=True)
