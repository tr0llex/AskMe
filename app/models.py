from django.db import models
from django.contrib.auth.models import User


class ProfileManager(models.Manager):
    def best_members(self):
        return self.order_by('-rating')[:10]


class Profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Профиль')
    avatar = models.ImageField(upload_to='avatars/%y/%m/%d', verbose_name='Аватар')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    objects = ProfileManager()

    def __str__(self):
        return self.user_id.get_username()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class TagManager(models.Manager):
    def add_tags_to_question(self, added_tags):
        tags = self.filter(tag__in=added_tags)
        for tag in tags:
            tag.rating += 1
            tag.save()
        return tags

    def popular_tags(self):
        return self.order_by('-rating')[:15]


class Tag(models.Model):
    tag = models.CharField(unique=True, max_length=16, verbose_name='Тег')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    objects = TagManager()

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class QuestionManager(models.Manager):
    def new_questions(self):
        return self.order_by('-date_added')

    def hot_questions(self):
        return self.order_by('-rating')

    def by_tag(self, tag):
        return self.filter(tags__tag=tag).order_by('-rating')


class Question(models.Model):
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст вопроса')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    number_of_answers = models.IntegerField(default=0, verbose_name='Количество ответов')

    objects = QuestionManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class AnswerManager(models.Manager):
    def by_question(self, pk):
        return self.filter(question_id=pk).order_by('-rating')


class Answer(models.Model):
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Профиль')
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.TextField(verbose_name='Текст ответа')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_correct = models.BooleanField(default=False, verbose_name='Флаг правильного ответа')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    objects = AnswerManager()

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if not self.pk:
            self.question_id.number_of_answers += 1
            self.question_id.save()
        super(Answer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.question_id.number_of_answers -= 1
        self.question_id.save()
        super(Answer, self).delete(*args, **kwargs)

    def change_flag_is_correct(self):
        self.is_correct = not self.is_correct
        self.save()

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class LikeQuestion(models.Model):
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name='Вопрос')
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Профиль')
    is_like = models.BooleanField(default=True, verbose_name='Лайк или дизлайк')

    def __str__(self):
        action = 'дизлайкнул'
        if self.is_like:
            action = 'лайкнул'
        return f'{self.profile_id.user_id.get_username()} {action} вопрос: {self.question_id.title}'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.is_like:
                self.question_id.rating += 1
            else:
                self.question_id.rating -= 1
            self.question_id.save()
        super(LikeQuestion, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_like:
            self.question_id.rating -= 1
        else:
            self.question_id.rating += 1
        self.question_id.save()
        super(LikeQuestion, self).delete(*args, **kwargs)

    def change_flag_is_like(self):
        if self.is_like:
            self.question_id.rating += 2
        else:
            self.question_id.rating -= 2
        self.is_like = not self.is_like
        self.save()
        self.question_id.save()

    class Meta:
        unique_together = ('question_id', 'profile_id')
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'


class LikeAnswer(models.Model):
    answer_id = models.ForeignKey('Answer', on_delete=models.CASCADE, verbose_name='Ответ')
    profile_id = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name='Профиль')
    is_like = models.BooleanField(default=True, verbose_name='Лайк или дизлайк')

    def __str__(self):
        action = 'дизлайкнул'
        if self.is_like:
            action = 'лайкнул'
        return f'{self.profile_id.user_id.get_username()} {action} ответ: {self.answer_id.text}'

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.is_like:
                self.answer_id.rating += 1
            else:
                self.answer_id.rating -= 1
            self.answer_id.save()
        super(LikeAnswer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_like:
            self.answer_id.rating -= 1
        else:
            self.answer_id.rating += 1
        self.answer_id.save()
        super(LikeAnswer, self).delete(*args, **kwargs)

    def change_flag_is_like(self):
        if self.is_like:
            self.answer_id.rating += 2
        else:
            self.answer_id.rating -= 2
        self.is_like = not self.is_like
        self.save()
        self.answer_id.save()

    class Meta:
        unique_together = ('answer_id', 'profile_id')
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
