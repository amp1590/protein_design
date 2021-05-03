from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

CHAIN_NAME_CHOICES=( 
    ("A", "A"), 
    ("B", "B"), 
    ("C", "C"), 
) 

MODEL_NAME_CHOICES=(
    ("BBO", "BBO"),
    ("BBS","BBS")
)

MODEL_VERSION_CHOICES=(
    ("90", "90"),
    ("30","30")
)

def validate_alpha(value): #Why not working!!
    if value.isalpha() != 1:
        raise ValidationError(
            _('%(value)s should be a single capital letter!'),
            params={'value': value},
        )

letters = RegexValidator(r'^[A-Z]*$', 'Only single captial letters are allowed.')


class NameForm(forms.Form):
    pdb_file = forms.FileField(label="PDB File")
    chain_name = forms.CharField(initial="A", max_length=1, validators=[validate_alpha])
    prediction_begin_range = forms.IntegerField(initial='1')
    prediction_end_range = forms.IntegerField(initial='-1')
    model_name = forms.ChoiceField(choices = MODEL_NAME_CHOICES)
    model_version = forms.ChoiceField(choices = MODEL_VERSION_CHOICES)
    recipient = forms.EmailField(label="Your Email")

class ContactForm(forms.Form):
    #subject = forms.CharField(max_length=100)
    #message = forms.CharField(widget=forms.Textarea)
    #sender = forms.EmailField()
    #cc_myself = forms.BooleanField(required=False)
    recipient = forms.EmailField()
    