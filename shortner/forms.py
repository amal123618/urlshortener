from django import forms

class ShortenForm(forms.Form):
    url = forms.URLField(
        label="Long URL",
        widget=forms.URLInput(attrs={
            "placeholder": "https://example.com/very/long/link",
            "class": "w-full border px-3 py-2 rounded-lg",
            "required": True
        })
    )
    custom_code = forms.CharField(
        label="Custom code (optional)",
        max_length=8,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. mylink",
            "class": "w-full border px-3 py-2 rounded-lg",
        })
    )
