from django.http import Http404
from django.views.generic import DetailView, ListView

from goods.models import Products
from goods.utils import q_search
from django.db.models import Q

class CatalogView(ListView):
    model = Products
    # queryset = Products.objects.all().order_by("-id")
    template_name = "goods/catalog.html"
    context_object_name = "goods"
    paginate_by = 12
    allow_empty = True
    # чтоб удобно передать в методы
    slug_url_kwarg = "category_slug"

    def get_queryset(self):
        category_slug = self.kwargs.get(self.slug_url_kwarg)
        on_sale = self.request.GET.get("on_sale")
        order_by = self.request.GET.get("order_by")
        query = self.request.GET.get("q", "").strip()

        # Базовый queryset
        goods = super().get_queryset()

        # Фильтр по категории
        if category_slug and category_slug != "all":
            goods = goods.filter(category__slug=category_slug)

        # Поиск по неполному слову
        if query:
            goods = goods.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        # Если после фильтров товаров нет — 404
        if not goods.exists():
            raise Http404()

        # Фильтр по акции
        if on_sale:
            goods = goods.filter(discount__gt=0)

        # Сортировка
        if order_by and order_by != "default":
            goods = goods.order_by(order_by)

        return goods
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home - Каталог"
        context["slug_url"] = self.kwargs.get(self.slug_url_kwarg)
        context['query'] = self.request.GET.get("q", "").strip()
        return context


class ProductView(DetailView):

    # model = Products
    # slug_field = "slug"
    template_name = "goods/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_object(self, queryset=None):
        product = Products.objects.get(slug=self.kwargs.get(self.slug_url_kwarg))
        return product
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.name
        context['query'] = self.request.GET.get("q", "").strip()
        # Фильтруем картинки, чтобы убрать пустые
        context['images'] = self.object.images.exclude(image__isnull=True).exclude(image__exact='')
        return context


# def catalog(request, category_slug=None):

#     page = request.GET.get('page', 1)
#     on_sale = request.GET.get('on_sale', None)
#     order_by = request.GET.get('order_by', None)
#     query = request.GET.get('q', None)
    
#     if category_slug == "all":
#         goods = Products.objects.all()
#     elif query:
#         goods = q_search(query)
#     else:
#         goods = Products.objects.filter(category__slug=category_slug)
#         if not goods.exists():
#             raise Http404()

#     if on_sale:
#         goods = goods.filter(discount__gt=0)

#     if order_by and order_by != "default":
#         goods = goods.order_by(order_by)

#     paginator = Paginator(goods, 3)
#     current_page = paginator.page(int(page))

#     context = {
#         "title": "Home - Каталог",
#         "goods": current_page,
#         "slug_url": category_slug
#     }
#     return render(request, "goods/catalog.html", context)


# def product(request, product_slug):
#     product = Products.objects.get(slug=product_slug)

#     context = {"product": product}

#     return render(request, "goods/product.html", context)
