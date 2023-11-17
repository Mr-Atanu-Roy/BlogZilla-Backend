from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [

    #user auth related urls
    path('auth/login/', UserLogin.as_view(), name='api_login'),
    path('auth/signup/', UserSignup.as_view(), name='api_signup'),
    path('auth/email-verify/', EmailVerify.as_view(), name='email_verification'),
    path('auth/password-reset/', ResetPassword.as_view(), name='password_reset'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='get_refresh_token'),

    #user details & profile related urls
    path('user/me/', UserPrivateProfile.as_view(), name='user_me'),
    path('user/follow-unfollow/', FollowUnfollow.as_view(), name='follow_unfollow'),

    #other user/people details & profile related urls
    path('people/', PeopleList.as_view(), name='people_list'),
    path('people/<uuid>', PeopleRetrieve.as_view(), name='people_retrieve'),
    path('followers/<uuid>', FollowersList.as_view(), name='followers'),
    path('following/<uuid>', FollowingList.as_view(), name='following'),

    #blog related urls
    path('blogs/', BlogListCreate.as_view(), name='blog_list_create'),
    path('blogs/<uuid>', BlogRetrieveUpdateDelete.as_view(), name='blog_retrieve_update_delete'),

    #comment related urls
    path('blog/<uuid>/comments/', BlogCommentListCreate.as_view(), name='blog_comment_list_create'),
    path('blog/comments/<uuid>', BlogCommentRetrieveUpdateDelete.as_view(), name='blog_comment_retrieve_update_delete'),

    path('blog/comments/<uuid>/reply/', ReplyCommentListCreate.as_view(), name='reply_comment_list_create'),
    path('blog/comments/reply/<uuid>', ReplyCommentRetrieveUpdateDelete.as_view(), name='reply_comment_retrieve_update_delete'),


    #like related urls
    path('blog/<uuid>/likes/', BlogLikesListCreate.as_view(), name='blog_like_list_create'),
    path('blog/likes/<uuid>', BlogLikesRetrieveDelete.as_view(), name='blog_like_update_delete'),

    path('blog/comments/<uuid>/likes/', CommentLikesListCreate.as_view(), name='comment_likes_list_create'),
    path('blog/comments/likes/<uuid>', CommentLikesRetrieveDelete.as_view(), name='comment_likes_update_delete'),
    

]
