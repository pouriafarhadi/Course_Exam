# from django.contrib.auth import login
# from django.http import HttpRequest, HttpResponse
# from django.shortcuts import render
# from django.views import View
# from woocommerce import API
# from quiz_module.forms import SignUpModelForm, LoginModelForm
# from quiz_module.models import UserModel, Course
#
#
# class RegisterView(View):
#     def get(self, request):
#         signupform = SignUpModelForm()
#         return render(request, "quiz_module/register.html", {"form": signupform})
#
#     def post(self, request: HttpRequest):
#         signupform = SignUpModelForm(request.POST)
#         if signupform.is_valid():
#             user_email = signupform.cleaned_data.get('email')
#             user_order_id = signupform.cleaned_data.get('user_id')
#             wcapi = API(
#                 url="https://medical-exam.ir",
#                 consumer_key="ck_d90ea6be7f2881cbd8f23d51b6be390a6300b9ea",
#                 consumer_secret="cs_537364de74126923605ea3e1169b9e74b8d2527e",
#                 wp_api=True,
#                 version="wc/v3",
#                 query_string_auth=True  # Force Basic Authentication as query string true and using under HTTPS
#             )
#             data: dict = wcapi.get('orders').json()
#             for i in data:
#                 if i["id"] == user_order_id:
#                     if i['billing']['email'] == user_email:
#                         user_exist: bool = UserModel.objects.filter(username__iexact=user_email).exists()
#                         if user_exist:
#                             signupform.add_error('email', "in karbar az ghabl vojod darad")
#                         else:
#                             course = Course.objects.get(couse_id=user_order_id)
#                             password = UserModel.objects.make_random_password()
#                             user = UserModel(username=user_email,
#                                              is_active=False,
#                                              is_staff=False,
#                                              is_superuser=False,
#                                              first_name=i['billing']['first_name'],
#                                              last_name=i['billing']['last_name'],
#                                              )
#
#                             user.set_password(password)
#
#                             print(password)
#                             user.save()
#                             user.course.add(course)
#                             user.save()
#                             # todo: send activation code
#                             # todo: send username and password
#                             return HttpResponse("okaye")
#
#                     else:
#                         signupform.add_error('email', "id doroste vali email ghalate")
#
#                 else:
#                     signupform.add_error('user_id', "in id vojod nadarad")
#                 return render(request, "quiz_module/register.html", {"form": signupform})
#         return render(request, "quiz_module/register.html", {"form": signupform})
#
#
# class LoginView(View):
#     def get(self, request: HttpRequest):
#         loginform = LoginModelForm()
#         return render(request, "quiz_module/login.html", {"form": loginform})
#
#     def post(self, request: HttpRequest):
#         loginform = LoginModelForm(request.POST)
#
#         if loginform.is_valid():
#             user_email = loginform.cleaned_data.get("email")
#             user_password = loginform.cleaned_data.get("password")
#             user: UserModel = UserModel.objects.filter(username__iexact=user_email).first()
#             if user is not None:
#                 is_password_correct = user.check_password(user_password)
#                 if is_password_correct:
#                     login(request, user)
#                     return HttpResponse('shoma login shodin')
#                 else:
#                     loginform.add_error('password', 'in karbar vojod nadarad (passwrod dorost nist)')
#             else:
#                 loginform.add_error("email", 'in karbar vojod nadarad (email esh nist)')
#
#         return render(request, "quiz_module/login.html", {"form": loginform})
