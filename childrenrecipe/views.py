#!/usr/bin/env Python
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import datetime
from django.utils.timezone import UTC
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from childrenrecipe.serializers import *
from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from rest_framework.response import Response
from rest_framework.permissions import(
	AllowAny,
	IsAuthenticated
)
from rest_framework.decorators import(
	api_view,
	permission_classes,
	parser_classes,
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.core.handlers.wsgi import WSGIRequest
# Create your views here.
class JSONResponse(HttpResponse):
        """
        An HttpResponse that renders its content into JSON.
        """
	def __init__(self, data, **kwargs):
        	content = JSONRenderer().render(data)
        	kwargs['content_type'] = 'application/json'
        	super(JSONResponse, self).__init__(content, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
        queryset = Group.objects.all()
        serializer_class = GroupSerializer

class APIRootView(APIView):
    def get(self, request):
        year = now().year
        data = {
            'year-summary-url': reverse('year-summary', args=[year], request=request)
        }
        return Response(data)

class RecipeViewSet(viewsets.ModelViewSet):
	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer
	ordering =('-create_time')


class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer

class MaterialViewSet(viewsets.ModelViewSet):
	queryset = Material.objects.all()
	serializer_class = MaterialSerializer

class ProcedureViewSet(viewsets.ModelViewSet):
	queryset = Procedure.objects.all()
	serializer_class = ProcedureSerializer

class TagViewSet(viewsets.ModelViewSet):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def tags(request):
	data = []
	categorys = {}
	tags = Tag.objects.exclude(category__is_tag= 1 )
	if tags:
                for tag in tags:
                        tag_id = tag.id
                        tag_name = tag.name
                        category_name = tag.category.name
                        category_seq = tag.category.seq
                        categroy = None
                        if category_name in categorys:
                                category = categorys[category_name]
                        else:
                                category = {'seq': category_seq, 'category': category_name, 'tags': []}
                                categorys[category_name] = category
                                data.append(category)
                        category['tags'].append({
                                'id': tag_id,
                                'tag': tag_name,                                                            
                        })

                if len(data)>1:
                        for item in range(0, len(data)-1):
                                #category_seq = data[item].get('seq')
                                min = item
                                for item2 in range(item+1, len(data)):
                                        if data[item2].get('seq') < data[min].get('seq'):
                                                min = item2
                                tmp = data[item]
                                data[item] = data[min]
                                data[min] = tmp
                        return Response(data, status=status.HTTP_200_OK)
                else:
                        return Response(data, status=status.HTTP_200_OK)                       
        else:
                return Response(data, status=status.HTTP_200_OK) 

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def recipe(request):
	import time
	data = []
        tags = {}
        ages = []
        search = None
        create_time = None
	tag = None
        search = request.data.get('search',None)
	print search
        ages = request.data.get('age',None)
        create_time = request.data.get('create_time', None)
	tag = request.data.get('tag_id',None)
	print tag
        print ages
	if ages is None and search is None and tag is None:
                recipes = Recipe.objects.all().order_by('tag__seq','create_time')
        elif search is None:
		recipes = Recipe.objects.all().order_by('tag__seq','create_time')
		for recipe in recipes:
			if ages is None:
				recipes = Recipe.objects.filter(tag__id__in = tag).order_by('tag__seq','create_time')[:10]
				for recipe in recipes:
                        		if create_time is None:
                                		recipes = Recipe.objects.filter(tag__id = tag).order_by('tag__seq','create_time')[:10]
					else:
						createtime = time.localtime(int(create_time))
                                		s = time.strftime('%Y-%m-%d %H:%M:%S',createtime)
                                		recipes = Recipe.objects.filter(Q(tag__id = tag) & Q(create_time__gt = s)).order_by('tag__seq','create_time')[:10]

                        elif tag is None:
				recipes = Recipe.objects.filter(tag__id__in = ages).order_by('tag__seq','create_time')[:10]
				for recipe in recipes:
					if create_time is None:
						recipes = Recipe.objects.filter(tag__id__in = ages).order_by('tag__seq','create_time')[:10]
					else:
						createtime = time.localtime(int(create_time))
                                                s = time.strftime('%Y-%m-%d %H:%M:%S',createtime)
						recipes = Recipe.objects.filter(Q(tag__id__in = ages) & Q(create_time__gt = s)).order_by('tag__seq','create_time')[:10]

			else:	
                                recipes = Recipe.objects.filter(tag__id = tag).filter(tag__id__in = ages).order_by('tag__seq','create_time')[:10]
				for recipe in recipes:
					if create_time is None:
						recipes = Recipe.objects.filter(tag__id = tag).filter(tag__id__in = ages).order_by('tag__seq','create_time')[:10]
					else:
                				createtime = time.localtime(int(create_time))
                				s = time.strftime('%Y-%m-%d %H:%M:%S',createtime)
                				recipes = Recipe.objects.filter(tag__id__in = tag).filter(Q(tag__id__in = ages) & Q(create_time__gt = s)).order_by('tag__seq','create_time')[:10]

        else:  		 
                recipes = Recipe.objects.filter(Q(name__contains = search)|Q(tag__name = search)).order_by('tag__seq','create_time')
		for recipe in recipes:
			if tag is None:
				recipes = Recipe.objects.filter(Q(name__contains = search)|Q(tag__name = search)).order_by('tag__seq','create_time')
			else:
				recipes = Recipe.objects.filter(tag__id__in = tag).filter(Q(name__contains = search)|Q(tag__name = search)).order_by('tag__seq','create_time')
                		for recipe in recipes:
                        		if create_time is None:
						recipes = Recipe.objects.filter(tag__id__in = tag).filter(Q(name__contains = search)|Q(tag__name = search)).order_by('tag__seq','create_time')
                        		else:
                                		createtime = time.localtime(int(create_time))
                                		s = time.strftime('%Y-%m-%d %H:%M:%S',createtime)
                                		recipes = Recipe.objects.filter(tag__id__in = tag).filter(Q(name = search)|Q(tag__name = search) & Q(create_time__gt = s)).order_by('tag__seq','create_time')[:10]
				

#	pdb.set_trace()
        epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)
        for recipe in recipes:
                recipe_id = recipe.id
                recipe_create_time = recipe.create_time
                recipe_name = recipe.name
                recipe_user = recipe.user
                recipe_exihibitpic = recipe.exihibitpic
		recipe_introduce = recipe.introduce
                recipe_tips = recipe.tips

                td = recipe_create_time - epoch
                timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600))

                tag_name = recipe.tag.filter(category__is_tag= 1 )[0].name
		tag_id = recipe.tag.filter(category__is_tag = 1 )[0].id  
                tag = None
                if tag_name in tags:
                        tag = tags[tag_name]
                else:
                        tag = {'tag':tag_name,'tag_id':tag_id, 'recipes':[]}
                        tags[tag_name] = tag
                        data.append(tag)
                tag['recipes'].append({
                        'id':recipe_id,
                        'url':"http://"+request.META['HTTP_HOST']+'/'+'api'+'/'+'recipes'+'/'+str(recipe_id),
                        'create_time':timestamp_recipe_createtime,
                        'recipe':recipe_name,
                        'user':recipe_user,
                        'tips':recipe_tips,
                        'exihibitpic':"http://"+request.META['HTTP_HOST']+recipe_exihibitpic.url,
                        'introduce':recipe_introduce,
                        'tag': [{"category_name": x.category.name, 'name': x.name}for x in recipe.tag.filter(category__is_tag = 4)]

                })
		
	return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def tagshow(request):
	data = []
        categorys = {}
        tags = Tag.objects.filter(category__is_tag=1)
        for tag in tags:
                tag_id = tag.id
                tag_name = tag.name
                category_name = tag.category.name
                categroy = None
                if category_name in categorys:
                        category = categorys[category_name]
                else:
                        category = {'category': category_name, 'tags': []}
                        categorys[category_name] = category
                        data.append(category)
                category['tags'].append({
                        'id': tag_id,
                        'tag': tag_name
                })
        return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def recommend(request):
        #import pdb
        #pdb.set_trace()

        now = datetime.datetime.now()
        epoch = datetime.datetime(1970, 1, 1)+datetime.timedelta(hours=8)

	if Recommend.objects.all().filter(pubdate__lte=now): 
                recommend = Recommend.objects.all().filter(pubdate__lte=now).order_by('-pubdate').first()
                
                recommend_image = recommend.image.url
                recommend_pubdate = recommend.pubdate
                recommend_create_time = recommend.create_time
                recommend_recipe_id = recommend.recipe.id
                recommend_recipe_create_time = recommend.recipe.create_time
                recommend_recipe_name = recommend.recipe.name
                recommend_recipe_user = recommend.recipe.user
                recommend_recipe_introduce = recommend.recipe.introduce

		td = recommend_recipe_create_time - epoch
                td1 = recommend_create_time - epoch
                td2 = recommend_pubdate - epoch
		timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)
                timestamp_createtime = int(td1.microseconds + (td1.seconds + td1.days * 24 * 3600) * 10**6)
                timestamp_pubdate = int(td2.microseconds + (td2.seconds + td2.days * 24 * 3600) * 10**6)
                
                recommend = {'recommend_recipe': 'Today\'s Specials', 'create_time': timestamp_createtime,
                        'pubdate': timestamp_pubdate, 'image': "http://"+request.META['HTTP_HOST']+recommend_image, 'recipe': {}}
                
                recommend['recipe'] = {
                        'id': recommend_recipe_id,
                        'create_time': timestamp_recipe_createtime,
                        'name': recommend_recipe_name,
                        'user': recommend_recipe_user,
                        'introduce': recommend_recipe_introduce,
			'url': "http://"+request.META['HTTP_HOST']+'/'+'api'+'/'+'recipes'+'/'+str(recommend_recipe_id)
                }
     
                return Response(recommend, status=status.HTTP_200_OK)
        
        else:
                recommend = {}
                return Response(recommend, status=status.HTTP_200_OK)
