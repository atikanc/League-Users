from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.html import strip_tags
from django.contrib import messages
from .forms import SummonerInfo
from django.conf import settings
import requests
import json
import sys

API_key = settings.RIOT_KEY

def findSumm(userInput, request, adv):
    greeting = "League User Lookup: " + userInput

    summoner_name = userInput

    account_info = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name, headers = {"X-Riot-Token": API_key})
    
    if account_info.status_code != 200:
        messages.error(request, 'Summoner Not Found')
        return render(request, 'forms/name.html', {'form': SummonerInfo()})

    advanced = ""
    if adv == "true":
        advanced = "enabled"

    account_info = account_info.json()

    account_summId = str(account_info["id"])
    account_id = str(account_info["accountId"])
    account_puuid = str(account_info["puuid"])
    account_level = str(account_info["summonerLevel"])

    account_mastery = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/" + account_summId, headers = {"X-Riot-Token": API_key}).json()

    account_rank = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + account_summId, headers = {"X-Riot-Token": API_key}).json()

    acount_rank_val = "N/A"
    acount_rank_LP = "N/A"
    acount_rank_WL = "N/A"
    if(len(account_rank) != 0):
        acount_rank_val = ("%s %s" % (account_rank[0].get("tier"), account_rank[0].get("rank")))
        acount_rank_LP = ("%s" % account_rank[0].get("leaguePoints"))
        acount_rank_WL = ("%s/%s" % (account_rank[0].get("wins"), (account_rank[0].get("losses"))))

    champion_mastery_response = requests.get("https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + account_summId, headers = {"X-Riot-Token": API_key})
    champion_mastery_response = champion_mastery_response.json()

    champ_list = requests.get("https://ddragon.leagueoflegends.com/cdn/11.5.1/data/en_US/champion.json").json()

    mastery_levels = [0, 0, 0, 0, 0, 0, 0]
    chests_earned = 0
    champion_specifics = []

    for summ_champ in champion_mastery_response:
        for champ in champ_list["data"].keys():
            if(str(champ_list["data"].get(champ).get("key")) == str(summ_champ["championId"])):
                if(summ_champ["chestGranted"] == True):
                    chests_earned += 1
                mastery_levels[int(summ_champ["championLevel"])-1] += 1

                line = { 
                    "Champion" : (champ_list["data"].get(champ).get("name")),
                    "Mastery Level" : str(summ_champ["championLevel"]),
                    "Mastery Points" : str(summ_champ["championPoints"]),
                    "Pts for Lvl Up" : str(summ_champ["championPointsUntilNextLevel"]),
                    "Earned Chest?" : str(summ_champ["chestGranted"]),
                    "Tokens Stored" : str(summ_champ["tokensEarned"])
                }
                champion_specifics.append(line)

                # print((champ_list["data"].get(champ).get("name")))
                # print("\tMastery Level:\t" + str(summ_champ["championLevel"]))
                # print("\tMastery Points:\t" + str(summ_champ["championPoints"]))
                # print("\tPts for Lvl Up:\t" + str(summ_champ["championPointsUntilNextLevel"]))
                # print("\tGotten Chest:\t" + str(summ_champ["chestGranted"]))
                # print("\tTokens Stored:\t" + str(summ_champ["tokensEarned"]))

    # print("Mastery Summary".center(48, "-"))
    # for m in range(7, 0,-1):
    #     print("\tLevel " + str(m) + ": " + str(mastery_levels[m-1]))
    # print("\tTotal Chests Earned:" + str(chests_earned))
    return render(request, 'statPage.html', {
        'advanced' : advanced,
        'form': SummonerInfo(),
        'name' : greeting,
        'SummonerID' : account_summId,
        'AccountID' : account_id,
        'PUUID' : account_puuid,
        'Level' : account_level,
        'MasteryScore' : account_mastery,
        'rank' : acount_rank_val,
        'rank_LP' : acount_rank_LP,
        'rank_WL' : acount_rank_WL,
        'masteryLevels' : mastery_levels,
        'chestsEarned' : chests_earned,
        'champion_specifics' : champion_specifics
        })

def index(request):
    userInput = strip_tags(request.GET.get("SummName", ""))
    adv = strip_tags(request.GET.get("a", ""))

    if(userInput):
        return findSumm(userInput, request, adv)
    else:
        return render(request, 'forms/name.html', {'form': SummonerInfo()})