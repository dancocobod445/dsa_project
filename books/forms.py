from django import forms
from datetime import date, timedelta
from .models import Book, GENRE_CHOICES, COVER_COLORS


class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['isbn', 'title', 'author', 'year', 'genre', 'copies_total', 'cover_color', 'description']
        widgets = {
            'isbn':         forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'e.g. 978-3-16-148410-0'}),
            'title':        forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'Book title'}),
            'author':       forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'Author full name'}),
            'year':         forms.NumberInput(attrs={'class': 'field-input', 'placeholder': '2023'}),
            'genre':        forms.Select(attrs={'class': 'field-input'}),
            'copies_total': forms.NumberInput(attrs={'class': 'field-input', 'min': 1, 'value': 1}),
            'cover_color':  forms.Select(attrs={'class': 'field-input'}),
            'description':  forms.Textarea(attrs={'class': 'field-input', 'rows': 3, 'placeholder': 'Short description (optional)'}),
        }


class BorrowRequestForm(forms.Form):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'field-input',
            'type': 'date',
        }),
        help_text='Choose a return date — minimum 1 day, maximum 14 days from today.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        min_date = today + timedelta(days=1)
        max_date = today + timedelta(days=14)
        self.fields['due_date'].widget.attrs.update({
            'min': min_date.isoformat(),
            'max': max_date.isoformat(),
        })
        self.fields['due_date'].initial = max_date

    def clean_due_date(self):
        due = self.cleaned_data['due_date']
        today = date.today()
        if due < today + timedelta(days=1):
            raise forms.ValidationError('Return date must be at least 1 day from today.')
        if due > today + timedelta(days=14):
            raise forms.ValidationError('Return date cannot exceed 14 days from today.')
        return due


class RejectRequestForm(forms.Form):
    reason = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'field-input',
            'placeholder': 'Reason for rejection (optional)',
        })
    )


class SearchForm(forms.Form):
    FIELD_CHOICES = [('title', 'Title'), ('author', 'Author')]

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'Search books...'})
    )
    field = forms.ChoiceField(
        choices=FIELD_CHOICES,
        widget=forms.Select(attrs={'class': 'field-input'})
    )
