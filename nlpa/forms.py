from django import forms




ENTRY_CHOICES = [('6', 'Six Entries'), ('12', 'Twelve Entries'), ('18', 'Eighteen Entries')]
PORTFOLIO_CHOICES = [('0','No Porfolios'), ('1','One Porfolio'), ('2','Two Porfolios')]


class PaymentPlanForm(forms.Form):
    number_of_entries = forms.ChoiceField(widget=forms.Select, choices=ENTRY_CHOICES, label='Number of Entries')
    number_of_portfolios = forms.ChoiceField(widget=forms.Select, choices=PORTFOLIO_CHOICES, label='Number of Portfolios')

class EntriesForm(forms.Form):
    number_of_entries = forms.ChoiceField(widget=forms.Select, choices=ENTRY_CHOICES, label='Number of Entries')
    number_of_portfolios = forms.ChoiceField(widget=forms.Select, choices=PORTFOLIO_CHOICES, label='Number of Portfolios')
