from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsVerified(BasePermission):
    '''
    permission to allow only the verified users to access the obj
    '''

    def has_object_permission(self, request, view, obj):
        
        return obj.user.is_verified
    

class IsOwnerOrReadOnly(BasePermission):
    '''
    permission to allow only the owner of the obj to delete/update/edit it
    '''

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True

        if obj.user == request.user:
            return True
        
        return False
    

class IsOwner(BasePermission):
    '''
    permission to allow only the owner of the obj to view/delete/update/edit it
    '''

    def has_object_permission(self, request, view, obj):

        if obj.user == request.user:
            return True
        
        return False



class BlogPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # If the user is not logged in, they can only view published blogs.
        if not request.user.is_authenticated:
            print(obj.published)
            return obj.published

        # If the user is logged in and the blog's author is the current user,
        # they can view the blog even if it's not published.
        return obj.user == request.user or obj.published

