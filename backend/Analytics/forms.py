from django import forms
from .models import ProductPerformance

class ProductPerformanceForm(forms.ModelForm):
    # Кастомные поля для JSON metrics
    views = forms.IntegerField(min_value=0, label="Просмотры")
    cart_adds = forms.IntegerField(min_value=0, label="Добавления в корзину")
    purchases = forms.IntegerField(min_value=0, label="Покупки")
    stock_level = forms.IntegerField(min_value=0, label="Остаток на складе")

    class Meta:
        model = ProductPerformance
        exclude = ['metrics']  # Исключаем оригинальное JSON поле

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заполняем кастомные поля из JSON
        if self.instance and self.instance.metrics:
            self.fields['views'].initial = self.instance.metrics.get('views', 0)
            self.fields['cart_adds'].initial = self.instance.metrics.get('cart_adds', 0)
            self.fields['purchases'].initial = self.instance.metrics.get('purchases', 0)
            self.fields['stock_level'].initial = self.instance.metrics.get('stock_level', 0)

    def save(self, commit=True):
        # Сохраняем данные из кастомных полей в JSON
        instance = super().save(commit=False)
        instance.metrics = {
            'views': self.cleaned_data['views'],
            'cart_adds': self.cleaned_data['cart_adds'],
            'purchases': self.cleaned_data['purchases'],
            'stock_level': self.cleaned_data['stock_level'],
            'conversion_rate': instance.metrics.get('conversion_rate', 0.0)
        }
        if commit:
            instance.save()
        return instance

