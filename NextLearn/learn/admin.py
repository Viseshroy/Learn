from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Course, Module, Content, Assignment, Submission, Enrollment

# 1. Inline for Content inside Module
class ContentInline(admin.TabularInline):
    model = Content
    extra = 1

# 2. Admin for Module with Content inline
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    ordering = ('course', 'order')
    inlines = [ContentInline]

# 3. Inline for Module inside Course — define it BEFORE using in CourseAdmin!
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

# 4. Admin for Course with Module inline
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'instructor__username')
    inlines = [ModuleInline]

# 5. Admin for Assignment
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date')
    list_filter = ('course',)

# 6. Admin for Submission
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'file_link')
    list_filter = ('assignment',)

    def file_link(self, obj):
        if obj.file:
            return format_html("<a href='{}' target='_blank'>Download</a>", obj.file.url)
        return "No file"
    file_link.short_description = "Submission File"

# 7. Admin for Enrollment
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_on')
    list_filter = ('course', 'student')

class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'video_url', 'file_link')

    def file_link(self, obj):
        if obj.file:
            return format_html("<a href='{}' target='_blank'>Download</a>", obj.file.url)
        return "No file"
    file_link.short_description = "Attached File"


admin.site.register(Category)
admin.site.register(Course, CourseAdmin)
admin.site.register(Module, ModuleAdmin)
# admin.site.register(Content)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Content, ContentAdmin)

