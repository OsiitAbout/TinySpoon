#!/usr/bin/env Python
# coding=utf-8
import time
from datetime import datetime

from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
)

from .serializers import *
from .constent import EPOCH


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
        year = datetime.now().year
        data = {
            'year-summary-url': reverse('year-summary', args=[year], request=request)
        }
        return Response(data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    ordering = ('-create_time')


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
    tags = Tag.objects.exclude(category__is_tag=1)
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

        if len(data) > 1:
            for item in range(0, len(data) - 1):
                # category_seq = data[item].get('seq')
                min = item
                for item2 in range(item + 1, len(data)):
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


class RecipeResponseItem:
    def __init__(self, recipe, host, create_time,
                 tags):
        self.recipe = recipe
        self.host = host
        self.create_time = create_time
        self.tag = tags

    def to_data(self):
        recipe = self.recipe
        _id = recipe.id
        recipe_name = recipe.name
        user = recipe.user
        tips = recipe.tips
        introduce = recipe.introduce
        host = self.host
        url = 'http://%s/api/recipes/%d' % (host, _id)
        exihibitpic_url = recipe.exihibitpic
        exihibitpic = 'http://%s/%s' % (host, exihibitpic_url)
        exihibitpic = exihibitpic.decode('utf-8')
        data = {
            'id': _id,
            'url': url,
            'create_time': self.create_time,
            'recipe': recipe_name,
            'user': user,
            'tips': tips,
            'exihibitpic': exihibitpic,
            'introduce': introduce,
            'tag': self.tag
        }
        return data


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def recipe(request):
    data = []
    ta = {}
    search = request.data.get('search', None)
    create_time = request.data.get('create_time', None)
    tags_ = request.data.get('tag_id', None)
    host = request.META['HTTP_HOST']

    if tags_ is None:
        query = Recipe.objects
    else:
        query = Recipe.objects
        for tag_id in tags_:
            query = query.filter(tag=tag_id)  # tag and query

    if search:
        query = query.filter(name__contains=search)
    if create_time:
        createtime = time.localtime(int(create_time))
        s = time.strftime('%Y-%m-%d %H:%M:%S', createtime)
        query = query.filter(create_time__gt=s)
    recipes = query.order_by('create_time')[:10]

    for recipe in recipes:
        recipe_create_time = recipe.create_time

        td = recipe_create_time - EPOCH
        timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600))

        query_tag = recipe.tag.filter(category__is_tag=1)
        tag_first = query_tag[0]

        tag_name = tag_first.name
        tag_id = tag_first.id
        tag_seq = tag_first.seq

        if tag_name in ta:
            tag = ta[tag_name]
        else:
            tag = {'tag': tag_name, 'tag_id': tag_id, 'tag_seq': tag_seq, 'recipes': []}
            ta[tag_name] = tag
            data.append(tag)

        _tags = [{"category_name": x.category.name, 'name': x.name}
                    for x in recipe.tag.filter(category__is_tag=4)]
        recipe_item = RecipeResponseItem(recipe=recipe,
                                         host=host,
                                         create_time=timestamp_recipe_createtime,
                                         tags=_tags)
        tag['recipes'].append(recipe_item.to_data())
    data.sort(key=lambda x: x['tag_seq'])
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reci(request):
    import pdb
    search = request.data.get('search', None)
    create_time = request.data.get('create_time', None)
    tags = request.data.get('tag_id', None)
    print tags

    def get_tag(tags=None):
        pdb.set_trace()
        if tags is not None:
            x = Tag.objects.filter(id__in=tags_)
            stage = [x.id for x in age]
            print stage
            print tags
            pdb.set_trace()
        else:
            return Tag.objects.none()
        print stage

    def get_recipe(tags_=None, serach=None, create_time=None):

        pass

    pdb.set_trace()

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def tagshow(request):
    data = []
    categorys = {}
    tags = Tag.objects.filter(category__is_tag=1).order_by('seq')
    for tag in tags:
        tag_id = tag.id
        tag_name = tag.name
        tag_seq = tag.seq
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
            'tag': tag_name,
            'is_tag': tag_seq
        })
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def recommend(request):
    # import pdb
    # pdb.set_trace()

    now = datetime.datetime.now()
    epoch = datetime.datetime(1970, 1, 1) + datetime.timedelta(hours=8)

    if Recommend.objects.all().filter(pubdate__lte=now):
        recommend = Recommend.objects.all().filter(pubdate__lte=now).order_by('-pubdate').first()

        if recommend.name:
            recommend_name = recommend.name
        else:
            recommend_name = recommend.recipe.name

        if recommend.introduce:
            recommend_introduce = recommend.introduce
        else:
            recommend_introduce = recommend.recipe.introduce

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
        timestamp_recipe_createtime = int(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6)
        timestamp_createtime = int(td1.microseconds + (td1.seconds + td1.days * 24 * 3600) * 10 ** 6)
        timestamp_pubdate = int(td2.microseconds + (td2.seconds + td2.days * 24 * 3600) * 10 ** 6)

        recommend = {'recommend_recipe': 'Today\'s Specials', 'create_time': timestamp_createtime,
                     'pubdate': timestamp_pubdate, 'image': request.build_absolute_uri(recommend_image),
                     'name': recommend_name, 'introduce': recommend_introduce, 'recipe': {}}

        recommend['recipe'] = {
            'id': recommend_recipe_id,
            'create_time': timestamp_recipe_createtime,
            'name': recommend_recipe_name,
            'user': recommend_recipe_user,
            'introduce': recommend_recipe_introduce,
            'url': "http://" + request.META['HTTP_HOST'] + '/' + 'api' + '/' + 'recipes' + '/' + str(
                recommend_recipe_id)
        }
        return Response(recommend, status=status.HTTP_200_OK)

    else:
        recommend = {}
        return Response(recommend, status=status.HTTP_200_OK)
