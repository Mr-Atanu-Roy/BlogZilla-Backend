from typing import Any, Dict
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from backend.models import User, UserProfile, Tokens, Blog, BlogComments, BlogLikes, ReplyComments, LikeComments
from backend.utils import TokenGenerator, EmailSender

from .utils import str_to_list, list_to_str, is_valid_sequence


#serializer for custom claims: access token -> uuid, first_name, last_name
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['uuid'] = str(user.uuid)
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        
        password = attrs.get('password', None)
        email = attrs.get('email', None)
        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'email': 'Account with this email does not exists.'
                })

            if not user.is_verified:
                raise serializers.ValidationError({
                    'email': 'Email is not verified.'
                })
        
        
        return data



class UserSignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        '''
        Overriding create method since password is not hashed by default 
        '''
        user = User.objects.create_user(
            email=validated_data.get("email"), 
            password = validated_data.get("password")
        )
        user.save()

        return user
    

class EmailVerifyLinkSendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data.get('email', None)

        if not email:
            raise serializers.ValidationError({
                'email': 'Email address is required.'
            })
        
        try:
            user = User.objects.get(email=email)

            if not user.is_verified:
                EmailSender(user.email).email_verify_link_send(user, user.get_full_name())
                return super().validate(data)
            
            else:
                raise serializers.ValidationError({
                    'email': 'Account with this email is already verified.'
                })

        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        
        raise serializers.ValidationError({
            'email': 'Account with this email does not exists.'
        })


class EmailVerifySerializer(serializers.Serializer):

    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, data):
        uidb64 = data.get('uidb64', None)
        token = data.get('token', None)

        if not uidb64:
            raise serializers.ValidationError({
                'uidb64': 'uidb64 is required.'
            })
  
        if not token:
            raise serializers.ValidationError({
                'token': 'token is required.'
            })
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            raise serializers.ValidationError({
                "token": "Invalid link."
            })
        
        if user is not None and TokenGenerator().check_token(user, token):
            if user.is_verified:
                raise serializers.ValidationError({
                    'user': 'User is already verified'
                })
            else:
                user.is_verified = True
                user.save()

                #sending email to notify user
                EmailSender(user.email).email_verify_notify()

                return super().validate(data)



        
class ResetPasswordLinkSendSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data.get('email', None)

        if not email:
            raise serializers.ValidationError({
                'email': 'Email address is required.'
            })
        
        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                token = Tokens(user=user)
                token.save()
                return super().validate(data)
            
            else:
                raise serializers.ValidationError({
                    'email': 'Account with this email is not verified.'
                })

        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        
        raise serializers.ValidationError({
            'email': 'Account with this email does not exists.'
        })



class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, data):
        uidb64 = data.get('uidb64', None)
        token = data.get('token', None)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            try:
                db_token = Tokens.objects.get(token=token, user=user, is_expired=False)
                
                ten_minutes_ago = timezone.now() - timezone.timedelta(minutes=10)
                if db_token.created_at < ten_minutes_ago:
                    raise serializers.ValidationError({
                        'token': 'link has expired.'
                    })
            
            except(TypeError, ValueError, OverflowError, Tokens.DoesNotExist):
                db_token = None
                raise serializers.ValidationError({
                    'token': 'Invalid link.'
                })
            
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            raise serializers.ValidationError({
                'uidb64': 'Invalid link.'
            })
        
        
        return super().validate(data)
    

    def create(self, validated_data):
        password = validated_data.get('password', None)
        uidb64 = validated_data.get('uidb64', None)
        token = validated_data.get('token', None)

        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        db_token = Tokens.objects.get(token=token, user=user, is_expired=False)
        db_token.is_expired = True
        db_token.save()

        user.set_password(password)
        user.save()

        #sending email to notify user
        EmailSender(user.email).reset_password_notify()


        return user
        

#serializer for User model for public profile
class UserPublicSerializer(serializers.ModelSerializer):
    '''
    user for profile/user cards in following and followers 
    '''

    blogs_published = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['uuid', 'first_name', 'last_name', 'profile_pic', 'profession', 'country', 'blogs_published']
        
    
    def get_blogs_published(self, obj):
        return Blog.objects.filter(user=obj).count()


#serializer for UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    '''
    used for nesting in users
    '''

    interests_parsed = serializers.SerializerMethodField('get_interests_parsed')
    interests = serializers.ListField(child=serializers.CharField(max_length=350), write_only=True)
        
    followers = serializers.SerializerMethodField(read_only=True)
    following = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'website', 'interests', 'interests_parsed', 'followers', 'following']
        read_only_fields = ['interests_parsed']

    def get_interests_parsed(self, obj):
        return str_to_list(obj.interests)
    
    def get_followers(self, obj):
            return obj.followers.all().count()
    

    def get_following(self, obj):
        return obj.following.all().count()

        

#serializer for User model for private profile
class UserPrivateSerializer(serializers.ModelSerializer):
    '''
    mainly used for user/me/ endpoint, to get the user's profile when user requests his profile
    '''

    user_profile = UserProfileSerializer()
    blogs_published_no = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['uuid', 'email', 'phone', 'is_verified', 'date_joined', 'first_name', 'last_name', 'profile_pic', 'profession', 'country', 'user_profile', 'blogs_published_no']
        read_only_fields = ['uuid', 'email', 'is_verified', 'date_joined']


    def get_blogs_published_no(self, obj):
        return Blog.objects.filter(user=obj).count()


    def validate_phone(self, phone):
        if phone:
            print(len(phone))

            if not phone.isdigit():
                raise serializers.ValidationError('Phone number should be numeric.')

            if len(phone) != 10:
                raise serializers.ValidationError('Phone number should be 10 digits.')
            
        return phone   


    def create(self, validated_data):
        return None
    
    def update(self, instance, validated_data):
        print(validated_data)
        user_profile_data = validated_data.pop('user_profile', None)
        user_profile = instance.user_profile

        #updating the user instance
        if validated_data is not None:
            instance.phone = validated_data.get('phone', instance.phone)
            instance.first_name = validated_data.get('first_name', instance.first_name)
            instance.last_name = validated_data.get('last_name', instance.last_name)
            instance.profession = validated_data.get('profession', instance.profession)
            instance.country = validated_data.get('country', instance.country)
            if 'profile_pic' in validated_data:
                instance.profile_pic = validated_data.get('profile_pic')
            instance.save()

        #updating the user_profile instance
        if user_profile_data is not None:
            user_profile_data.pop('followers', None)
            user_profile_data.pop('following', None)

            user_profile.bio = user_profile_data.get('bio', user_profile.bio)
            user_profile.website = user_profile_data.get('website', user_profile.website)
            interests = user_profile_data.get('interests', None)
            if interests is not None:
                interests = list_to_str(interests)
                user_profile.interests = interests
            user_profile.save()

        return instance



#serializer for full People Profile for public view
class PeoplePublicSerializer(serializers.ModelSerializer):
    '''
    Mainly used for public view of people profiles
    '''

    user_profile = UserProfileSerializer(read_only=True)
    blogs_published_no = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['uuid', 'first_name', 'last_name', 'profile_pic', 'profession', 'country', 'blogs_published_no', 'user_profile']


    def get_blogs_published_no(self, obj):
        return Blog.objects.filter(user=obj).count()

    def update(self, instance, validated_data):
        return None
    
    def create(self, validated_data):
        return None


#serializer for blog model --> retrieve, update, delete. Shows detail view of blog
class BlogDetailSerializer(serializers.ModelSerializer):

    user = UserPublicSerializer(read_only=True)
    tags_parsed = serializers.SerializerMethodField('get_tags_parsed')
    tags = serializers.ListField(child=serializers.CharField(max_length=350), write_only=True, required=True)

    class Meta:
        model = Blog
        fields = ["uuid", "user", "created_at", "title", "slug", "header_img", "content", "tags", "tags_parsed", "likes_no", "comments_no", "published"]
        read_only_fields = ["uuid", "user", "created_at", "slug", "likes_no", "comments_no", "content_summery", "tags_parsed"]

    def tags_validate(self, tags):
        if tags and not is_valid_sequence(tags):
            raise serializers.ValidationError({
                'tags': 'Tags should be list of strings.'
            })
        
        return tags

    
    def update(self, instance, validated_data):
        if validated_data.get("tags"):
            validated_data["tags"] = list_to_str(validated_data.get("tags"))
        return super().update(instance, validated_data)
        
    
    def get_tags_parsed(self, obj):
        return str_to_list(obj.tags)



#serializer for blog model --> list and create. Shows minimal view of blog
class BlogListCreateSerializer(serializers.ModelSerializer):

    user = UserPublicSerializer(read_only=True)
    truncated_content = serializers.SerializerMethodField('get_truncated_content')
    tags_parsed = serializers.SerializerMethodField('get_tags_parsed')
    tags = serializers.ListField(child=serializers.CharField(max_length=350), write_only=True, required=True)

    
    class Meta:
        model = Blog
        fields = ["uuid", "user", "created_at", "title", "slug", "header_img", "content", "truncated_content", "tags", "tags_parsed", "likes_no", "comments_no", "published"]
        read_only_fields = ["uuid", "user", "created_at", "slug", "likes_no", "comments_no", "content_summery", "tags_parsed"]
        extra_kwargs = {
            'content': {'write_only': True},
        }

    def tags_validate(self, tags):
        if tags and not is_valid_sequence(tags):
            raise serializers.ValidationError({
                'tags': 'Tags should be list of strings.'
            })
        
        return tags
    
    def create(self, validated_data):
        if validated_data.get("tags"):
            validated_data["tags"] = list_to_str(validated_data.get("tags"))
        return super().create(validated_data)
    
    def get_truncated_content(self, obj):
        content_words = obj.content.split()
        truncated_content = ' '.join(content_words[:25])
        return f"{truncated_content}...."
    
    def get_tags_parsed(self, obj):
        return str_to_list(obj.tags)



#serializer for follow/unfollow
class FollowUnfollowSerializer(serializers.Serializer):

    action = serializers.CharField(required=True)
    user = serializers.UUIDField(required=True)

    
    def is_following(self, user):
        current_user = self.context["current_user"]
        return current_user.user_profile.following.filter(id=user.id).exists()

    
    def validate(self, data):
        action = data.get('action', None)
        user = data.get('user', None)

        if action:
            if action not in ['follow', 'unfollow']:
                raise serializers.ValidationError({
                    'action': 'action should be follow or unfollow.'
                })
        else:
            raise serializers.ValidationError({
                'action': 'action is required.'
            })
        
  
        if not user:
            raise serializers.ValidationError({
                'user': 'uuid of user is required.'
            })
        
        try:
            user = User.objects.get(uuid=user)

            if user == self.context["current_user"]:
                raise serializers.ValidationError({
                    'user': "user can't be itself."
                })
            
            status = self.is_following(user)
            if action == "follow" and status:
                raise serializers.ValidationError({
                    'user': "user is already being followed."
                })
            
            if action == "unfollow" and not status:
                raise serializers.ValidationError({
                    'user': "user is already being unfollowed."
                })

            self.user = user
            return super().validate(data)
        
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({
                'user': 'user is invalid.'
            })
        
    
        
    def create(self, validated_data):
        action = validated_data.get('action')
        user = validated_data.get('user')
        current_user = self.context["current_user"]

        if action == 'follow':
            current_user.user_profile.following.add(user)
            user.user_profile.followers.add(current_user)

        if action == 'unfollow':
            current_user.user_profile.following.remove(user)
            user.user_profile.followers.remove(current_user)

        return validated_data



#serializer for reply comment model --> list, create, update, delete
class ReplyCommentsSerializer(serializers.ModelSerializer):


    user = UserPublicSerializer(read_only=True)

    reply_comments = serializers.SerializerMethodField()

    def get_reply_comments(self, obj):
        children = ReplyComments.objects.filter(parent_reply_comment=obj)
        return children.count()

    class Meta:
        model = ReplyComments
        fields = ["uuid", "user", "comment", "likes_no", "comments_no", "created_at", "reply_comments"]
        read_only_fields = ["uuid", "user", "likes_no", "comments_no", "created_at"]

        
    def create(self, validated_data):
        if validated_data:
            comment = validated_data.get('comment')
            parent_blog_comment = validated_data.get('parent_blog_comment')
            parent_reply_comment = validated_data.get('parent_reply_comment')
            
            reply = ReplyComments(user=validated_data.get("user"), comment=comment)
            if parent_blog_comment is not None:
                reply.parent_blog_comment = parent_blog_comment
            else:
                reply.parent_reply_comment = parent_reply_comment
            reply.save()

            return reply
        
            
#serializer for blog comments
class BlogCommentsSerializer(serializers.ModelSerializer):

    user = UserPublicSerializer(read_only=True)
    
    comments_no = serializers.SerializerMethodField()
    likes_no = serializers.SerializerMethodField()

    def get_comments_no(self, obj):
        return obj.reply_comments.count()
    
    def get_likes_no(self, obj):
        return obj.like_blog_comments.count()

    class Meta:
        model = BlogComments
        fields = ["uuid", "user", "comment", "likes_no", "comments_no", "created_at"]
        read_only_fields = ["uuid", "user", "likes_no", "comments_no", "created_at"]



#serializer for blog likes
class BlogLikesSerializer(serializers.ModelSerializer):

    user = UserPublicSerializer(read_only=True)


    class Meta:
        model = BlogLikes
        fields = ["uuid", "user", "created_at"]
        read_only_fields = ["uuid", "user", "created_at"]



    def validate(self, data):
        
        user = self.context['user']
        blog = self.context['blog']

        #raise exception if user has already liked the blog
        if BlogLikes.objects.filter(user=user, blog=blog).exists():
            raise serializers.ValidationError({
                'user': 'user has already liked this blog.'
            })


        return super().validate(data)



#serializer for comment likes
class CommentsLikeSerializer(serializers.ModelSerializer):

    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = LikeComments
        fields = ["uuid", "user", "created_at"]
        read_only_fields = ["uuid", "user", "created_at"]


    
    def validate(self, data):
        
        user = self.context['user']
        parent_blog_comment = self.context['parent_blog_comment']
        parent_reply_comment = self.context['parent_reply_comment']

        #raise exception if user has already liked the blog
        if parent_blog_comment:
            if LikeComments.objects.filter(user=user, parent_blog_comment=parent_blog_comment).exists():
                raise serializers.ValidationError({
                    'user': 'user has already liked this comment.'
                })
        elif parent_reply_comment:
            if LikeComments.objects.filter(user=user, parent_reply_comment=parent_reply_comment).exists():
                raise serializers.ValidationError({
                    'user': 'user has already liked this comment.'
                })


        return super().validate(data)

        
    def create(self, validated_data):
        if validated_data:
            parent_blog_comment = validated_data.get('parent_blog_comment')
            parent_reply_comment = validated_data.get('parent_reply_comment')
            
            like = LikeComments(user=validated_data.get("user"))
            if parent_blog_comment is not None:
                like.parent_blog_comment = parent_blog_comment
            else:
                like.parent_reply_comment = parent_reply_comment
            like.save()

            return like

