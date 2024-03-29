import json
from django.utils import timezone
from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from woocommerce import API
from api_module.serializers import QuizTakerSerializer, QuizResultSerializer, CourseSerializer, NotesQuestionDetailSerializer
from quiz_module.models import QuizTaker, UserModel, QuizResult, Course, UserAnswer, NotesQuestion
from utils.email_service import send_email


class QuizTakerAPIView(generics.ListAPIView):
    serializer_class = QuizTakerSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        username = self.kwargs['email']
        user = UserModel.objects.get(username=username)
        queryset = QuizTaker.objects.filter(user=user).order_by('course')
        is_taken = self.request.query_params.get('is_taken')
        if is_taken:
            queryset = queryset.filter(is_taken=is_taken)
        return queryset


class QuizResultAPIView(generics.ListAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        try:
            email = self.kwargs['email']
            user = UserModel.objects.get(email__iexact=email)

            return QuizResult.objects.filter(quiz_taker__user_id=user.id)
        except:
            return ""


class CourseAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        try:
            user_email = self.kwargs['email']
            user = UserModel.objects.get(email__iexact=user_email)
            courses = user.course
            return courses
        except:
            return ""

    def list(self, request, *args, **kwargs):
        courses = self.get_queryset()
        serializer = self.get_serializer(courses, many=True)
        if not serializer.data:
            return Response("not exist")
        response_data = {"courses": serializer.data}

        return Response(response_data)


class NotesQuestionAPIView(generics.ListAPIView):
    serializer_class = NotesQuestionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        try:
            email = self.kwargs['email']
            user = UserModel.objects.get(email__iexact=email)
            notes = NotesQuestion.objects.filter(user_answer__quiz_taker__user=user)
            return notes
        except:
            return ""

    def list(self, request, *args, **kwargs):
        notes = self.get_queryset()
        serializer = self.get_serializer(notes, many=True)
        if not serializer.data:
            return Response("not exist")
        response_data = serializer.data
        return Response(response_data)


# todo: add course to user
# todo: update user courses


@csrf_exempt
def signup(request: HttpRequest):
    if request.method == "POST":
        try:
            data1 = json.loads(request.body.decode())
            user_email = data1['email']
            user_order_id = int(data1['course_id'])
            wcapi = API(
                url="https://medical-exam.ir",
                consumer_key="ck_d90ea6be7f2881cbd8f23d51b6be390a6300b9ea",
                consumer_secret="cs_537364de74126923605ea3e1169b9e74b8d2527e",
                wp_api=True,
                version="wc/v3",
                query_string_auth=True
            )

            data: dict = wcapi.get('orders').json()

            flag_user_wrong_id_exist = False
            flag_course_id_not_exist = False

            for i in data:
                print(i["id"], user_order_id)
                if i["id"] == user_order_id:
                    if i['billing']['email'] == user_email:
                        user_exist: bool = UserModel.objects.filter(email__iexact=user_email).exists()
                        if user_exist:
                            return JsonResponse(
                                {'error': 'That username has already exist.'},
                                status=400
                            )
                        else:
                            course = Course.objects.get(course_id=user_order_id)
                            password = UserModel.objects.make_random_password(length=15, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*")
                            user = UserModel(username=user_email,
                                             email=user_email,
                                             is_active=True,
                                             is_staff=False,
                                             is_superuser=False,
                                             first_name=i['billing']['first_name'],
                                             last_name=i['billing']['last_name'],
                                             )

                            user.set_password(password)
                            print(password)
                            user.save()
                            user.course.add(course)
                            user.save()
                            try:
                                send_email("Activated Account",
                                           user.email,
                                           {"username": user.email, "password": password},
                                           "info_email.html")
                                flag_user_wrong_id_exist = False
                                flag_course_id_not_exist = False
                                return JsonResponse({"signup": "ok (email sent)"}, status=201)

                            except:
                                return JsonResponse({"signup": "fail"}, status=400)

                    else:
                        flag_user_wrong_id_exist = True

                else:
                    flag_course_id_not_exist = True

            if flag_course_id_not_exist or flag_user_wrong_id_exist:
                return JsonResponse(
                    {'error': "course id or email is wrong or didn't match (try again)"},
                    status=404
                )

        except:
            return JsonResponse(
                {'error': 'Errorrrrrrrrrrr'},
                status=400
            )

    else:
        return JsonResponse(
            {'error': 'bad req'},
            status=400
        )


@csrf_exempt
def log_in(request: HttpRequest):
    if request.method == "POST":
        try:
            data1 = json.loads(request.body.decode())
            user_email = data1['email']
            user_password = data1['password']
            user = UserModel.objects.filter(email__iexact=user_email).first()
            if user is None:
                return JsonResponse({'error': 'user does not exist'}, status=400)
            else:
                is_pass_correct = user.check_password(user_password)
                if is_pass_correct:
                    return JsonResponse({'login': 'ok'}, status=200)
                return JsonResponse({'error': "can't login (user or pass incorrect)"}, status=400)
        except:
            return JsonResponse({'error': 'error'}, status=400)


@csrf_exempt
def forgot(request: HttpRequest):
    data1 = json.loads(request.body.decode())
    email = data1["email"]
    user: UserModel = UserModel.objects.filter(email__iexact=email).first()
    if user is not None:
        password = UserModel.objects.make_random_password(length=15, allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*")
        send_email("Password Changed",
                   user.email,
                   {"username": user.email, "password": password},
                   "forgot_pass.html")
        user.set_password(password)
        user.save()
        return JsonResponse({"change password": "ok"}, status=200)
    else:
        return JsonResponse({"error": "user not found"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def start_quiz(request: HttpRequest):
    if request.method == "POST":
        try:
            data1 = json.loads(request.body.decode())
            email = data1["email"]
            course_id = data1["course_id"]
            lesson_name = data1["lesson_name"]
            user = UserModel.objects.filter(email__iexact=email).first()
            course = Course.objects.filter(course_id=course_id).first()

            if lesson_name == "all":
                lessons = course.lessons.all()
            else:
                lessons = course.lessons.filter(lessonName__iexact=lesson_name)
            for lesson in lessons:

                if QuizTaker.objects.filter(user=user, course=course, lesson=lesson).exists():
                    return JsonResponse({'error': 'this exam is already taken'}, status=400)
                else:
                    QuizTaker.objects.create(user=user,
                                             course=course,
                                             lesson=lesson,
                                             is_taken=True,
                                             start_time=timezone.now())

                return JsonResponse({'ok': 'done'}, status=201)
        except KeyError:
            return JsonResponse({'error': 'bad req'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': 'wrong info'}, status=400)
        except:
            return JsonResponse({'error': 'bad req'}, status=400)
    return JsonResponse({'error': "its not post"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def end_quiz(request: HttpRequest):
    if request.method == "POST":
        try:
            data1 = json.loads(request.body.decode())
            email = data1["email"]
            course_id = data1["course_id"]
            lesson_name = data1["lesson_name"]
            user = UserModel.objects.filter(email__iexact=email).first()
            course = Course.objects.filter(course_id=course_id).first()
            if lesson_name == "all":
                lessons = course.lessons.all()
            else:
                lessons = course.lessons.filter(lessonName__iexact=lesson_name)
            if not lessons:
                return JsonResponse({"error": "lesson vojod nadarad"}, status=400)
            for lesson in lessons:
                taker = QuizTaker.objects.get(user=user,
                                              course=course,
                                              lesson=lesson)
                taker.end_time = timezone.now()
                taker.save()
            return JsonResponse({"ok": "set end time successfully"}, status=202)
        except:
            return JsonResponse({'error': 'bad req'}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def question_answer(request: HttpRequest):
    if request.method == "POST":
        data1 = json.loads(request.body.decode())
        user = UserModel.objects.filter(email__iexact=data1["email"]).first()
        course = Course.objects.filter(course_id=data1["course_id"]).first()
        lesson = course.lessons.filter(lessonName__iexact=data1["lesson_name"]).first()
        taker = QuizTaker.objects.filter(user=user,
                                         course=course,
                                         lesson=lesson).first()
        if taker:
            question = lesson.questions.get(no=data1["question_number"])
            try:
                option = question.options.get(index=data1["index"])
                created_user_answer = UserAnswer.objects.get_or_create(quiz_taker=taker,
                                                                       question=question,
                                                                       option=option)
                if not created_user_answer[1]:
                    return JsonResponse({"error": "already answered"}, status=400)
                taker_result = QuizResult.objects.filter(quiz_taker=taker).first()
                if taker_result is None:
                    taker_result = QuizResult.objects.create(quiz_taker=taker,
                                                             total_questions=0,
                                                             total_correct=0,
                                                             total_incorrect=0)

            except:

                created_user_answer = UserAnswer.objects.get_or_create(quiz_taker=taker,
                                                                       question=question, )
                if not created_user_answer[1]:
                    return JsonResponse({"error": "already answered"}, status=400)
                taker_result = QuizResult.objects.filter(quiz_taker=taker).first()
                if taker_result is None:
                    taker_result = QuizResult.objects.create(quiz_taker=taker,
                                                             total_questions=0,
                                                             total_correct=0,
                                                             total_incorrect=0)

            taker_result.total_questions += 1
            correct_option = question.options.get(status=True).index
            if data1["index"] == correct_option:
                taker_result.total_correct += 1
            else:
                taker_result.total_incorrect += 1
            taker_result.save()

            NotesQuestion.objects.create(user_answer=created_user_answer[0],
                                         note=data1["note"])
        else:
            return JsonResponse({"error": "take the lesson started first"}, status=400)
        return JsonResponse({"ok": "ok"}, status=201)
