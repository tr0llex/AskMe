from django.shortcuts import render

# Temporary data generators
QUESTION_COUNT = 10
ANSWERS_COUNT = 4
from random import sample, randint

questions = [
    {
        'id': idx,
        'title': f'Title number {idx}',
        'text': f'Some text for question #{idx}'
    } for idx in range(QUESTION_COUNT)
]

answers = [
    {
        'id': idx,
        'text': f'Some text for answer #{idx}'
    } for idx in range(ANSWERS_COUNT)
]

possible_tags = ['Javascript', 'Java', 'Python', 'C#', 'Php', 'Android', 'Html', 'Jquery', 'C++', 'Css', 'Ios', 'Mysql',
                 'Sql',
                 'Node.js', 'Arrays', 'Asp.net', 'Ruby-on-rails', 'Json', '.net', 'Sql-server', 'Reactjs', 'Swift',
                 'Objective-c']
tags = [{
    'tags': sample(possible_tags, randint(3, 5)),
    'tag_id': i
} for i in range(QUESTION_COUNT)]  # sample(tags, randint(3, 5)), "tag"


# END Temporary data generators

def index(request):
    return render(request, 'index.html', {'questions': questions, "tags": sample(possible_tags, randint(3, 5))})


def hot_questions(request):
    return render(request, 'hot_questions.html', {'questions': questions, "tags": sample(possible_tags, randint(3, 5))})


def one_question(request, pk):
    question = questions[pk]
    return render(request, 'question.html', {"question": question, "answers": questions, "tags": sample(possible_tags, randint(3, 5))})


def ask_question(request):
    return render(request, 'ask_question.html', {})


def tag_questions(request, tag):
    return render(request, 'tag_questions.html',
                  {"questions": questions, "tags": sample(possible_tags, randint(3, 5)), "tag": tag})


def login(request):
    return render(request, 'login.html', {})


def signup(request):
    return render(request, 'signup.html', {})


def settings(request):
    return render(request, 'settings.html', {})
