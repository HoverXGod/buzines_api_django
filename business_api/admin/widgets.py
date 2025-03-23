from django.forms import TextInput

class PhoneNumberWidget(TextInput):
    """Виджет для ввода телефонных номеров"""
    template_name = 'admin/widgets/phone_number.html'

    class Media:
        css = {'all': ('admin/css/phone-widget.css',)}
        js = ('admin/js/phone-mask.js',)