from django.contrib import auth
from django.http import Http404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView, 
    RetrieveAPIView, 
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveDestroyAPIView, 
    RetrieveUpdateDestroyAPIView, 
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permission import IsOwnerOrReadOnly, BlogPermission


from .serializers import (
    UserLoginSerializer,
    UserSignupSerializer,

    EmailVerifyLinkSendSerializer,
    EmailVerifySerializer,

    ResetPasswordLinkSendSerializer,
    ResetPasswordSerializer,

    UserPrivateSerializer,
    UserPublicSerializer,

    PeoplePublicSerializer,

    FollowUnfollowSerializer,

    BlogSerializer,

    BlogCommentsSerializer,
    ReplyCommentsSerializer,

    BlogLikesSerializer,
    CommentsLikeSerializer
)

from backend.models import (
    User, UserProfile, 
    Blog, BlogComments, 
    BlogLikes, ReplyComments, LikeComments
)
from .filters import (
    NameFilterBackend, 
    CountryFilterBackend, 
    BlogFilterBackend, 
    LatestFilterBackend, 
)

from .utils import get_token

# Create your views here.

class UserLogin(APIView):

    def post(self, request):

        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                # get email and password if data is valid 
                email = serializer.validated_data.get("email")
                password = serializer.validated_data.get("password")
                
                #authenticate the user            
                user = auth.authenticate(request, email=email, password=password)
                
                if user is not None:
                    if user.is_verified:            
                        #get tokens for user is user exists
                        tokens = get_token(user)
                        
                        if tokens is not None:
                            response = {
                                "status": HTTP_200_OK,
                                "data" : tokens,
                                "message" : "Login successful.",
                                "error": None
                            }

                            status=HTTP_200_OK

                        else:
                            response = {
                                "status": HTTP_400_BAD_REQUEST,
                                "data" : {
                                    "access": None,
                                    "refresh": None
                                },
                                "message": "Could not generate tokens.",
                                "error" : "Invalid credentials."
                            }
                            status=HTTP_400_BAD_REQUEST
                    
                    else:
                            response = {
                                "status": HTTP_400_BAD_REQUEST,
                                "data" : {
                                    "access": None,
                                    "refresh": None
                                },
                                "message": "User's email is not verified.",
                                "error" : "Email not verified."
                            }
                            status=HTTP_400_BAD_REQUEST
                else:
                    #return this if data is not valid
                    response = {
                        "status": HTTP_400_BAD_REQUEST,
                        "data" : {
                            "access": None,
                            "refresh": None
                        },
                        "message": "User does not exists.",
                        "error" : "Invalid credentials."
                    }
                    
                    status=HTTP_400_BAD_REQUEST
                    
            
            else:
                #return this if email and password is not given
                response = {
                    "status": HTTP_400_BAD_REQUEST,
                    "data" : {
                        "access": None,
                        "refresh": None
                    },
                    "message": "Invalid data.",
                    "error" : serializer.errors
                }
                status = HTTP_400_BAD_REQUEST
        
        except Exception as e:
            #return this in case of any error
            response = {
                    "status": HTTP_500_INTERNAL_SERVER_ERROR,
                    "data" : {
                        "access": None,
                        "refresh": None
                    },
                    "message" : "Internal server error.",
                    "error": None
                }
            status = HTTP_500_INTERNAL_SERVER_ERROR
        
        

        return Response(response, status)



class UserSignup(APIView):
    
    def post(self, request):

        try:
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                new_user = serializer.save()

                #check if user is created
                if new_user:
                    response = {
                            "status" : HTTP_201_CREATED,
                            "data" : serializer.data, 
                            "message" : "User created successfully.",
                            "error": None
                        }

                    status = HTTP_201_CREATED
                
                else:
                    response = {
                        "status" : HTTP_500_INTERNAL_SERVER_ERROR,
                        "data" : serializer.data,
                        "message" : "Failed to create user.",
                        "error": None
                    }

                    status = HTTP_500_INTERNAL_SERVER_ERROR

            else:
                response = {
                    "status" : HTTP_400_BAD_REQUEST,
                    "data" : serializer.data,
                    "message": "Invalid data.",
                    "error" : serializer.errors
                }

                status = HTTP_400_BAD_REQUEST
        
        except Exception as e:
            #return this in case of any error
            response = {
                    "status": HTTP_500_INTERNAL_SERVER_ERROR,
                    "data" : request.data,
                    "message" : "Internal server error.",
                    "error": None 
                }
            status = HTTP_500_INTERNAL_SERVER_ERROR
        
        

        return Response(response, status)



class EmailVerify(APIView):

    def get(self, request):
        try:
            
            serializer = EmailVerifyLinkSendSerializer(data=request.data)
            if serializer.is_valid():
                response = {
                    "status": HTTP_200_OK,
                    "data" : None,
                    "message" : "Email verification link sent successfully.",
                    "error": None 
                }
                status = HTTP_200_OK
            else:
                response = {
                    "status": HTTP_400_BAD_REQUEST,
                    "data" : serializer.data,
                    "message" : "Invalid data.",
                    "error": serializer.errors 
                }
                status = HTTP_400_BAD_REQUEST
            
        except Exception as e:

            response = {
                    "status": HTTP_500_INTERNAL_SERVER_ERROR,
                    "data" : request.data,
                    "message" : "Internal server error.",
                    "error": None 
                }
            status = HTTP_500_INTERNAL_SERVER_ERROR
        
        
        return Response(response, status)
    

    def post(self, request):
        try:
            serializer = EmailVerifySerializer(data=request.data)
            if serializer.is_valid():
                response = {
                    "status": HTTP_200_OK,
                    "data" : None,
                    "message" : "Email verified successfully.",
                    "error": None 
                }
                status = HTTP_200_OK
        
            else:
                response = {
                    "status": HTTP_400_BAD_REQUEST,
                    "data" : serializer.data,
                    "message" : "Invalid data.",
                    "error": serializer.errors 
                }
                status = HTTP_400_BAD_REQUEST
        
        except Exception as e:
             #return this in case of any error
            response = {
                    "status": HTTP_500_INTERNAL_SERVER_ERROR,
                    "data" : request.data, 
                    "message" : "Internal server error.",
                    "error": None 
                }
            status = HTTP_500_INTERNAL_SERVER_ERROR
        
        

        return Response(response, status)



class ResetPassword(APIView):
    
    def get(self, request):
        try:
            
            serializer = ResetPasswordLinkSendSerializer(data=request.data)
            if serializer.is_valid():
                response = {
                    "status": HTTP_200_OK,
                    "data" : None,
                    "message" : "Reset password link sent successfully.",
                    "error": None 
                }
                status = HTTP_200_OK
            else:
                response = {
                    "status": HTTP_400_BAD_REQUEST,
                    "data" : serializer.data,
                    "message" : "Invalid data.",
                    "error": serializer.errors 
                }
                status = HTTP_400_BAD_REQUEST
            
        except Exception as e:

            response = {
                    "status": HTTP_500_INTERNAL_SERVER_ERROR,
                    "data" : request.data,
                    "message" : "Internal server error.",
                    "error": None 
                }
            status = HTTP_500_INTERNAL_SERVER_ERROR
        
        
        return Response(response, status)
    
    

    def post(self, request):
        try:
            
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                user  = serializer.save()
                response = {
                    "status": HTTP_200_OK,
                    "data" : None,
                    "message" : "Password reset successful.",
                    "error": None 
                }
                status = HTTP_200_OK
            else:
                response = {
                    "status": HTTP_400_BAD_REQUEST,
                    "data" : serializer.data,
                    "message" : "Invalid data.",
                    "error": serializer.errors 
                }
                status = HTTP_400_BAD_REQUEST
            
        except Exception as e:

            response = {
                    "status": HTTP_500_INTERNAL_SERVER_ERROR,
                    "data" : request.data,
                    "message" : "Internal server error.",
                    "error": None 
                }
            status = HTTP_500_INTERNAL_SERVER_ERROR
        
        

        return Response(response, status)



class UserPrivateProfile(RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = UserPrivateSerializer
    pagination_class = None
    lookup_field = None
    http_method_names = ['get', 'patch']
    
    def get_object(self):
        return self.request.user


    
#list all people/users with country and name filters
class PeopleList(ListAPIView):
    serializer_class = UserPublicSerializer
    queryset = User.objects.all()
    filter_backends = [CountryFilterBackend, NameFilterBackend]



#retrieve a single user profile/details based on uuid
class PeopleRetrieve(RetrieveAPIView):

    serializer_class = PeoplePublicSerializer
    queryset = User.objects.all()
    lookup_field = 'uuid'
    

#list followers of a user
class FollowersList(ListAPIView):
    
    serializer_class = UserPublicSerializer
    lookup_field = 'uuid'

    def get_user(self, uuid):
        try:
            return User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            raise Http404
        
    def get_user_profile(self, user):
        try:
            return UserProfile.objects.prefetch_related('followers').get(user=user)
        except UserProfile.DoesNotExist:
            raise Http404
        
    def get_followers(self, user):
        try:
            profile = self.get_user_profile(user)
            return profile.followers.all()
        except UserProfile.DoesNotExist:
            raise Http404

    def get_queryset(self):
        uuid = self.kwargs.get('uuid')
        user = self.get_user(uuid)
        followers = self.get_followers(user)

        return followers
    

#list following of a user
class FollowingList(ListAPIView):
    
    serializer_class = UserPublicSerializer
    lookup_field = 'uuid'

    def get_user(self, uuid):
        try:
            return User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            raise Http404
        
    def get_user_profile(self, user):
        try:
            return UserProfile.objects.prefetch_related('following').get(user=user)
        except UserProfile.DoesNotExist:
            raise Http404
        
    def get_following(self, user):
        try:
            profile = self.get_user_profile(user)
            return profile.following.all()
        except UserProfile.DoesNotExist:
            raise Http404

    def get_queryset(self):
        uuid = self.kwargs.get('uuid')
        user = self.get_user(uuid)
        following = self.get_following(user)

        return following


#check or add or delete following and followers of user
class FollowUnfollow(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user(self, uuid):
        try:
            return User.objects.get(uuid=uuid)
        except:
            raise Http404

    #check if user is following and followed
    def get(self, request):
        uuid = request.data.get('user', None)
        if uuid:
            user = self.get_user(uuid)
            serializer = FollowUnfollowSerializer(context={"current_user": request.user,})
            
            status = HTTP_200_OK
            response = {
                "status": status,
                "following": serializer.is_following(user),
                "error": None
            }
        else:
            status = HTTP_400_BAD_REQUEST
            response = {
                "status": status,
                "following": None,
                "error": {
                    "user": ["uuid of user is required."]
                }
            }        
        
        return Response(response, status=status)


    #add follower/following
    def post(self, request):
        serializer = FollowUnfollowSerializer(data=request.data, context={"current_user": request.user,})
    
        if serializer.is_valid():
            user = serializer.user
            serializer.save(user=user)
            
            status = HTTP_201_CREATED
            response = {
                "status": status,
                "message": f"{request.data.get('action', 'Action')} successful.",
                "error": None
            }
        else:
            status = HTTP_400_BAD_REQUEST
            response = {
                "status": status,
                "message": "Invalid data.",
                "error": serializer.errors
            }
        
        return Response(response, status=status)
    


#list and create blogs
class BlogListCreate(ListCreateAPIView):
    '''
    1. List the published blogs
    2. Create new blogs with logged in user
    3. Filter blog listing based on blog title, author name, author uuid query params
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [LatestFilterBackend, BlogFilterBackend]

    serializer_class = BlogSerializer
    queryset = Blog.objects.filter(published = True)


    def get_queryset(self):
        if self.request.user.is_authenticated:
            # If user is logged in, show his/her unpublished blogs too
            return Blog.objects.filter(user=self.request.user) | Blog.objects.filter(published=True)
        return self.queryset


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Assign the current user to the blog
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    


#retrieve, update, delete blogs
class BlogRetrieveUpdateDelete(RetrieveUpdateDestroyAPIView):
    '''
    1. Retrieve the blogs with uuid
    2. Update the blog if author is logged in
    3. Delete the blog if author is logged in
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [BlogPermission]

    serializer_class = BlogSerializer
    queryset = Blog.objects.all()
    lookup_field = 'uuid'



#list and create blog comments of a specific blog post
class BlogCommentListCreate(ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = BlogCommentsSerializer
    queryset = BlogComments.objects.all()
    filter_backends = [LatestFilterBackend]

    def get_blog(self, uuid):
        try:
            return Blog.objects.get(uuid=uuid)
        except Blog.DoesNotExist:
            raise Http404

    def get_queryset(self):
        uuid = self.kwargs['uuid']
        return BlogComments.objects.filter(blog__uuid=uuid)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            blog = self.get_blog(uuid=kwargs['uuid'])
            serializer.save(user=request.user, blog=blog)  # Assign the current user to the comment
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
        
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    

#retrieve, update and destroy a blog comments
class BlogCommentRetrieveUpdateDelete(RetrieveUpdateDestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = BlogCommentsSerializer
    queryset = BlogComments.objects.all()
    lookup_field = "uuid"
    http_method_names = ["get", "delete", "patch"]


#list and create reply comments of a specific blog post
class ReplyCommentListCreate(ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ReplyCommentsSerializer

    #func to get the parent_blog_comment
    def get_parent_blog_comment(self, uuid):
        try:
            obj = BlogComments.objects.get(uuid=uuid)
        except BlogComments.DoesNotExist or ValueError or TypeError:
            obj = None

        return obj
    
    #func to get the parent_reply_comment
    def get_parent_reply_comment(self, uuid):
        try:
            obj = ReplyComments.objects.get(uuid=uuid)
        except ReplyComments.DoesNotExist or ValueError or TypeError:
            obj = None

        return obj


    def get_queryset(self):
        uuid = self.kwargs['uuid']
        return ReplyComments.objects.filter(
            Q(parent_reply_comment__uuid=uuid) | Q(parent_blog_comment__uuid=uuid)
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            uuid=kwargs['uuid']
            
            parent_blog_comment = self.get_parent_blog_comment(uuid)
            if parent_blog_comment is None:
                parent_reply_comment = self.get_parent_reply_comment(uuid)
            else:
                parent_reply_comment = None

            if parent_blog_comment is None and parent_reply_comment is None:
                raise Http404
            
            if parent_blog_comment is not None:
                serializer.save(user=request.user, parent_blog_comment=parent_blog_comment)  
            elif parent_reply_comment is not None:
                serializer.save(user=request.user, parent_reply_comment=parent_reply_comment)  

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


#retrieve, update and destroy a reply comments
class ReplyCommentRetrieveUpdateDelete(RetrieveUpdateDestroyAPIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = ReplyCommentsSerializer
    queryset = ReplyComments.objects.all()
    lookup_field = "uuid"
    http_method_names = ["get", "delete", "patch"]



#list and create blog likes of a specific blog post
class BlogLikesListCreate(ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = BlogLikesSerializer
    queryset = BlogLikes.objects.all()
    filter_backends = [LatestFilterBackend]

    def get_blog(self, uuid):
        try:
            return Blog.objects.get(uuid=uuid)
        except Blog.DoesNotExist:
            raise Http404

    def get_queryset(self):
        uuid = self.kwargs['uuid']
        return BlogLikes.objects.filter(blog__uuid=uuid)

    def create(self, request, *args, **kwargs):
        blog = self.get_blog(uuid=kwargs['uuid'])

        serializer = self.get_serializer(data=request.data, context={'request': request, 'user': request.user, 'blog': blog})

        if serializer.is_valid():
            serializer.save(user=request.user, blog=blog)  # Assign the current user to the comment
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
        
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


#retrieve and destroy a blog likes
class BlogLikesRetrieveDelete(RetrieveDestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = BlogLikesSerializer
    queryset = BlogLikes.objects.all()
    lookup_field = "uuid"


#list and create likes of a specific comment
class CommentLikesListCreate(ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentsLikeSerializer


    #func to get the parent_blog_comment
    def get_parent_blog_comment(self, uuid):
        try:
            obj = BlogComments.objects.get(uuid=uuid)
        except BlogComments.DoesNotExist or ValueError or TypeError:
            obj = None

        return obj
    
    #func to get the parent_reply_comment
    def get_parent_reply_comment(self, uuid):
        try:
            obj = ReplyComments.objects.get(uuid=uuid)
        except ReplyComments.DoesNotExist or ValueError or TypeError:
            obj = None

        return obj


    def get_queryset(self):
        uuid = self.kwargs['uuid']
        return LikeComments.objects.filter(
            Q(parent_reply_comment__uuid=uuid) | Q(parent_blog_comment__uuid=uuid)
        )
    
    def create(self, request, *args, **kwargs):

        uuid=kwargs['uuid']
        parent_blog_comment = self.get_parent_blog_comment(uuid)
        if parent_blog_comment is None:
            parent_reply_comment = self.get_parent_reply_comment(uuid)
        else:
            parent_reply_comment = None

        if parent_blog_comment is None and parent_reply_comment is None:
            raise Http404
        
        serializer = self.get_serializer(data=request.data,  context={'request': request, 'user': request.user, 'parent_blog_comment': parent_blog_comment, 'parent_reply_comment': parent_reply_comment})

        if serializer.is_valid():
            if parent_blog_comment is not None:
                serializer.save(user=request.user, parent_blog_comment=parent_blog_comment)  
            elif parent_reply_comment is not None:
                serializer.save(user=request.user, parent_reply_comment=parent_reply_comment)  

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)



#retrieve, update and destroy a like comments
class CommentLikesRetrieveDelete(RetrieveDestroyAPIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = CommentsLikeSerializer
    queryset = LikeComments.objects.all()
    lookup_field = "uuid"


