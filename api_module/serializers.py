from django.db.models import Count
from rest_framework import serializers
from quiz_module.models import Option, Question, Lesson, Course, UserAnswer, QuizTaker, QuizResult


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['option', 'index', 'status']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)
    lesson = serializers.ReadOnlyField(source='lesson.lessonName')

    class Meta:
        model = Question
        fields = ['no', 'lesson', 'question', 'options']


class LessonSerializer(serializers.ModelSerializer):
    questions_no = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Lesson
        fields = ['lessonName', 'questions_no',]



class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ['courseName', 'hours', 'minutes', 'seconds', 'lessons', 'questions']


    def to_representation(self, instance):
        print(instance)
        representation = super().to_representation(instance)
        lessons = instance.lessons.all().annotate(questions_no=Count('questions'))
        representation['lessons'] = LessonSerializer(lessons, many=True).data
        questions = Question.objects.filter(lesson__course=instance)
        representation['questions'] = QuestionSerializer(questions, many=True).data
        return representation


class UserAnswerSerializer(serializers.ModelSerializer):
    option = serializers.SerializerMethodField()
    question = serializers.ReadOnlyField(source="question.question")

    def get_option(self, obj: UserAnswer):
        d = {}
        status = obj.option.status
        index = obj.option.index
        d["status"] = status
        d["index"] = index
        if not status :
            q_id = obj.question.id
            o = Option.objects.filter(question_id=q_id)
            for i in o:
                if i.status:
                    d["right_answer"] = i.index
        return d

    class Meta:
        model = UserAnswer
        fields = ['question', 'option']


class QuizTakerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    course = serializers.StringRelatedField()
    lesson = serializers.StringRelatedField()
    user_answers = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = QuizTaker
        fields = ['user', 'course', 'lesson', 'is_taken', 'start_time', 'end_time', 'user_answers', 'duration']

    def get_user_answers(self, obj):
        user_answers = UserAnswer.objects.filter(quiz_taker=obj)
        return UserAnswerSerializer(user_answers, many=True).data

    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            return duration.total_seconds() // 60
        else:
            return 0


class QuizResultSerializer(serializers.ModelSerializer):
    course = serializers.ReadOnlyField(source="course.courseName")
    total_correct = serializers.SerializerMethodField()
    total_incorrect = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = QuizResult
        fields = ['user', 'course', 'total_questions', 'total_correct', 'total_incorrect']

    def get_total_correct(self, obj):
        quiz_taker = obj.user
        user_answers = UserAnswer.objects.filter(quiz_taker__user=quiz_taker)
        correct_answers = 0
        for answer in user_answers:
            if answer.option.status:
                correct_answers += 1
        return correct_answers

    def get_total_incorrect(self, obj):
        quiz_taker = obj.user
        user_answers = UserAnswer.objects.filter(quiz_taker__user=quiz_taker)
        incorrect_answers = 0
        for answer in user_answers:
            if not answer.option.status:
                incorrect_answers += 1
        return incorrect_answers



