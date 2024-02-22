from django.urls import path
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from projects.schema import schema  
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
