from django.urls import path

from api_module.views import QuizTakerAPIView, question_answer, end_quiz, start_quiz, QuizResultAPIView, CourseAPIView, signup, log_in, forgot, NotesQuestionAPIView

urlpatterns = [

    # Courses

    path('courses/<str:email>/', CourseAPIView.as_view(), name='courses'),
    path('quiz-taker/<str:email>/', QuizTakerAPIView.as_view(), name='quiz-taker-list'),
    path('quiz-taker/<str:email>/result/', QuizResultAPIView.as_view(), name='quiz-result'),
    path('q_notes/<str:email>/', NotesQuestionAPIView.as_view(), name="question_notes"),

    # take quiz
    path('start-quiz/', start_quiz),
    path('end-quiz/', end_quiz),

    # question_answer
    path('question-answer/', question_answer),


    # Auth
    path("signup", signup, name="register_page"),
    path("login", log_in, name="login_page"),
    path("forgot", forgot, name="forgot_page")
]





