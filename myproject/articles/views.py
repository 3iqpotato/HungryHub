from django.shortcuts import render
from django.views import View

# Create your views here.
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from .models import Article, Menu
# from .forms import ArticleForm


class ArticleCreateView(CreateView):
    model = Article
    fields = ['name', 'img', 'type', 'ingredients', 'price', 'weight', 'category']
    template_name = 'articles/article_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = get_object_or_404(Menu, id=self.kwargs['menu_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('restaurant_menu_edit', kwargs={'pk': self.kwargs['menu_id']})

    # def form_valid(self, form):
    #     menu = get_object_or_404(Menu, id=self.kwargs['menu_id'])
    #     self.object.menus.add(menu)
    #     response = super().form_valid(form)
    #
    #     return response

    def form_valid(self, form):
        # Автоматично задаваме менюто от URL параметъра
        form.instance.menu = get_object_or_404(Menu, id=self.kwargs['menu_id'])
        return super().form_valid(form)


class ArticleUpdateView(UpdateView):
    model = Article
    fields = ['name', 'img', 'type', 'ingredients', 'price', 'weight', 'category']
    template_name = 'articles/article_edit.html'

    def get_success_url(self):
        return reverse_lazy('restaurant_menu_edit', kwargs={'pk': self.object.menu.id})


class ArticleDeleteView(View):
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, id=request.POST.get('delete_article'))
        menu_id = article.menu.id
        article.delete()
        return redirect(reverse('restaurant_menu_edit', kwargs={'pk': menu_id}))