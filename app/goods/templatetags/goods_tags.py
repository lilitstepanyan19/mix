from django import template
from django.utils.http import urlencode
import re

from goods.models import Categories


register = template.Library()


@register.simple_tag()
def tag_categories():
    return Categories.objects.all()


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.dict()
    # example with other context vars
    # print(context['title'])
    # print(context['slug_url'])
    # print(context['goods'])
    # print([product.name for product in context['goods']])
    query.update(kwargs)
    return urlencode(query)

@register.filter
def highlight(text, query):
    if not query:
        return text
    words = query.split()  # разбиваем по пробелам
    for word in words:
        escaped = re.escape(word)
        pattern = re.compile(escaped, re.IGNORECASE)
        text = pattern.sub(lambda m: f'<mark style="background-color: #ff6; color: red;">{m.group(0)}</mark>', text)
    return text

@register.filter
def filter_by_category(products, category_id):
    return [p for p in products if p.category_id == category_id][:2]  # первые 5 товаров категории