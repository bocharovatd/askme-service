from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class ProfileManager(models.Manager):
    def get_top(self):
        # 10 users who asked the most popular questions or gave the most popular answers in the last week
        last_week = timezone.now() - timezone.timedelta(days=7)
        return self.filter(
            Q(question__created_at__gte=last_week) |
            Q(answer__created_at__gte=last_week)
        ).distinct(
        ).annotate(
            nquestionlikes=Count(
                'question__questionscore',
                filter=Q(question__questionscore__type=1, question__created_at__gte=last_week),
            ),
            nanswerlikes=Count(
                'answer__answerscore',
                filter=Q(answer__answerscore__type=1, answer__created_at__gte=last_week),
            )
        ).order_by('-nquestionlikes', '-nanswerlikes')[:10]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    objects = ProfileManager()


class QuestionManager(models.Manager):
    def get_current(self):
        return self.order_by('created_at').reverse()

    def get_hot(self):
        return self.annotate(nlikes=Count('questionscore')).order_by('-nlikes')


class Question(models.Model):
    title = models.TextField()
    text = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    objects = QuestionManager()
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [GinIndex(fields=["search_vector", ]), ]


class ScoreManager(models.Manager):
    def likes(self):
        return self.get_queryset().filter(type__gt=0)

    def dislikes(self):
        return self.get_queryset().filter(type__lt=0)

    def sum_rating(self):
        return self.get_queryset().aggregate(Sum('type')).get('type__sum') or 0


class QuestionScore(models.Model):
    TYPE = {1: 'like', -1: 'dislike'}
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    type = models.IntegerField(choices=TYPE)
    objects = ScoreManager()

    class Meta:
        unique_together = ('user', 'question')


class Answer(models.Model):
    text = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class AnswerScore(models.Model):
    TYPE = {1: 'like', -1: 'dislike'}
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    type = models.IntegerField(choices=TYPE)
    objects = ScoreManager()

    class Meta:
        unique_together = ('user', 'answer')


class TagManager(models.Manager):
    def get_top(self):
        # 10 tags with the most amount of questions in the last 3 months
        three_months = timezone.now() - timezone.timedelta(days=90)
        return self.annotate(
            nquestions=Count(
                'questions',
                filter=Q(questions__created_at__gte=three_months))
        ).order_by('-nquestions')[:10]


class Tag(models.Model):
    name = models.TextField()
    questions = models.ManyToManyField(Question)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    objects = TagManager()
