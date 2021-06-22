from django.contrib.auth.models import User
from app.models import *

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from app.forms import *

# # Temporary data generators
# QUESTION_COUNT = 10
# ANSWERS_COUNT = 4
# from random import sample, randint
#
# questions = [
#     {
#         'id': idx,
#         'title': f'Title number {idx}',
#         'text': f'Some text for question #{idx}'
#     } for idx in range(QUESTION_COUNT)
# ]
#
# answers = [
#     {
#         'id': idx,
#         'text': f'Some text for answer #{idx}'
#     } for idx in range(ANSWERS_COUNT)
# ]
#
# possible_tags = ['Javascript', 'Java', 'Python', 'C#', 'Php', 'Android', 'Html', 'Jquery', 'C++', 'Css', 'Ios', 'Mysql',
#                  'Sql',
#                  'Node.js', 'Arrays', 'Asp.net', 'Ruby-on-rails', 'Json', '.net', 'Sql-server', 'Reactjs', 'Swift',
#                  'Objective-c']
# tags = [{
#     'tags': sample(possible_tags, randint(3, 5)),
#     'tag_id': i
# } for i in range(QUESTION_COUNT)]  # sample(tags, randint(3, 5)), "tag"
#
#
# # END Temporary data generators

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page = request.GET.get('page')
    objects = paginator.get_page(page)

    return objects

def index(request):
    questions = paginate(Question.objects.new_questions(), request)
    popular_tags = Tag.objects.popular_tags()
    best_members = Profile.objects.best_members()

    return render(request, 'index.html', {'questions': questions,
                                          'popular_tags': popular_tags,
                                          'best_members': best_members})

def hot_questions(request):
    questions = paginate(Question.objects.hot_questions(), request)
    popular_tags = Tag.objects.popular_tags()
    best_members = Profile.objects.best_members()

    return render(request, 'hot_questions.html', {'questions': questions,
                                                  'popular_tags': popular_tags,
                                                  'best_members': best_members})


def tag_questions(request, name):
    try:
        tag = Tag.objects.get(tag=name)
        questions = paginate(Question.objects.by_tag(name), request)
        popular_tags = Tag.objects.popular_tags()
        best_members = Profile.objects.best_members()

        return render(request, 'tag.html', {'tag': tag,
                                            'questions': questions,
                                            'popular_tags': popular_tags,
                                            'best_members': best_members})
    except Tag.DoesNotExist:
        raise Http404


def one_question(request, pk):
    try:
        question = Question.objects.get(pk=pk)
        question_answers = paginate(Answer.objects.by_question(pk), request, 3)
        if request.method == 'GET':
            form = AnswerForm()
        else:
            if not request.user.is_authenticated:
                return redirect(f"/login/?next={request.get_full_path()}")

            form = AnswerForm(profile_id=request.user.profile, question_id=question, data=request.POST)
            if form.is_valid():
                form.save()
                answers_page = paginate(Answer.objects.by_question(pk), request)
                return redirect(reverse('answers_for_questions', kwargs={'pk': pk}) + f"?page={answers_page.paginator.num_pages}")

        popular_tags = Tag.objects.popular_tags()
        best_members = Profile.objects.best_members()

        return render(request, 'question.html', {'form': form,
                                                 'question': question,
                                                 'answers': question_answers,
                                                 'popular_tags': popular_tags,
                                                 'best_members': best_members})
    except Question.DoesNotExist:
        raise Http404


def login(request):
    if (request.method == 'GET') :
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            profile = authenticate(request, **form.cleaned_data)
            if profile is not None:
                login(request, profile)
                return redirect(request.POST.get('next', '/'))
    popular_tags = Tag.objects.popular_tags()
    best_members = Profile.objects.best_members()

    return render(request, 'login.html', {'form': form,
                                          'popular_tags': popular_tags,
                                          'best_members': best_members})


@login_required
def logout_view(request):
    logout(request)
    previous_page = request.META.get('HTTP_REFERER')
    if previous_page is not None:
        return redirect(previous_page)
    return redirect("/")


def signup(request):
    if request.method == 'GET':
        form = SignupForm()
    else:
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(request.POST.get('next', '/'))
    popular_tags = Tag.objects.popular_tags()
    best_members = Profile.objects.best_members()

    return render(request, 'signup.html', {'form': form,
                                           'popular_tags': popular_tags,
                                           'best_members': best_members})


@login_required
def ask_question(request):
    if request.method == 'GET':
        form = AskForm()
    else:
        form = AskForm(request.user.profile, data=request.POST)
        if form.is_valid():
            question = form.save()
            return redirect(reverse('answers_for_questions', kwargs={'pk': question.pk}))
    popular_tags = Tag.objects.popular_tags()
    best_members = Profile.objects.best_members()

    return render(request, 'ask.html', {'form': form,
                                        'popular_tags': popular_tags,
                                        'best_members': best_members})


@login_required
def settings(request):
    form_updated = False
    if request.method == 'GET':
        form = SettingsForm(initial={'username': request.user.username, 'email': request.user.email})
        ava = ImageForm()
    else:
        form = SettingsForm(user=request.user, data=request.POST)
        ava = ImageForm(data=request.POST, files=request.FILES, instance=request.user.profile)
        if form.is_valid() and ava.is_valid():
            user = form.save()
            ava.save()
            form_updated = True
            login(request, user)
    popular_tags = Tag.objects.popular_tags()
    best_members = Profile.objects.best_members()

    return render(request, 'settings.html', {'form': form,
                                             'form_updated': form_updated,
                                             'ava': ava,
                                             'popular_tags': popular_tags,
                                             'best_members': best_members})


@require_POST
@login_required
def votes(request):
    data = request.POST
    rating = 0
    if data['type'] == 'question':
        form = LikeQuestionForm(user=request.user.profile, question=data['id'], is_like=(data['action'] == 'like'))
        rating = form.save()
    elif data['type'] == 'answer':
        form = LikeAnswerForm(user=request.user.profile, answer=data['id'], is_like=(data['action'] == 'like'))
        rating = form.save()

    return JsonResponse({'rating': rating})


@require_POST
@login_required
def is_correct(request):
    data = request.POST
    answer = Answer.objects.get(pk=data['id'])
    if Answer.objects.filter(question_id=answer.question_id, is_correct=True).count() < 3 or answer.is_correct:
        answer.change_flag_is_correct()
    return JsonResponse({'action': answer.is_correct})

# def index(request):
#     return render(request, 'index.html', {'questions': questions, "tags": sample(possible_tags, randint(3, 5))})


# def hot_questions(request):
#     return render(request, 'hot_questions.html', {'questions': questions, "tags": sample(possible_tags, randint(3, 5))})


def one_question(request, pk):
    question = questions[pk]
    return render(request, 'question.html', {"question": question, "answers": questions, "tags": sample(possible_tags, randint(3, 5))})


def ask_question(request):
    return render(request, 'ask_question.html', {})


# def tag_questions(request, tag):
#     return render(request, 'tag_questions.html',
#                   {"questions": questions, "tags": sample(possible_tags, randint(3, 5)), "tag": tag})


# def login(request):
#     return render(request, 'login.html', {})
#
#
# def signup(request):
#     return render(request, 'signup.html', {})
#
#
# def settings(request):
#     return render(request, 'settings.html', {})
