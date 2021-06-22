from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag, LikeQuestion, LikeAnswer
from random import choice, sample, randint
from faker import Faker

f = Faker()


class Command(BaseCommand):
    help = 'Fill test database'

    def add_arguments(self, parser):
        parser.add_argument('--full', nargs='+', type=int)
        parser.add_argument('--users', nargs='+', type=int)
        parser.add_argument('--questions', nargs='+', type=int)
        parser.add_argument('--answers', nargs='+', type=int)
        parser.add_argument('--tags', nargs='+', type=int)
        parser.add_argument('--likes', nargs='+', type=int)

        parser.add_argument('--dusers', nargs='+', type=int)
        parser.add_argument('--dlikes', nargs='+', type=int)

    def handle(self, *args, **options):
        if options['full']:
            self.fill_full_db(options['full'][0])

        if options['users']:
            self.fill_users(options['users'][0])

        if options['tags']:
            self.fill_tags(options['tags'][0])

        if options['questions']:
            self.fill_questions(options['questions'][0])

        if options['answers']:
            self.fill_answers(options['answers'][0])

        if options['likes']:
            self.fill_likes_questions(options['likes'][0])
            self.fill_likes_answers(2 * options['likes'][0])

        if options['dusers']:
            self.delete_users()

        if options['dlikes']:
            self.delete_likes()

    @staticmethod
    def fill_users(count):
        for i in range(count):
            name = f.user_name()
            while User.objects.filter(username=name).exists():
                name = f.user_name()
            Profile.objects.create(
                user_id=User.objects.create_user(
                    username=name,
                    email=f.email(),
                    password='qwert'),
                avatar=f'img/avatars/{i}.png',
            )

    @staticmethod
    def fill_tags(count):
        for i in range(count):
            tag = f.word()
            while Tag.objects.filter(tag=tag).exists():
                tag = f.word()
            Tag.objects.create(tag=tag)

    @staticmethod
    def fill_questions(count):
        profiles = list(Profile.objects.values_list('id', flat=True))
        for i in range(count):
            current_question = Question.objects.create(
                profile_id=Profile.objects.get(pk=choice(profiles)),
                title=f.sentence(),
                text=f.text(),
            )
            tags = list(Tag.objects.values_list('tag', flat=True))
            tags_for_question = sample(tags, k=randint(1, 5))
            current_question.tags.set(Tag.objects.add_tags_to_question(tags_for_question))

    @staticmethod
    def fill_answers(count):
        profiles = list(Profile.objects.values_list('id', flat=True))
        questions = list(Question.objects.values_list('id', flat=True))
        for i in range(count):
            Answer.objects.create(
                profile_id=Profile.objects.get(pk=choice(profiles)),
                question_id=Question.objects.get(pk=choice(questions)),
                text=f.text(),
                is_correct=randint(0, 1),
            )

    @staticmethod
    def fill_likes_questions(count):
        iterator = 0
        for question in Question.objects.all():
            profiles = list(Profile.objects.values_list('id', flat=True))
            current_profiles = Profile.objects.filter(id__in=sample(profiles, k=randint(0, 10)))
            for profile in current_profiles:
                LikeQuestion.objects.create(
                    question_id=question,
                    profile_id=profile,
                )
                iterator += 1
                if iterator == count:
                    break
            if iterator == count:
                break

    @staticmethod
    def fill_likes_answers(count):
        iterator = 0
        for answer in Answer.objects.all():
            profiles = list(Profile.objects.values_list('id', flat=True))
            current_profiles = Profile.objects.filter(id__in=sample(profiles, k=randint(0, 15)))
            for profile in current_profiles:
                LikeAnswer.objects.create(
                    answer_id=answer,
                    profile_id=profile,
                )
                iterator += 1
                if iterator == count:
                    break
            if iterator == count:
                break

    @staticmethod
    def delete_users():
        Profile.objects.all().delete()
        User.objects.all().delete()

    @staticmethod
    def delete_likes():
        LikeQuestion.objects.all().delete()
        LikeAnswer.objects.all().delete()

    def fill_full_db(self, count):
        self.fill_users(count)
        print('Users are created')
        self.fill_tags(count)
        print('Tags are created')
        self.fill_questions(count * 10)
        print('Questions are created')
        self.fill_answers(count * 100)
        print('Answers are created')
        self.fill_likes_questions(count * 100)
        print('Likes for questions are created')
        self.fill_likes_answers(count * 200)
        print('Likes for answers are created')
