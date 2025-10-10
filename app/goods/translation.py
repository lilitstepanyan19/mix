from modeltranslation.translator import register, translator, TranslationOptions
from .models import Products, Categories


@register(Categories)
class CategoriesTranslationOptions(TranslationOptions):
    fields = ("name",)



@register(Products)
class ProductsTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "description",
    )




