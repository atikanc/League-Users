from django import forms

class SummonerInfo(forms.Form):
    SummName = forms.CharField(label='Summoner Name', max_length=100)