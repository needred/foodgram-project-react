from django.forms import widgets


class ColorPicker(widgets.Input):
    input_type = 'text'
    template_name = 'recipes/color_picker_2.html'
