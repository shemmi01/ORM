from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Comment, Like, Post,STATUS
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    LikeSerializer,
    PostSerializer,
    PostValueSerializer,
)


#how to save data in table using Django .create(), save(), get_or_create(), bulk_create()

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=["POST"])
    def bulk_create(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data, many=True)
        data.is_valid(raise_exception=True)
        if new_data := [
            Category(
                title=row["title"],
                slug=row["slug"],
                description=row["description"],
            )
            for row in data.validate_data
        ]:
            new_data = Category.objects.bulk_create(new_data)
        return Response("Successfully created data.", status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def save_data(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data or None)
        data.is_valid(raise_exception=True)

        title_data = data.validated_data.get("title")
        slug_data = data.validated_data.get("slug")
        description_data = data.validated_data.get("description")

        obj = Category()
        obj.title = title_data
        obj.slug = slug_data
        obj.description = description_data
        obj.save()

        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def get_or_create_data(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data or None)
        data.is_valid(raise_exception=True)

        title_data = data.validated_data.get("title")
        slug_data = data.validated_data.get("slug")

        obj, _ = Category.objects.get_or_create(title=title_data, slug=slug_data)

        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=False, methods=["POST"])
    # def bulk_create(self, request, *args, **kwargs):
    #     data = self.serializer_class(data=request.data, many=True)
    #     data.is_valid(raise_exception=True)

    #     if new_data := [
    #         Category(
    #             title=row["title"],
    #             slug=row["slug"],
    #             description=row["description"],
    #         )
    #         for row in data.validate_data
    #     ]:
    #         new_data=Category.objects.bulk_create(new_data)


    #     # if new_data:[
        #     Category(
        #     title=row["title"],
        #     slug=row["slug"],
        #     description=row["description"]
        # )]


        #return Response("Successfully created data.", status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class LikeViewSet(viewsets.ModelViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer




#How to save data to in many to many field in Django .add(), .set()
class PostViewSet(viewsets.ModelViewSet):

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail = True, methods = ['PATCH'])
    def add_category(self, request, pk,*args, **kwargs):
        categories = request.data.get('ids')
        instance =Post.objects.filter(pk=pk).first()
        # for category in categories:
        #     instance.category.add(category)
        categories = set(categories)
        instance.category.add(*categories)

        serializer = self.serializer_class(instance)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    @action(detail =True,methods = ['PATCH'])
    def set_category(self,request, pk, *args, **kwargs):
        # sourcery skip: avoid-builtin-shadow
        categories_data = request.data.get("ids")

        instance = Post.objects.filter(pk=pk).first()
        # isinstance.category.clear()
        # categories = set(categories)
        # instance.category.add(*categories)
        instance.category.set(categories_data)

        serializer = self.serializer_class(instance)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    @action(detail= True, methods ="POST")
    def update_data(self,request, pk,*args,**kwargs):
        #requesting summery and content from the user to update and pk also for which object to update
        summary_data = request.data.get("summery")
        content_data = request.data.get("content")
        
        #updating data
        Post.objects.filter(pk=pk).update(summery =summary_data,content=content_data)

        return Response({'message':"successfully updated the data."})
    
    @action(detail = False,methods=["POST"])
    def update_or_create_data(self,request,*args,**kwargs):
        category_data = request.data.get("category")
        summary_data = request.data.get("summary")
        title_data = request.data.get("title")
        author = 1
        content_data = request.data.get("content")
        
        obj, _ =Post.objects.update_or_create(title=title_data, defaults={"summery":summary_data,
                                                                  "content":content_data,
                                                                  "author_id":author})
        obj.category.set(category_data)
        return Response({'message':"successfully updated the data."})
    
    @action(detail =False,methods=["POST"])
    def bulk_update_data(self,request,*args,**kwargs):
        ids = request.data.get("ids")
        queryset = Post.objects.filter(id__in = ids)

        for obj in queryset:
            obj.status = STATUS.PUBLISH.value
        
        Post.objects.bulk_update(queryset,["status"])
        return Response({'message':"successfully updated the data."})
    
#How to retrive /filter data:
    @action(detail = False, methods = ["GET"])
    def get_all(self,request,*args,**kwargs):
        queryset =Post.objects.all()
        serializer= self.serializer_class(queryset,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=["GET"])
    def get_one(self,request,*args,**kwargs):
        slug =request.GET.get("slug")

        try:
            obj=Post.objects.get(slug=slug)
        except Post.MultipleObjectsReturned:
            return Response({"message":"Multiple objs found" },status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({"message":"Object is not found"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(obj)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=["GET"])
    def get_filter(self,request,*args,**kwargs):
        # sourcery skip: avoid-builtin-shadow
        id = request.GET.get("id")
        queryset = Post.objects.filter(id=id) 

        #we can use .first() for get one obj and .last() , and queryset wiil become obj many =true is not required
        # obj= Post.objects.filter(id=id).first()
        # serializer = self.serializer_class(queryset)

        serializer = self.serializer_class(queryset,many =True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=["GET"])
    def exclude_filter(self,request,*args,**kwargs):
        # sourcery skip: avoid-builtin-shadow, avoid-builtin-shadow .filter(status=1)
        id = request.GET.get("id")
        queryset=Post.objects.exclude(id=id)
        serializer = self.serializer_class(queryset,many =True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    @action(detail=False,methods=["GET"])
    def limit_data(self,request,*args,**kwargs):
        queryset=Post.objects.all()[1:2]

        serializer = self.serializer_class(queryset,many =True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=["GET"])
    def lookup_filter(self,request,*args,**kwargs):
        ids = request.GET.get("ids")
        ids=ids.split(",") #converting into list,
        queryset=Post.objects.filter(id__in=ids)

        serializer = self.serializer_class(queryset,many =True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["POST"])
    def bulk_create(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data, many=True)
        data.is_valid(raise_exception=True)

        if new_data := [
            Post(
                summary= row["summary"],
                content=row["content"],
                status=row["status"],
                image=row["image"],
                author=row["author"],
                category=row["category"],
                title=row["title"],
                slug=row["slug"],
                description=row["description"],
            )
            for row in data.validate_data
        ]:
            new_data=Post.objects.bulk_create(new_data)

        return Response("Successfully created data.", status=status.HTTP_201_CREATED)

#How to retrive/filter data by using order by ,distinct, deep filter
    @action(detail=False,methods=["GET"])
    def order_by_data(self,request,*args,**kwargs):
        queryset=Post.objects.all().order_by("title") #if i give like this ascending oder if i want descending just give '-' to "title"
        serializer =self.serializer_class(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=["GET"])
    def destinct_data(self,request,*args,**kwargs):
        queryset = (
            Post.objects.all().filter(category__id__in=[1,2]).distinct()
        )
        serializer =self.serializer_class(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=False,methods=["GET"])
    def deep_filter_data(self,request,*args,**kwargs):
        queryset =Post.objects.all().filter(category__id=0).distinct()

        serializer =self.serializer_class(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    #How to retrive/filter data  values(), value_list()
    @action(detail=True, methods=["GET"])
    def get_values(self,request,pk,*args,**kwargs):
        queryset=Post.objects.filter(pk=pk).values('id',"title","slug")
        serializer= PostValueSerializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["GET"])
    def get_values(self,request,pk,*args,**kwargs):
        queryset=Post.objects.filter(pk=pk).values_list('id',"title","slug")
        return Response(queryset,status=status.HTTP_200_OK)
    










    




    

        
    









        

    

    