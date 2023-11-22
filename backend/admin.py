from django.contrib import admin

from .models import User, UserProfile, Tokens, Blog, BlogComments, BlogLikes, ReplyComments, LikeComments

# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    classes = ['collapse']


class BlogCommentsInline(admin.StackedInline):
    model = BlogComments
    extra = 0
    classes = ['collapse']

class BlogLikesInline(admin.TabularInline):
    model = BlogLikes
    extra = 0
    classes = ['collapse']


class ReplyCommentsInline(admin.TabularInline):
    model = ReplyComments
    extra = 0
    classes = ['collapse']


class LikeCommentsInline(admin.TabularInline):
    model = LikeComments
    extra = 0
    classes = ['collapse']
    


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'is_verified', 'date_joined', 'is_staff')
    
    fieldsets = [
        ("User Details", {
            "fields": (
                ['email', 'password', 'phone', 'first_name', 'last_name', 'profession', 'country', 'profile_pic']
            ),
        }),
        ("More Details", {
            "fields": (
                ['is_verified', 'date_joined', 'last_login', 'last_logout']
            ), 'classes': ['collapse']
        }),
        ("Permissions", {
            "fields": (
                ['is_staff', 'is_superuser', 'is_active', 'user_permissions', 'groups']
            ), 'classes': ['collapse']
        }),
    ]
    
    inlines = [UserProfileInline]


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'profile_is_complete')
    
    fieldsets = [
        ("User Details", {
            "fields": (
                ['user', 'bio', 'website', 'interests']
            ),
        }),
        ("More Details", {
            "fields": (
                ['profile_is_complete', 'following', 'followers']
            ),
        }),
        # ("Plan Details", {
        #     "fields": (
        #         ['plan', 'last_paid', 'plan_expiry']
        #     ),
        # }),
        
    ]

    
class BlogAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'published', 'created_at')
    
    fieldsets = [
        ("Blog Details", {
            "fields": (
                ['user', 'published', 'title', 'tags', 'content', 'header_img', 'likes_no', 'comments_no']
            ),
        }),
                
    ]

    inlines = [BlogLikesInline, BlogCommentsInline]


class BlogCommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'created_at')
    
    fieldsets = [
        ("Blog Comments Details", {
            "fields": (
                ['user', 'blog', 'comment', 'likes_no', 'comments_no']
            ),
        }),
                
    ]

    inlines = [ReplyCommentsInline]


class BlogLikesAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'created_at')
    
    fieldsets = [
        ("Blog Comments Details", {
            "fields": (
                ['user', 'blog']
            ),
        }),
                
    ]


class ReplyCommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent_blog_comment', 'parent_reply_comment', 'created_at')
    
    fieldsets = [
        ("Blog Comments Details", {
            "fields": (
                ['user', 'parent_blog_comment', 'parent_reply_comment', 'comment', 'likes_no', 'comments_no']
            ),
        }),
                
    ]

    inlines = [ReplyCommentsInline, LikeCommentsInline]

   
class LikeCommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent_blog_comment', 'parent_reply_comment', 'created_at')
    
    fieldsets = [
        ("Blog Comments Details", {
            "fields": (
                ['user', 'parent_blog_comment', 'parent_reply_comment']
            ),
        }),
                
    ]


#Registering user model   
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Tokens)
admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogComments, BlogCommentsAdmin)
admin.site.register(BlogLikes, BlogLikesAdmin)
admin.site.register(ReplyComments, ReplyCommentsAdmin)
admin.site.register(LikeComments, LikeCommentsAdmin)