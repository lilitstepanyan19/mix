from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.utils import translation
from django.db.models import Q

from goods.models import Products
from goods.utils import q_search


class CatalogView(ListView):
    model = Products
    template_name = "goods/catalog.html"
    context_object_name = "goods"
    paginate_by = 12
    allow_empty = True
    slug_url_kwarg = "category_slug"

    def get_queryset(self):
        category_slug = self.kwargs.get(self.slug_url_kwarg)
        on_sale = self.request.GET.get("on_sale")
        order_by = self.request.GET.get("order_by")
        query = self.request.GET.get("q", "").strip()

        goods = super().get_queryset()

        if category_slug and category_slug != "all":
            goods = goods.filter(category__slug=category_slug)

        lang = translation.get_language()
        name_field = f"name_{lang}"
        desc_field = f"description_{lang}"

        if query:
            goods = goods.filter(
                Q(**{f"{name_field}__icontains": query})
                | Q(**{f"{desc_field}__icontains": query})
            )

        if not goods.exists():
            raise Http404()

        if on_sale:
            goods = goods.filter(discount__gt=0)

        if order_by and order_by != "default":
            goods = goods.order_by(order_by)

        return goods

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home - Каталог"
        context["slug_url"] = self.kwargs.get(self.slug_url_kwarg)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class ProductView(DetailView):
    template_name = "goods/product.html"
    slug_url_kwarg = "product_slug"
    context_object_name = "product"

    def get_object(self, queryset=None):
        return get_object_or_404(Products, slug=self.kwargs.get(self.slug_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        lang = translation.get_language()
        name_field = f"name_{lang}"
        desc_field = f"description_{lang}"

        product = self.object
        context["title"] = getattr(product, name_field, product.name_ru)
        context["description"] = getattr(product, desc_field, product.description_ru)

        context["query"] = self.request.GET.get("q", "").strip()
        context["images"] = product.images.filter(image__isnull=False).exclude(image="")

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
