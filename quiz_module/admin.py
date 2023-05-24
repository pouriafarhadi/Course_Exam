from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin


class EmployeeAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "course", "phone_number"),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "course", "phone_number")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


admin.site.register(models.UserModel, EmployeeAdmin)
admin.site.register(models.Course)
admin.site.register(models.Lesson)
admin.site.register(models.Question)
admin.site.register(models.Option)
admin.site.register(models.QuizTaker)
admin.site.register(models.UserAnswer)
admin.site.register(models.QuizResult)
admin.site.register(models.NotesQuestion)

# user
"""
pouria
pouria@pouria.com
123
"""
# amirhajif2@gmail.com / vFe7Xwa93k / "token": "a6277616815ed5c4cf164c6ea9d2f0599fc7faf8"
