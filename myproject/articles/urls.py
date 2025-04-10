from django.urls import path
from .views import (ArticleCreateView,
                   ArticleUpdateView, ArticleDeleteView)

urlpatterns = [
    path('article/add/<int:menu_id>/', ArticleCreateView.as_view(), name='add_article_to_menu'),
    path('article/<int:pk>/edit/', ArticleUpdateView.as_view(), name='edit_article'),
    path('article/delete/', ArticleDeleteView.as_view(), name='delete_article'),
]