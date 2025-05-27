from django import forms

from oauth_admin.models import Review


class ReviewForm(forms.ModelForm):
    reason = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        decision = cleaned_data.get('decision')
        if decision == 'REJ' and not cleaned_data.get('reason'):
            raise forms.ValidationError('Reason must be filled for rejects', code='reason')
        return cleaned_data

    class Meta:
        model = Review
        fields = ('decision', 'reason')
