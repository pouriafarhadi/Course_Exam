# from django import forms
# from quiz_module.models import UserModel
#
#
# class SignUpModelForm(forms.ModelForm):
#     class Meta:
#         model = UserModel
#         fields = [
#             "email",
#             "first_name"
#         ]
#
#     def clean_user_id(self):
#         if len(self.cleaned_data["first_name"]) != 4:
#             raise forms.ValidationError("bayad 4 ragham bashe")
#         return int(self.cleaned_data["first_name"])
#
#
# class LoginModelForm(forms.ModelForm):
#     class Meta:
#         model = UserModel
#         fields = [
#             "email",
#             "password"
#         ]
