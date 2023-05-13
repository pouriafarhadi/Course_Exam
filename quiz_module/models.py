from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Course(models.Model):
    courseName = models.CharField(max_length=50)
    course_id = models.IntegerField(null=True)
    hours = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(24)])
    minutes = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(60)])
    seconds = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(60)])

    def __str__(self):
        return self.courseName


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    lessonName = models.CharField(max_length=200)
    questionsNo = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.lessonName}({self.course})"


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    no = models.IntegerField()
    question = models.TextField()

    def __str__(self):
        return f"{self.question}|{self.lesson}"


class Option(models.Model):
    indexes = [
        ('a', "a"),
        ('b', "b"),
        ('c', "c"),
        ('d', "d"),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.CharField(max_length=350, )
    index = models.CharField(max_length=1, choices=indexes, null=True)
    status = models.BooleanField()

    def __str__(self):
        return f"{self.option}|{self.question}"


class UserModel(AbstractUser):
    course = models.ManyToManyField(Course, null=True)
    phone_number = models.IntegerField(null=True)

    def __str__(self):
        return self.username


class QuizTaker(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_taken = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"({self.user})|{self.lesson}"


class UserAnswer(models.Model):
    quiz_taker = models.ForeignKey(QuizTaker, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.quiz_taker}/{self.question.no}/{self.option.status}"


class QuizResult(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    total_questions = models.PositiveIntegerField()
    total_correct = models.PositiveIntegerField()
    total_incorrect = models.PositiveIntegerField()
