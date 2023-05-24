from django.db.models import Count
from rest_framework import serializers
from quiz_module.models import Option, Question, Lesson, Course, UserAnswer, QuizTaker, QuizResult, NotesQuestion


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
        fields = ['lessonName', 'questions_no', ]


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['courseName', 'hours', 'minutes', 'seconds', 'lessons', 'questions']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        lessons = instance.lessons.all().annotate(questions_no=Count('questions'))
        representation['lessons'] = LessonSerializer(lessons, many=True).data
        questions = Question.objects.filter(lesson__course=instance)
        representation['questions'] = QuestionSerializer(questions, many=True).data
        return representation


class NotesQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotesQuestion
        fields = ["note", "create_time", "update_time"]


class NotesQuestionDetailSerializer(serializers.ModelSerializer):
    note_detail = serializers.SerializerMethodField()

    def get_note_detail(self, obj: NotesQuestion):
        d = {"course": obj.user_answer.quiz_taker.course.courseName, "lesson": obj.user_answer.quiz_taker.lesson.lessonName, "question": obj.user_answer.question.question, "question_no": obj.user_answer.question.no}
        return d

    class Meta:
        model = NotesQuestion
        fields = ["note_detail", "note", "create_time", "update_time"]


class UserAnswerSerializer(serializers.ModelSerializer):
    option = serializers.SerializerMethodField()
    question = serializers.ReadOnlyField(source="question.question")
    question_number = serializers.ReadOnlyField(source="question.no")
    note = serializers.SerializerMethodField()

    def get_option(self, obj: UserAnswer):
        d = {}
        try:
            status = obj.option.status
            index = obj.option.index
        except:
            status = ""
            index = ""
        d["status"] = status
        d["index"] = index
        if not status:
            q_id = obj.question.id
            o = Option.objects.filter(question_id=q_id)
            for i in o:
                if i.status:
                    d["right_answer"] = i.index
        return d

    def get_note(self, obj: UserAnswer):
        try:
            note = NotesQuestion.objects.get(user_answer=obj)
            return NotesQuestionSerializer(note).data
        except:
            return ""

    class Meta:
        model = UserAnswer
        fields = ['question', 'question_number', 'option', 'note']


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
    quiz_taker = serializers.SerializerMethodField()

    class Meta:
        model = QuizResult
        fields = ["quiz_taker", "total_questions", "total_correct", "total_incorrect"]

    def get_quiz_taker(self, obj: QuizResult):
        d = {"course": obj.quiz_taker.course.courseName, "lesson": obj.quiz_taker.lesson.lessonName}
        return d
