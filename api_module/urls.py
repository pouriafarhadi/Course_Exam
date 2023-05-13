from django.urls import path

from api_module.views import QuizTakerAPIView, question_answer, end_quiz, start_quiz, QuizResultAPIView, CourseAPIView, signup, log_in

urlpatterns = [

    # Courses

    path('courses/<str:email>', CourseAPIView.as_view(), name='courses'),
    path('quiz-taker/<str:username>', QuizTakerAPIView.as_view(), name='quiz-taker-list'),
    path('quiz-taker/<str:username>/result/', QuizResultAPIView.as_view(), name='quiz-result'),

    # take quiz
    path('start-quiz/', start_quiz),
    path('end-quiz/', end_quiz),

    # question_answer
    path('question-answer/', question_answer),


    # Auth
    path("signup", signup, name="register_page"),
    path("login", log_in, name="login_page"),
]




#todo : think about creating a user
