from django import forms




ENTRY_CHOICES = [ ('0', 'No Entries'), ('6', 'Six Entries'), ('12', 'Twelve Entries'), ('18', 'Eighteen Entries')]
PORTFOLIO_CHOICES = [('0','No Portfolios'), ('1','One Portfolio'), ('2','Two Portfolios')]


class PaymentPlanForm(forms.Form):
    number_of_entries = forms.ChoiceField(widget=forms.RadioSelect, choices=ENTRY_CHOICES, label='Number of Entries', initial=12)
    number_of_portfolios = forms.ChoiceField(widget=forms.Select, choices=PORTFOLIO_CHOICES, label='Number of Portfolios', initial=0)
    youth_entry = forms.BooleanField(widget=forms.CheckboxInput, label="Youth Entry", required=False)

    def clean(self):
        cleaned_data = super().clean()
        number_of_entries = cleaned_data.get("number_of_entries")
        number_of_portfolios = cleaned_data.get("number_of_portfolios")


        if number_of_entries == 0 and number_of_portfolios == 0:
                raise ValidationError(
                    "You need to choose either a Portfolio Plan or an Entry Plan"
                )
