from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Question, Review, ReviewResponse

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'manager', 'position']
    list_filter = ['role']
    fieldsets = UserAdmin.fieldsets + (
        ('Company Info', {'fields': ('role', 'manager', 'position')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Company Info', {'fields': ('role', 'manager', 'position')}),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'order', 'is_active']
    list_editable = ['order', 'is_active']

class ReviewResponseInline(admin.TabularInline):
    model = ReviewResponse
    extra = 0

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewee', 'review_type', 'period', 'rating']
    list_filter = ['review_type', 'period']
    inlines = [ReviewResponseInline]

admin.site.register(User, CustomUserAdmin)
