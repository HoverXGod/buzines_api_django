from django.db import models

class Component(models.model):
    COMPONENT_TYPES = (
        "BLOCK",
        "ELEMENT",
        "FORM",
        "GROUP",
        "TABLE",
        "BUTTON",
        "INPUT_LABEL",
    )

    html_tag = models.CharField(max_length=16)
    html_label = models.CharField(max_length=32, null=True)
    html_style = models.CharField(max_length=128)
    html_id = models.IntegerField(null=True)
    description = models.TextField(max_length=512, null=True)
    component_type = models.CharField(max_length=16, choices=COMPONENT_TYPES)

    class Meta: pass

    def __str__(self): return super.__str__(self)

    def get_component_json(self) -> dict: pass

    def render_html(self, data: dict) -> str | None: pass


class HTMLStyle(models.Model):
    class_name = models.CharField(max_length=32)
    style = models.JSONField()

    class Meta: pass

    def __str__(self): return super.__str__(self)

    def get_style_json(self) -> dict: pass


class PageMarking(models.model):
    """ Стркуктура page_data
    {
        COMPONENT_ID: {
            COMPONENT_ID: DATA_ID | DATA,
            COMPONENT_ID: DATA_ID | DATA,
            COMPONENT_ID: {
                COMPONENT_ID: DATA_ID | DATA,
                COMPONENT_ID: DATA_ID | DATA,
                COMPONENT_ID: DATA_ID | DATA,
            },
            COMPONENT_ID: {
                DATA_ID | DATA,
                DATA_ID | DATA,
                DATA_ID | DATA,
            }
        },

        COMPONENT_ID: DATA_ID | DATA,
        COMPONENT_ID: DATA_ID | DATA,
        COMPONENT_ID: DATA_ID | DATA,
    }

    """

    page_name = models.CharField(max_length=128)
    page_data = models.JSONField()

    class Meta: pass

    def __str__(self) -> str: return str(self.page_name)

    def render_page(self): pass

