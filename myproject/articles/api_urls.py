from django.urls import path
from . import api_views

urlpatterns = [
    path('article/add/<int:menu_id>/', api_views.article_add_api, name='api_add_article'),
    path('article/<int:pk>/edit/', api_views.article_edit_api, name='api_edit_article'),
    path('article/delete/', api_views.article_delete_api, name='api_delete_article'),
]