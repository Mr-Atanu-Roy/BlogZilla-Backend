from rest_framework.filters import BaseFilterBackend
from .utils import str_to_list
from django.db.models import Q
from functools import reduce

#filter backend to filter authors by country
class CountryFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_param = request.query_params.get('country')
        if filter_param:
            return queryset.filter(country__icontains=filter_param)
        
        return queryset
    

#filter backend to filter authors by their name: first_name, last_name
class NameFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_param = request.query_params.get('name')
        if filter_param:
            return queryset.filter(first_name__icontains=filter_param) | queryset.filter(last_name__icontains=filter_param)
        
        return queryset



#filter backend to filter blogs by author's name: first_name, last_name and uuid. Filter blog by its tags, title. Order blogs by likes_no, comments_no if popular, rated is true respectively
class BlogFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_param_name = request.query_params.get('name')
        filter_param_title = request.query_params.get('title')
        filter_param_tags = request.query_params.get('tags')
        filter_param_popular = request.query_params.get('popular')
        filter_param_rated = request.query_params.get('rated')

        filter_param_uuid = request.query_params.get('uuid', None)
        if filter_param_uuid is None:
            filter_param_uuid = request.query_params.get('user', None)

        if filter_param_uuid:
            queryset = queryset.filter(user__uuid=filter_param_uuid)
        
        if filter_param_name:
            queryset = queryset.filter(user__first_name__icontains=filter_param_name) | queryset.filter(user__last_name__icontains=filter_param_name)
        
        if filter_param_title:
            return queryset.filter(title__icontains=filter_param_title) | queryset.filter(slug__icontains=filter_param_title)
        
        if filter_param_tags:
            tags = str_to_list(filter_param_tags)
            tag_filters = [Q(tags__icontains=tag) for tag in tags]
            return queryset.filter(reduce(Q.__or__, tag_filters))
        
        if filter_param_popular=="true":
            return queryset.order_by('-likes_no')
        
        if filter_param_rated=="true":
            return queryset.order_by('-comments_no')
        
        return queryset
    

#order queryset by created_at field
class LatestFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_param = request.query_params.get('latest')

        if filter_param=="true":
            queryset = queryset.order_by('-created_at')
        
        
        return queryset


    


    