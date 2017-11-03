# -*- coding: utf-8 -*-
#telegrambot.py
#import numpy as np
import json
import requests
import time
import urllib
import random
import re
import os
import pickle
import string
import pandas as pd
from datetime import datetime,date,timedelta

value_dir = os.getcwd()
##------------------------------------------------------------------------------------------------------
os.chdir(r"\data_01Nov2017")

obj =[]
with open("mtd_yesterday_"+datetime.strftime(date.today() - timedelta(1) , "%Y%b%d")+".pickle","rb") as pkl:
    while True:
        try:
            obj.append(pickle.load (pkl))
        except EOFError:
            break

mtd_yesterday = obj[0]
del obj
##creating a namespace called mtd_yesterday for calculated of last day
##-----------------------------------------------------------------------------------------------------
os.chdir(value_dir)
exec(open('fytd.py').read())


#Global variables token and url
TOKEN = "460347293:AAFCS3bDSKf5j_MjwU9EZvduRjhOuYeVOIw"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
#Greetings global variables
GREETINGS = ["Hi", "Hello", "Namaskar", "Namaste"]
approve_ids = (440672469,403007169, 371351771)


#--------------Pandas Processing------------------------------------------------#
#import numpy as np

PATH = r"\data_02Nov2017"
os.chdir(PATH)
def importing_csv(fname):
    df = pd.read_csv(fname, header=0)
    return df

AccountInfoBank = importing_csv("AccountInfoBank.csv")
AccountInfoDetails = importing_csv("AccountInfoDetails.csv")
ActiveCust = importing_csv("ActiveCust.csv")
ATMTxnFailure = importing_csv("ATMTxnFailure.csv") #Not used
CashBalnces = importing_csv("CashBalnces.csv")
FTM_ChannelTxn = importing_csv("FTM_ChannelTxn.csv")
IPFlag = importing_csv("IPFlag.csv")
NewCust = importing_csv("NewCust.csv")
onBoarding = importing_csv("onBoarding.csv") #Not used
StandaloneCustomer = importing_csv("StandaloneCustomer.csv")

###-------------Channel derivation----------------------------
def map_values(row, values_dict):
    return values_dict[row]

values_dict = {"MB": "Mobile Banking", "IB": "Internet Banking", "POS": "POS", "ATMWithdOnUs": "ATM", "ATMDeposit": "ATM", "ATMWithdOffUs": "ATM",
"NEFT/IMPS/RTGS": "Branch Banking", "InwardCheque": "Branch Banking","CashWithd": "Branch Banking","OutwardCheque": "Branch Banking",
"CashDeposit": "Branch Banking"}

FTM_ChannelTxn["Channel"] = FTM_ChannelTxn['ChannelFlag'].apply(map_values, args = (values_dict,))


def check_for_dash_space(dframe, dt_colname):
    if " " in dframe[dt_colname].head(1).sum():
        delim=" "
    elif "-" in dframe[dt_colname].head(1).sum():
        delim="-"
    else:
        dframe.loc[:,dt_colname] = dframe.loc[:,dt_colname].replace(string.punctuation, " ")
        delim = " "
    return delim


# df_final.columns = [c.replace(' ', '_') for c in df_final.columns]


def change_date_string_date(dframe,dt_colname=None,delim=" "):
    delim = check_for_dash_space(dframe, dt_colname)
    dframe1 = pd.DataFrame(dframe[dt_colname].str.split(delim,1).tolist(),
                                   columns = ['month','year'])
    dframe1["date"] = pd.to_datetime("01"+"-"+dframe1["month"]+"-"+dframe1["year"])
    del dframe1["month"]
    del dframe1["year"]
    return dframe1["date"].dt.date

#---------------------------------------------------------------------------------------------
def extract_info(dframe, key="TotalAccounts", value="2017-01-01"):
    try:
        return str(round(float(dframe.loc[dframe.index == value, key]),2))
    except TypeError:
        return "Unavailable value"

def extract_info_with_grps(dframe, key="TxnCount",groups="Channel",grp_value="ATM",  value="2017-08-01"):
    try:
        return  str(float(dframe.loc[(dframe.index == value) & (dframe[groups] == grp_value), key ]))
    except (TypeError,KeyError):
        return "Unavailable value"

#extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy)

#extract_info(df_monyy, key="TotalAccounts", value="2016-01-01")
#Determing if the month value is in correct format of mon yyyy or monyyyy
def month_processing(string):
    try:
        string = string.lower()
        match_found = re.match("([a-zA-Z]{3})\s*(\d{4})", string)
        return " ".join(match_found.groups()).title()
    except AttributeError:
        return "Unknown month year format"

def outcome_monthyr(string):
    x = month_processing(string)
    if x.split(" ")[0] == "Unknown":
        return "Unknown"
    else:
        return datetime.strftime(datetime.strptime(x.split(" ")[-1]+ "-" + x.split(" ")[0] + "-" + "01", "%Y-%b-%d"),"%Y-%m-%d")

###Writing the generic function for the pandas extraction of values -----------------------------------------------------------
# def extraction_of_data(dframe=None, variables="TotalAccounts", date_variable="MonthNam", constant_divisor = 1 ):
#
#     dframex = change_date_string_date(dframe, dt_colname="MonthNam")
#     dframe_final = pd.concat([dframex.reset_index(drop=True),pd.DataFrame(dframe)], axis=1)
#     dframe_final.sort_values(by="date", inplace=True)
#
#     mtd = dict()
#     mtd[variables] = str(round(float(dframe_final.tail(1)[variables]/(constant_divisor)),2)) #mtd_totalaccounts
#     return mtd
#
# extraction_of_data(dframe=AccountInfoBank1, variables="TotalAccounts", date_variable="MonthNam", constant_divisor=1)
# extraction_of_data(dframe=AccountInfoBank1, variables="TotalAccounts", date_variable="MonthNam", constant_divisor=1)
# extraction_of_data(dframe=AccountInfoBank1, variables="TotalAccounts", date_variable="MonthNam", constant_divisor=1)


    # mtd_EOPBalance = str(round(float(AccountInfoBank1.tail(1).EOPBalance/(10**7)),2)) #mtd_EOPBalance
    # mtd_AvgMTLBalnce = str(round(float(AccountInfoBank1.tail(1).AvgMTLBalnce/(10**7)),2)) #mtd_AvgMTLBalnce
    # df_monyy = AccountInfoBank1.loc[:,["date", "TotalAccounts", "EOPBalance", "AvgMTLBalnce"]]
    # df_monyy = df_monyy.set_index(df_monyy.date.astype("str")).loc[:,["TotalAccounts", "EOPBalance", "AvgMTLBalnce" ]]

################################################################################################################################
#-------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################

###For Banks Menu---------------------------------------------------------------------------
#Total Acc, AMB, BookValue------------------------------------------------------------------
AccountInfoBank_dt = change_date_string_date(AccountInfoBank, dt_colname="MonthNam")
AccountInfoBank1 = pd.concat([AccountInfoBank.reset_index(drop=True),pd.DataFrame(AccountInfoBank_dt)], axis=1)
AccountInfoBank1.sort_values(by="date", inplace=True)


mtd_totalaccounts = str(float(AccountInfoBank1.tail(1).TotalAccounts))
mtd_EOPBalance = str(round(float(AccountInfoBank1.tail(1).EOPBalance/(10**7)),2))
mtd_AvgMTLBalnce = str(round(float(AccountInfoBank1.tail(1).AvgMTLBalnce/(10**7)),2))

#New Edits
df_monyy = AccountInfoBank1.loc[:,["date", "TotalAccounts", "EOPBalance", "AvgMTLBalnce"]]
df_monyy = df_monyy.set_index(df_monyy.date.astype("str")).loc[:,["TotalAccounts", "EOPBalance", "AvgMTLBalnce" ]]
df_monyy.loc[:, "EOPBalance"] = round(df_monyy.loc[:, "EOPBalance"]/10**7,2)
df_monyy.loc[:, "AvgMTLBalnce"] = round(df_monyy.loc[:, "AvgMTLBalnce"]/10**7, 2)

#NewCust---------------------------------------------------------------------------------------

NewCust_dt = change_date_string_date(NewCust, dt_colname="AsOnYrMonName")
NewCust1 = pd.concat([NewCust.reset_index(drop=True),pd.DataFrame(NewCust_dt)], axis=1)
NewCust1.sort_values(by="date", inplace=True)
last_value_nc = list(NewCust1.tail(1)["AsOnYrMonName"])
mtd_NewCust = str(round(float(NewCust1.loc[NewCust1.AsOnYrMonName == last_value_nc[0], "CustCount"].sum(0)),2))

grpby_NewCust_monyy = pd.DataFrame(NewCust1['CustCount'].groupby([NewCust1['date']]).sum())
grpby_NewCust_monyy.index = grpby_NewCust_monyy.index.astype("str")

#----------------------------------------------------------------------------------------------
#IPFlag---------------------------------------------------------------------------------------
IPFlag_0 = IPFlag.loc[IPFlag.IPFlag == 0, :]
IPFlag_1 = IPFlag.loc[IPFlag.IPFlag == 1, :]
IPFlag_0_dt = change_date_string_date(IPFlag_0, dt_colname="YrMon_Acc_Opn_Date")
IPFlag_01 = pd.concat([IPFlag_0.reset_index(drop=True),pd.DataFrame(IPFlag_0_dt)], axis=1)
IPFlag_01.sort_values(by="date", inplace=True)
IPFlag_1_dt = change_date_string_date(IPFlag_1, dt_colname="YrMon_Acc_Opn_Date")
IPFlag_11 = pd.concat([IPFlag_1.reset_index(drop=True),pd.DataFrame(IPFlag_1_dt)], axis=1)
IPFlag_11.sort_values(by="date", inplace=True)

last_value_ip_0 = list(IPFlag_01.tail(1)["date"])
last_value_ip_1 = list(IPFlag_11.tail(1)["date"])

if last_value_ip_1 < last_value_ip_0:
    last_value_ip_0 = list(IPFlag_11.tail(1)["YrMon_Acc_Opn_Date"])
    last_value_ip_1 = list(IPFlag_11.tail(1)["YrMon_Acc_Opn_Date"])
elif last_value_ip_1 > last_value_ip_0:
    last_value_ip_0 = list(IPFlag_01.tail(1)["YrMon_Acc_Opn_Date"])
    last_value_ip_1 = list(IPFlag_01.tail(1)["YrMon_Acc_Opn_Date"])
else:
    last_value_ip_0 = list(IPFlag_01.tail(1)["YrMon_Acc_Opn_Date"])
    last_value_ip_1 = list(IPFlag_11.tail(1)["YrMon_Acc_Opn_Date"])

mtd_IPFlag_11 = float(IPFlag_11.loc[IPFlag_11.YrMon_Acc_Opn_Date == last_value_ip_1[0], "Count(ACCT_NBR)"].sum(0))
mtd_IPFlag_01 = float(IPFlag_01.loc[IPFlag_01.YrMon_Acc_Opn_Date == last_value_ip_0[0], "Count(ACCT_NBR)"].sum(0))
mtd_IPFlag_percentage = str(round(mtd_IPFlag_11/(mtd_IPFlag_01+mtd_IPFlag_11),2)*100) + "%"

grpby_NewCust_monyy_1 = pd.DataFrame(IPFlag_11['Count(ACCT_NBR)'].groupby([IPFlag_11['date']]).sum())
grpby_NewCust_monyy_0 = pd.DataFrame(IPFlag_01['Count(ACCT_NBR)'].groupby([IPFlag_01['date']]).sum())
grpby_NewCust_monyy_0['Count_0'] = grpby_NewCust_monyy_0['Count(ACCT_NBR)']
del grpby_NewCust_monyy_0['Count(ACCT_NBR)']
grpby_NewCust_monyy_1['Count_1'] = grpby_NewCust_monyy_1['Count(ACCT_NBR)']
del grpby_NewCust_monyy_1['Count(ACCT_NBR)']

#
grpby_NewCust_monyy_1.index = grpby_NewCust_monyy_1.index.astype("str")
grpby_NewCust_monyy_0.index = grpby_NewCust_monyy_0.index.astype("str")

grpby_NewCust_monyy_concat = pd.concat([grpby_NewCust_monyy_1, grpby_NewCust_monyy_0] ,axis =1)
grpby_NewCust_monyy_concat["percentage"] = round(grpby_NewCust_monyy_concat.Count_1/(grpby_NewCust_monyy_concat.Count_1+grpby_NewCust_monyy_concat.Count_0),2)

#----------------------------------------------------------------------------------------------
#CashBalnces----------------------------------------------------------------------------------

cashbalances_dt = change_date_string_date(CashBalnces, dt_colname="YrMon")
CashBalnces1 = pd.concat([CashBalnces.reset_index(drop=True),pd.DataFrame(cashbalances_dt)], axis=1)
CashBalnces1.sort_values(by="date", inplace=True)
last_value_cb = list(CashBalnces1.tail(1)["YrMon"])
mtd_CashBalnces = str(round(float(CashBalnces1.loc[CashBalnces1.YrMon == last_value_cb[0], "DayEndBal"].sum(0)/10**7),2))

#change also in yesterday file
grpby_cash_balances_monyy = pd.DataFrame(CashBalnces1['DayEndBal'].groupby([CashBalnces1['date']]).sum()/10**7)
grpby_cash_balances_monyy["DayEndBal"] = round(grpby_cash_balances_monyy["DayEndBal"],2)
grpby_cash_balances_monyy.index = grpby_cash_balances_monyy.index.astype("str")
#----------------------------------------------------------------------------------------------
#Active Customers------------------------------------------------------------------------------

ActiveCust_dt = change_date_string_date(ActiveCust, dt_colname="YrMon_AsOnDate")
ActiveCust1 = pd.concat([ActiveCust.reset_index(drop=True),pd.DataFrame(ActiveCust_dt)], axis=1)
ActiveCust1.sort_values(by="date", inplace=True)
last_value_ac = list(ActiveCust1.tail(1)["YrMon_AsOnDate"])
mtd_ActiveCust_temp = ActiveCust1.loc[ActiveCust1.YrMon_AsOnDate == last_value_ac[0], ["TxnActCusts", "CountAccs"]].sum(0)
mtd_ActiveCust = str(round(float(mtd_ActiveCust_temp.TxnActCusts / mtd_ActiveCust_temp.CountAccs)*100,2)) + "%"


grpby_ActiveCust1_monyy = pd.DataFrame(ActiveCust1[['TxnActCusts','CountAccs']].groupby([ActiveCust1['date']]).sum())
#change in yesterday file as well
grpby_ActiveCust1_monyy["percentage"] = grpby_ActiveCust1_monyy["TxnActCusts"]*100/grpby_ActiveCust1_monyy["CountAccs"]
del grpby_ActiveCust1_monyy["TxnActCusts"]
del grpby_ActiveCust1_monyy["CountAccs"]

grpby_ActiveCust1_monyy.index = grpby_ActiveCust1_monyy.index.astype("str")

#Helper function----------------------------------------------------------------------------------------------

def compress_spaces(text):
    spaces = re.compile("\s+")
    return spaces.sub(" ",text)

#compress_spaces("abc    def")

###For Branch Menu---------------------------------------------------------------------------
list_of_branches = [compress_spaces(item.upper()) for item in list(AccountInfoDetails.loc[:, "BRNCH_NME"].unique())]
AccountInfoDetails_dt = change_date_string_date(AccountInfoDetails, dt_colname="MonthNam", delim="-")
AccountInfoDetails1 = pd.concat([AccountInfoDetails.reset_index(drop=True),pd.DataFrame(AccountInfoDetails_dt)], axis=1)
AccountInfoDetails1.sort_values(by="date", inplace=True)
last_value_ad = list(AccountInfoDetails1.tail(1)["MonthNam"])
#Extra Step for cleanup
AccountInfoDetails1["BRNCH_NME"] = AccountInfoDetails1["BRNCH_NME"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()

# Book value and total accounts & AMB
AccountInfoDetails2 = AccountInfoDetails1.loc[AccountInfoDetails1["MonthNam"] == last_value_ad[0]]
AccountInfoDetaisl_branch_mix = pd.DataFrame(AccountInfoDetails2[["TotalAccounts","EOPBalance","AvgMTLBalnce"]].groupby(AccountInfoDetails2["BRNCH_NME"]).sum())
AccountInfoDetaisl_branch_account_mix = AccountInfoDetaisl_branch_mix.loc[:, "TotalAccounts"]
AccountInfoDetaisl_branch_eop_mix = AccountInfoDetaisl_branch_mix.loc[:, "EOPBalance"]
AccountInfoDetaisl_branch_amb_mix = AccountInfoDetaisl_branch_mix.loc[:, "AvgMTLBalnce"]
mtd_branch_account_dict = {iterx : str(round(float(AccountInfoDetaisl_branch_account_mix[AccountInfoDetaisl_branch_account_mix.index == iterx].sum(0)/1),2)) for iterx in list_of_branches}
mtd_branch_eop_dict = {iterx : str(round(float(AccountInfoDetaisl_branch_eop_mix[AccountInfoDetaisl_branch_eop_mix.index == iterx].sum(0)/10**7),2)) for iterx in list_of_branches}
mtd_branch_amb_dict = {iterx : str(round(float(AccountInfoDetaisl_branch_amb_mix[AccountInfoDetaisl_branch_amb_mix.index == iterx].sum(0)/10**7),2)) for iterx in list_of_branches}

grpby_mtd_AccountInfoDetaisl_branch_mix_monyy = AccountInfoDetails1.groupby(["date","BRNCH_NME"]).sum()
grpby_mtd_AccountInfoDetaisl_branch_mix_monyy = grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.loc[:, ["TotalAccounts","EOPBalance","AvgMTLBalnce"]]
grpby_mtd_AccountInfoDetaisl_branch_mix_monyy = grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.reset_index().set_index("date")
grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.index = grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.index.astype("str")
grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.loc[:,"EOPBalance" ] = round(grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.loc[:,"EOPBalance" ] /10**7,2)
grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.loc[:,"AvgMTLBalnce" ] = round(grpby_mtd_AccountInfoDetaisl_branch_mix_monyy.loc[:,"AvgMTLBalnce" ] /10**7,2)


# New Customers

NewCust_dt = change_date_string_date(NewCust, dt_colname="AsOnYrMonName")
NewCust1 = pd.concat([NewCust.reset_index(drop=True),pd.DataFrame(NewCust_dt)], axis=1)
NewCust1.sort_values(by="date", inplace=True)
last_value_nc = list(NewCust1.tail(1)["AsOnYrMonName"])
#Extra Step for cleanup
NewCust1["BName"] = NewCust1["BName"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()

mtd_NewCust_branch_mix = NewCust1.loc[NewCust1.AsOnYrMonName == last_value_nc[0], "CustCount"].groupby(NewCust1["BName"]).sum()

NewCust_branch_mix_monyy = NewCust1.groupby(['date',"BName"]).sum()
NewCust_branch_mix_monyy = NewCust_branch_mix_monyy.reset_index(drop=False).set_index("date")
NewCust_branch_mix_monyy.index = NewCust_branch_mix_monyy.index.astype("str")

# %Active Clients

ActiveCust_dt = change_date_string_date(ActiveCust, dt_colname="YrMon_AsOnDate")
ActiveCust1 = pd.concat([ActiveCust.reset_index(drop=True),pd.DataFrame(ActiveCust_dt)], axis=1)
ActiveCust1.sort_values(by="date", inplace=True)
last_value_ac = list(ActiveCust1.tail(1)["YrMon_AsOnDate"])
#Extra Step for cleanup
ActiveCust1["BRNCH_NME"] = ActiveCust1["BRNCH_NME"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()


mtd_ActiveCust_branch_temp = ActiveCust1.loc[ActiveCust1.YrMon_AsOnDate == last_value_ac[0], ["TxnActCusts", "CountAccs"]].groupby(ActiveCust1["BRNCH_NME"]).sum()
mtd_ActiveCust_branch_temp["percentage"] = round(mtd_ActiveCust_branch_temp.TxnActCusts / mtd_ActiveCust_branch_temp.CountAccs*100,2)
mtd_ActiveCust_branch_temp = mtd_ActiveCust_branch_temp.loc[:, "percentage"]

#change to be done in yesterday file as well
grpby_ActiveCust1_branch_monyy = ActiveCust1.groupby(['date','BRNCH_NME']).sum()
grpby_ActiveCust1_branch_monyy["percentage"] = grpby_ActiveCust1_branch_monyy["TxnActCusts"]*100/grpby_ActiveCust1_branch_monyy["CountAccs"]
del grpby_ActiveCust1_branch_monyy["TxnActCusts"]
del grpby_ActiveCust1_branch_monyy["CountAccs"]


grpby_ActiveCust1_branch_monyy = grpby_ActiveCust1_branch_monyy.reset_index(drop=False).set_index("date")
grpby_ActiveCust1_branch_monyy.index = grpby_ActiveCust1_branch_monyy.index.astype("str")
grpby_ActiveCust1_branch_monyy.loc[:,"percentage"] = round(grpby_ActiveCust1_branch_monyy.loc[:,"percentage"],2)
# Cash Day End Balance

cashbalances_dt = change_date_string_date(CashBalnces, dt_colname="YrMon")
CashBalnces1 = pd.concat([CashBalnces.reset_index(drop=True),pd.DataFrame(cashbalances_dt)], axis=1)
CashBalnces1.sort_values(by="date", inplace=True)
#Extra Step for cleanup
CashBalnces1["BRNCH_NME"] = CashBalnces1["BRNCH_NME"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()
last_value_cb = list(CashBalnces1.tail(1)["YrMon"])

mtd_CashBalnces_branch_mix = round(CashBalnces1.loc[CashBalnces1.YrMon == last_value_cb[0], ["DayEndBal", "BRNCH_NME"]].groupby(CashBalnces1["BRNCH_NME"]).sum()/10**7,2)

grpby_cash_balances_branch_monyy = CashBalnces1.groupby(['date',"BRNCH_NME"]).sum()
grpby_cash_balances_branch_monyy = grpby_cash_balances_branch_monyy.reset_index(drop=False).set_index("date")
grpby_cash_balances_branch_monyy["DayEndBal"] = round(grpby_cash_balances_branch_monyy["DayEndBal"]/10**7,2)
grpby_cash_balances_branch_monyy.index = grpby_cash_balances_branch_monyy.index.astype("str")

###For Products------------------------------------------------------------------------------
#AccountInfoDetails -------------------------------------------------------------------------

AccountInfoDetails_dt = change_date_string_date(AccountInfoDetails, dt_colname="MonthNam", delim="-")
AccountInfoDetails1 = pd.concat([AccountInfoDetails.reset_index(drop=True),pd.DataFrame(AccountInfoDetails_dt)], axis=1)
AccountInfoDetails1.sort_values(by="date", inplace=True)
last_value_ad = list(AccountInfoDetails1.tail(1)["MonthNam"])
AccountInfoDetails1_temp = pd.DataFrame(AccountInfoDetails1.loc[AccountInfoDetails1.MonthNam == last_value_ad[0], ["TotalAccounts", "EOPBalance"]].sum(0)).T
mtd_AccountInfoDetails1_bookvalue =  str(round(float(AccountInfoDetails1_temp.EOPBalance/10**7),2))
mtd_AccountInfoDetails1_noa =  str(round(float(AccountInfoDetails1_temp.TotalAccounts),2))

grpby_AccountInfoDetails1_monyy = pd.DataFrame(AccountInfoDetails1[['EOPBalance','TotalAccounts']].groupby([AccountInfoDetails1['date']]).sum())
grpby_AccountInfoDetails1_bookvalue_monyy = grpby_AccountInfoDetails1_monyy.loc[:,["EOPBalance"]]
grpby_AccountInfoDetails1_noa_monyy = grpby_AccountInfoDetails1_monyy.loc[:,["TotalAccounts"]]

#--------SA----------------------------------------------------------------------------------

AccountInfoDetails1_SA_temp = pd.DataFrame(AccountInfoDetails1.loc[(AccountInfoDetails1.MonthNam == last_value_ad[0]) & (AccountInfoDetails1.ProdGroup == "SA"),["TotalAccounts","EOPBalance"]].sum(0)).T
mtd_AccountInfoDetails1_SA_bookvalue =  str(round(float(AccountInfoDetails1_SA_temp.EOPBalance/10**7),2))
mtd_AccountInfoDetails1_SA_noa =  str(round(float(AccountInfoDetails1_SA_temp.TotalAccounts),2))

grpby_AccountInfoDetails1_SA_monyy = pd.DataFrame(AccountInfoDetails1.loc[AccountInfoDetails1.ProdGroup == "SA", ['EOPBalance','TotalAccounts']].groupby([AccountInfoDetails1['date']]).sum())
grpby_AccountInfoDetails1_SA_bookvalue_monyy = round(grpby_AccountInfoDetails1_SA_monyy.loc[:,["EOPBalance"]]/10**7,2)
grpby_AccountInfoDetails1_SA_noa_monyy = grpby_AccountInfoDetails1_SA_monyy.loc[:,["TotalAccounts"]]
grpby_AccountInfoDetails1_SA_noa_monyy.index = grpby_AccountInfoDetails1_SA_noa_monyy.index.astype("str")
grpby_AccountInfoDetails1_SA_bookvalue_monyy.index = grpby_AccountInfoDetails1_SA_bookvalue_monyy.index.astype("str")
#--------RD-----------------------------------------------------------------------------------

AccountInfoDetails1_RD_temp = pd.DataFrame(AccountInfoDetails1.loc[(AccountInfoDetails1.MonthNam == last_value_ad[0]) & (AccountInfoDetails1.ProdGroup == "RD"),["TotalAccounts","EOPBalance"]].sum(0)).T
mtd_AccountInfoDetails1_RD_bookvalue =  str(round(float(AccountInfoDetails1_RD_temp.EOPBalance/10**7),2))
mtd_AccountInfoDetails1_RD_noa =  str(round(float(AccountInfoDetails1_RD_temp.TotalAccounts),2))

grpby_AccountInfoDetails1_RD_monyy = pd.DataFrame(AccountInfoDetails1.loc[AccountInfoDetails1.ProdGroup == "RD", ['EOPBalance','TotalAccounts']].groupby([AccountInfoDetails1['date']]).sum())
grpby_AccountInfoDetails1_RD_bookvalue_monyy = round(grpby_AccountInfoDetails1_RD_monyy.loc[:,["EOPBalance"]]/10**7,2)
grpby_AccountInfoDetails1_RD_noa_monyy = grpby_AccountInfoDetails1_RD_monyy.loc[:,["TotalAccounts"]]
grpby_AccountInfoDetails1_RD_noa_monyy.index = grpby_AccountInfoDetails1_RD_noa_monyy.index.astype("str")
grpby_AccountInfoDetails1_RD_bookvalue_monyy.index = grpby_AccountInfoDetails1_RD_bookvalue_monyy.index.astype('str')
#--------FD-----------------------------------------------------------------------------------

AccountInfoDetails1_FD_temp = pd.DataFrame(AccountInfoDetails1.loc[(AccountInfoDetails1.MonthNam == last_value_ad[0]) & (AccountInfoDetails1.ProdGroup == "FD"),["TotalAccounts","EOPBalance"]].sum(0)).T
mtd_AccountInfoDetails1_FD_bookvalue =  str(round(float(AccountInfoDetails1_FD_temp.EOPBalance/10**7),2))
mtd_AccountInfoDetails1_FD_noa =  str(round(float(AccountInfoDetails1_FD_temp.TotalAccounts),2))

grpby_AccountInfoDetails1_FD_monyy = pd.DataFrame(AccountInfoDetails1.loc[AccountInfoDetails1.ProdGroup == "FD", ['EOPBalance','TotalAccounts']].groupby([AccountInfoDetails1['date']]).sum())
grpby_AccountInfoDetails1_FD_bookvalue_monyy = round(grpby_AccountInfoDetails1_FD_monyy.loc[:,["EOPBalance"]]/10**7,2)
grpby_AccountInfoDetails1_FD_noa_monyy = grpby_AccountInfoDetails1_FD_monyy.loc[:,["TotalAccounts"]]
grpby_AccountInfoDetails1_FD_noa_monyy.index = grpby_AccountInfoDetails1_FD_noa_monyy.index.astype("str")
grpby_AccountInfoDetails1_FD_bookvalue_monyy.index = grpby_AccountInfoDetails1_FD_bookvalue_monyy.index.astype("str")
#--------CA----------------------------------------------------------------------------------

AccountInfoDetails1_CA_temp = pd.DataFrame(AccountInfoDetails1.loc[(AccountInfoDetails1.MonthNam == last_value_ad[0]) & (AccountInfoDetails1.ProdGroup == "CA"),["TotalAccounts","EOPBalance"]].sum(0)).T
mtd_AccountInfoDetails1_CA_bookvalue =  str(round(float(AccountInfoDetails1_CA_temp.EOPBalance/10**7),2))
mtd_AccountInfoDetails1_CA_noa =  str(round(float(AccountInfoDetails1_CA_temp.TotalAccounts),2))

grpby_AccountInfoDetails1_CA_monyy = pd.DataFrame(AccountInfoDetails1.loc[AccountInfoDetails1.ProdGroup == "CA", ['EOPBalance','TotalAccounts']].groupby([AccountInfoDetails1['date']]).sum())
grpby_AccountInfoDetails1_CA_bookvalue_monyy = round(grpby_AccountInfoDetails1_CA_monyy.loc[:,["EOPBalance"]]/10**7,2)
grpby_AccountInfoDetails1_CA_noa_monyy = grpby_AccountInfoDetails1_CA_monyy.loc[:,["TotalAccounts"]]
grpby_AccountInfoDetails1_CA_noa_monyy.index = grpby_AccountInfoDetails1_CA_noa_monyy.index.astype("str")
grpby_AccountInfoDetails1_CA_bookvalue_monyy.index = grpby_AccountInfoDetails1_CA_bookvalue_monyy.index.astype("str")

#Standalone ----------------------------------------------------------------------------------

StandaloneCustomer_dt = change_date_string_date(StandaloneCustomer, dt_colname="YrMon_AsOnDate")
StandaloneCustomer1 = pd.concat([StandaloneCustomer.reset_index(drop=True),pd.DataFrame(StandaloneCustomer_dt)], axis=1)
StandaloneCustomer1.sort_values(by="date", inplace=True)
last_value_st = list(StandaloneCustomer1.tail(1)["YrMon_AsOnDate"])
mtd_StandaloneCustomer = StandaloneCustomer1.loc[StandaloneCustomer1.YrMon_AsOnDate == last_value_st[0], ["CustCount"]].sum(0)
mtd_StandaloneCustomer =  str(round(float(mtd_StandaloneCustomer),2))
grpby_StandaloneCustomer1_monyy = pd.DataFrame(StandaloneCustomer1['CustCount'].groupby([StandaloneCustomer1['date']]).sum())
grpby_StandaloneCustomer1_monyy.index = grpby_StandaloneCustomer1_monyy.index.astype("str")
#---SA-----------------------------------------------------------------------------------------

mtd_StandaloneCustomer_SA = StandaloneCustomer1.loc[(StandaloneCustomer1.YrMon_AsOnDate == last_value_st[0]) & (StandaloneCustomer1.ProdGroup=="SA"), ["CustCount"]].sum(0)
mtd_StandaloneCustomer_SA =  str(round(float(mtd_StandaloneCustomer_SA),2))
grpby_StandaloneCustomer1_SA_monyy = pd.DataFrame(StandaloneCustomer1.loc[StandaloneCustomer1.ProdGroup=="SA",['CustCount']].groupby([StandaloneCustomer1['date']]).sum())
grpby_StandaloneCustomer1_SA_monyy.index = grpby_StandaloneCustomer1_SA_monyy.index.astype("str")
#---RD--------------------------------

mtd_StandaloneCustomer_RD = StandaloneCustomer1.loc[(StandaloneCustomer1.YrMon_AsOnDate == last_value_st[0]) & (StandaloneCustomer1.ProdGroup=="RD"), ["CustCount"]].sum(0)
mtd_StandaloneCustomer_RD =  str(round(float(mtd_StandaloneCustomer_RD),2))
grpby_StandaloneCustomer1_RD_monyy = pd.DataFrame(StandaloneCustomer1.loc[StandaloneCustomer1.ProdGroup=="RD",['CustCount']].groupby([StandaloneCustomer1['date']]).sum())
grpby_StandaloneCustomer1_SA_monyy.index = grpby_StandaloneCustomer1_SA_monyy.index.astype("str")
#---CA--------------------------------

mtd_StandaloneCustomer_CA = StandaloneCustomer1.loc[(StandaloneCustomer1.YrMon_AsOnDate == last_value_st[0]) & (StandaloneCustomer1.ProdGroup=="CA"), ["CustCount"]].sum(0)
mtd_StandaloneCustomer_CA =  str(round(float(mtd_StandaloneCustomer_CA),2))
grpby_StandaloneCustomer1_CA_monyy = pd.DataFrame(StandaloneCustomer1.loc[StandaloneCustomer1.ProdGroup=="CA",['CustCount']].groupby([StandaloneCustomer1['date']]).sum())
grpby_StandaloneCustomer1_CA_monyy.index = grpby_StandaloneCustomer1_CA_monyy.index.astype("str")
#---FD--------------------------------

mtd_StandaloneCustomer_FD = StandaloneCustomer1.loc[(StandaloneCustomer1.YrMon_AsOnDate == last_value_st[0]) & (StandaloneCustomer1.ProdGroup=="FD"), ["CustCount"]].sum(0)
mtd_StandaloneCustomer_FD =  str(round(float(mtd_StandaloneCustomer_FD),2))
grpby_StandaloneCustomer1_FD_monyy = pd.DataFrame(StandaloneCustomer1.loc[StandaloneCustomer1.ProdGroup=="FD",['CustCount']].groupby([StandaloneCustomer1['date']]).sum())
grpby_StandaloneCustomer1_FD_monyy.index = grpby_StandaloneCustomer1_FD_monyy.index.astype("str")


#Channel--------------------------------------------------------------------------------------------
##Total Transactions--------------------------------------------------------------------------------
# FTM_ChannelTxn

FTM_ChannelTxn_dt = change_date_string_date(FTM_ChannelTxn, dt_colname="AS_ON_DATE_YrMon",delim="-")
FTM_ChannelTxn1 = pd.concat([FTM_ChannelTxn.reset_index(drop=True),pd.DataFrame(FTM_ChannelTxn_dt)], axis=1)
FTM_ChannelTxn1.sort_values(by="date", inplace=True)
last_value_tt = list(FTM_ChannelTxn1.tail(1)["AS_ON_DATE_YrMon"])
mtd_FTM_ChannelTxn = FTM_ChannelTxn1.loc[FTM_ChannelTxn1.AS_ON_DATE_YrMon == last_value_tt[0], ["TxnCount"]].sum(0)
mtd_FTM_ChannelTxn =  str(round(float(mtd_FTM_ChannelTxn),2))
grpby_mtd_FTM_ChannelTxn1_monyy = pd.DataFrame(FTM_ChannelTxn1['TxnCount'].groupby([FTM_ChannelTxn1['date']]).sum())
grpby_StandaloneCustomer1_FD_monyy.index = grpby_StandaloneCustomer1_FD_monyy.index.astype("str")

#Channel Mix----------------------------------------------------------------------------------------
FTM_ChannelTxn_dt = change_date_string_date(FTM_ChannelTxn, dt_colname="AS_ON_DATE_YrMon",delim="-")
FTM_ChannelTxn1 = pd.concat([FTM_ChannelTxn.reset_index(drop=True),pd.DataFrame(FTM_ChannelTxn_dt)], axis=1)
FTM_ChannelTxn1.sort_values(by="date", inplace=True)
last_value_tt = list(FTM_ChannelTxn1.tail(1)["AS_ON_DATE_YrMon"])

FTM_ChannelTxn_mix = pd.DataFrame(FTM_ChannelTxn1.loc[FTM_ChannelTxn1.AS_ON_DATE_YrMon == last_value_tt[0],"TxnCount"].groupby(FTM_ChannelTxn1["Channel"]).sum())
channel_indices = list(FTM_ChannelTxn_mix.index)
mtd_channel_dict = {items : str(float(FTM_ChannelTxn_mix[FTM_ChannelTxn_mix.index == items].sum(0))) for items in channel_indices}

grpby_mtd_FTM_ChannelTxn1_mix_monyy = FTM_ChannelTxn1.groupby(["date","Channel"]).sum()
grpby_mtd_FTM_ChannelTxn1_mix_monyy = grpby_mtd_FTM_ChannelTxn1_mix_monyy.loc[:, "TxnCount"]
grpby_mtd_FTM_ChannelTxn1_mix_monyy = grpby_mtd_FTM_ChannelTxn1_mix_monyy.reset_index().set_index("date")
grpby_mtd_FTM_ChannelTxn1_mix_monyy.index = grpby_mtd_FTM_ChannelTxn1_mix_monyy.index.astype("str")


#Added later for Transaction value hence there is a difference in logic
FTM_ChannelTxn_value_mix = pd.DataFrame(FTM_ChannelTxn1.loc[FTM_ChannelTxn1.AS_ON_DATE_YrMon == last_value_tt[0],"TxnValue"].groupby(FTM_ChannelTxn1["Channel"]).sum())
channel_indices = list(FTM_ChannelTxn_value_mix.index)
mtd_channel_value_dict = {items : str(round(float(FTM_ChannelTxn_value_mix[FTM_ChannelTxn_value_mix.index == items].sum(0))/10**7,2)) for items in channel_indices}

grpby_mtd_FTM_ChannelTxn1_mix_value_monyy = FTM_ChannelTxn1.groupby(["date","Channel"]).sum()
grpby_mtd_FTM_ChannelTxn1_mix_value_monyy = grpby_mtd_FTM_ChannelTxn1_mix_value_monyy.loc[:, "TxnValue"]
grpby_mtd_FTM_ChannelTxn1_mix_value_monyy = grpby_mtd_FTM_ChannelTxn1_mix_value_monyy.reset_index().set_index("date")
grpby_mtd_FTM_ChannelTxn1_mix_value_monyy.index = grpby_mtd_FTM_ChannelTxn1_mix_value_monyy.index.astype("str")
grpby_mtd_FTM_ChannelTxn1_mix_value_monyy.loc[:, "TxnValue"] = round(grpby_mtd_FTM_ChannelTxn1_mix_value_monyy.loc[:, "TxnValue"]/10**7,2)
#------------------------------------------------------------------------------------------------------------#
#--Transaction Failure Rate----------------------------------------------------------------------------------#
#ATMTxnFailure - It is clubbed with channel-mix but it is different as the values of channel corresponding to
# failure rate is as below
# OnUs -- Bank customer, Same Bank ATM
# OffUsAcq -- Bank Customer, Different Bank ATM
# RemoteOnUsIss -- Different Bank Customer, Same ATM
# FSS PG ECOM (Debit + PIN) -- Internal System
# ECOM -- Unable to understand
# IMPS Benificary -- Related to beneficiary IMPS transfer
# IMPS Remitter -- Related to sender IMPS transfer
#-------------------------------------------------------------------------------------------------------------#
ATMTxnFailure_dt =  change_date_string_date(ATMTxnFailure, dt_colname="DateMonNam",delim=" ")
ATMTxnFailure1 = pd.concat([ATMTxnFailure.reset_index(drop=True),pd.DataFrame(ATMTxnFailure_dt)], axis=1)
ATMTxnFailure1.sort_values(by="date", inplace=True)
last_value_tf = list(ATMTxnFailure1.tail(1)["DateMonNam"])

ATMTxnFailure1_mix = pd.DataFrame(ATMTxnFailure1.loc[ATMTxnFailure1.DateMonNam == last_value_tf[0],"Amount"].groupby(ATMTxnFailure1["OnOff_FLag"]).sum())
flag_indices = list(ATMTxnFailure1_mix.index)
mtd_flag_dict = {items : str(float(ATMTxnFailure1_mix[ATMTxnFailure1_mix.index == items].sum(0))) for items in flag_indices}



def strip_upper(x):
    x = x.upper()
    return x.strip()

#-------------Pandas Processing-End---------------------------------------------#

def mor_eve_aftnoon():
    time_now = datetime.now()
    now = datetime.now()
    if (time_now < now.replace(hour=12,minute=0, second=0, microsecond=0)):
        return "Good Morning !!!"
    elif (now.replace(hour=15,minute=0, second=0, microsecond=0) >= time_now \
    >= now.replace(hour=12,minute=0, second=0, microsecond=0)):
        return "Good Afternoon !!!"
    else:
        return "Good Evening !!!"

#-----------------------#
# Template of functions #
#-----------------------#

# ----------------------------------------------#
# final caller      -->      dependent function
# ==============================================#
# get_updates --> json_from_url --> get_the_url
# get_last_update_id
# response_all --> send_message
# ----------------------------------------------#
#Buildiing the keyboard

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


#get the first alphabet of a string and concatenates them
def first_letter(string):
    if len(string.split(" ")) == 3:
        value = re.match("(\w+)\s(\w+)\s(\w+)", string)
        return "".join(out[0] for out in value.groups())
    else:
        value = string
        return string

#getting the url response
def get_the_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

#loading the json which we recieved from url
def json_from_url(url):
    content = get_the_url(url)
    js = json.loads(content)
    return js

#getting the updates
def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    jsonout = json_from_url(url)
    return jsonout

#print(get_updates(offset=None))
#ids = get_updates(offset=None)["result"][0]["message"]["chat"]["id"]
#first_name = get_updates(offset=None)["result"][0]["message"]["chat"]["first_name"]
#last_name = get_updates(offset=None)["result"][0]["message"]["chat"]["last_name"]

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

#sending messages
def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    if chat_id in approve_ids: ##checking for valid ids
        get_the_url(url)

months_choices = []
for i in range(1,13):
    months_choices.append(datetime(2017, i, 1).strftime('%b'))

#(c-p)/c*100

def find_word(text_to_be_searched_in, word_to_be_matched):
   result = re.findall('\\b'+text_to_be_searched_in+'\\b', word_to_be_matched, flags=re.IGNORECASE)
   if len(result)>0:
      return True
   else:
      return False
###Dictinaories to fetch data from: MTD, YTD etc - banks.

list_of_banks_vars = ["totalaccounts", "EOPBalance", "AvgMTLBalnce", "NewCust", "IPFlag_percentage","ActiveCust", "CashBalnces" ]
list_views = ["MTD", "FYTD"]

newitems=[]
for items in list_of_banks_vars:
    for list_v in list_views:
        values = list_v.lower() + "_" + items
        newitems.append(values)

mydict_all_views = dict()

for items in newitems:
    mydict_all_views[items] = eval(items)


#Dicts for monyy - banks
#This can't be shortened as the keys given manually, however values is taken from dataframe inputs of csvs

dicts_banks = dict()
dicts_banks["total accounts"] = "TotalAccounts"
dicts_banks["book value"] = "EOPBalance"
dicts_banks["amb"] = "AvgMTLBalnce"
dicts_banks["new customers"] = "CustCount"
dicts_banks["ip funding"] = "percentage"
dicts_banks["active clients"] = "percentage"
dicts_banks["cash day end balance"] = "DayEndBal"

monyy_list_banks = []
for items in list(dicts_banks.keys()):
    for item in months_choices:
        monyy_list_banks.append(items + " " + item.lower())

banks_list_for_monyy = []
for item in months_choices:
    banks_list_for_monyy.append("bank" + " " + item.lower())

##PRODUCTS

PRODUCTS = ["SA", "RD", "FD", "CA"]
list_of_products_mnths = []
for prod in PRODUCTS:
    for item in months_choices:
        list_of_products_mnths.append(prod.lower() + " " + item.lower())

#Channel
CHANNEL = ["CHANNEL-MIX", "%TRANSACTION FAILURE RATE"]
list_of_channel_mnths=[]
for chnl in CHANNEL:
    for item in months_choices:
        list_of_channel_mnths.append(chnl.lower() + " " + item.lower())

#list_of_channel_mnths[0:12]
#Branch
BRANCH = list_of_branches
list_of_branches_mnths=[]
for brnch in BRANCH:
    for item in months_choices:
        list_of_branches_mnths.append(brnch.lower() + " " + item.lower())


def find_word_in_list(lyst=["a", "b", "c"], word ="a"):
    for item in lyst:
        if item == word:
            return True
        return False

#find_word_in_list(lyst=["mtd-cbd belapur"], word = "cbd belapur")

##-----------------------------------------------------------------------------------------------------
def response_all(updates):
    for update in updates["result"]:
        #text = "This is what I am returning" # This is working
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        global branch

        if text in  list_of_branches:
            branch = text.upper()

        if any(find_word(text.lower(), greet) for greet in [out.lower() for out in GREETINGS]) or text.lower() == "back":
            send_message(random.choice(GREETINGS) +", " + get_updates(offset=None)["result"][0]["message"]["chat"]["first_name"].title() + " " + mor_eve_aftnoon() , chat)
            keyboard = build_keyboard(["Bank", "Branch", "Product", "Channel"])
            send_message("Select the appropriate or type it on your device: ",chat, keyboard)

        elif text.lower() == "main menu":
            keyboard = build_keyboard(["Bank", "Branch", "Product", "Channel"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif text.lower() == "start":
            send_message("Hi", chat)
        #Banks
        elif text.lower() == "bank" :
            send_message("The below values are business done on yesterday and it is the default value", chat)
            send_message("Total Accounts(#) on yesterday is : "+ str(round(float(mtd_totalaccounts) - float(mtd_yesterday["mtd_totalaccounts"]),2)),chat)
            send_message("Total Book Value(Cr.) on yesterday is : "+ str(round(float(mtd_EOPBalance) - float(mtd_yesterday["mtd_EOPBalance"]),2)),chat)
            send_message("The AMB(Cr.) on yesterday is : "+ str(round((float(mtd_AvgMTLBalnce) - float(mtd_yesterday["mtd_AvgMTLBalnce"]))/float(mtd_yesterday["mtd_AvgMTLBalnce"]),2)),chat)
            #send_message("The New Customers on yesterday is : "+ "value",chat)
            send_message("The %IP Funding, on yesterday is : "+ mtd_yesterday["mtd_IPFlag_percentage"],chat)
            send_message("The % Active Clients on yesterday is : " + mtd_yesterday["mtd_ActiveCust"],chat)
            send_message("The Cash Day End Balance(Cr.) on yesterday is : "+ str(round(float(mtd_CashBalnces) -  float(mtd_yesterday["mtd_CashBalnces"]),2)) ,chat)
            keyboard = build_keyboard([ "Main Menu", "MTD", "FYTD"])
            #send_message("Please select the appropriate option: ", chat, keyboard)
            send_message("Please choose anyone from below or In case if you want to fetch values for a particular month, type 'bank mon yyyy'\
e.g. bank apr 2017 to get April 2017 business values", chat, keyboard)

        elif text.lower() == "bank menu":
            keyboard = build_keyboard([ "Main Menu", "MTD", "FYTD"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif find_word_in_list(lyst=list_views, word= text.upper()) : ##Here comparing with the MTD, YTD, WTD etc
            send_message("The Number of Accounts(#) " + text.upper() + " is: " + mydict_all_views[text.lower() + "_totalaccounts"] , chat)
            send_message("The Book Value(Cr.) for the " + text.upper() + " is: " + mydict_all_views[text.lower() + "_EOPBalance"], chat)
            send_message("The AMB(Cr.) for the " + text.upper() + " is: " + mydict_all_views[text.lower() + "_AvgMTLBalnce"], chat)
            send_message("The " + text.upper() + " for new customers(#) is: " + mydict_all_views[text.lower() + "_NewCust"], chat)
            send_message("The " + text.upper() + " for %IP funding is: " + mydict_all_views[text.lower() + "_IPFlag_percentage" ], chat)
            send_message("The " + text.upper() + " % of active clients is: " + mydict_all_views[text.lower() +"_ActiveCust"] , chat)
            send_message("The " + text.upper() + " for cash balance(Cr.) is: " +  mydict_all_views[text.lower() + "_CashBalnces"], chat)
            keyboard = build_keyboard(["Bank Menu", "Main Menu"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif " ".join(text.lower().split(" ")[:-1]) in banks_list_for_monyy : #monyy
            send_message("The number(#) of active accounts for the month of " + " ".join(text.lower().split(" ")[:-2]) + " is "  + extract_info(df_monyy, key= "TotalAccounts", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The Book Value(Cr.) for the month of " + " ".join(text.lower().split(" ")[:-2]) + " is "  + extract_info(df_monyy, key= "EOPBalance", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The AMB(Cr.) for the month of " + " ".join(text.lower().split(" ")[:-2]) + " is "  + extract_info(df_monyy, key= "AvgMTLBalnce", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The new customer(#) count for the month of ", " ".join(text.lower().split(" ")[:-2])+ extract_info(grpby_NewCust_monyy, key= "CustCount", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) , chat )
            send_message("The %IP Funding for the month of " + " ".join(text.lower().split(" ")[:-2]) + " is "  + extract_info(grpby_NewCust_monyy_concat, key= "percentage", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The %Active clients for the month of " + " ".join(text.lower().split(" ")[:-2]) + " is "  + extract_info(grpby_ActiveCust1_monyy, key= "percentage", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The cash balances(Cr.) for the month of " + " ".join(text.lower().split(" ")[:-2]) + " is "  + extract_info(grpby_cash_balances_monyy, key= "DayEndBal", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            keyboard = build_keyboard(["Bank Menu","Main Menu"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        #Products
        elif text.lower() in ("product", "products menu", "products"):
            keyboard = build_keyboard(PRODUCTS + ["Main Menu"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif any([find_word(text.lower(), products) for products in [out.lower() for out in PRODUCTS]]): #start
            send_message("The below values are business done on yesterday and it is the default value", chat)
            send_message("#Accounts for " + text +" on yesterday is : "+ str(float(eval("mtd_AccountInfoDetails1_" +text.upper()+"_noa")) - float(mtd_yesterday["mtd_AccountInfoDetails1_"+ text.upper()+"_noa"])),chat)
            send_message("Book Value(Cr.) for " + text +" on yesterday is : "+ str(round(float(eval("mtd_AccountInfoDetails1_" +text.upper()+"_bookvalue")) - float(mtd_yesterday["mtd_AccountInfoDetails1_"+ text.upper()+"_bookvalue"]),2)),chat)
            send_message("Standalone value(Cr.) for " + text +" on yesterday is : "+ str(float(eval("mtd_StandaloneCustomer_" + text.upper())) - float(mtd_yesterday["mtd_StandaloneCustomer_"+text.upper()])),chat)
            keyboard = build_keyboard([(item + "-" + text.upper() ) for item in list_views] + ["Products Menu", "Main Menu"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif text.lower() in  " ".join( [(views.lower() + "-" + products.lower()) for products in PRODUCTS for views in list_views] ).lower(): #mtd,ytd etc
            send_message("#Accounts for " + text.upper().split("-")[0] + " is: " + eval(text.lower().split("-")[0]+"_AccountInfoDetails1_"+text.upper().split("-")[1]+"_noa"), chat)
            send_message("Book Value (Cr.) for "+ text.upper().split("-")[0] + " is: " + eval(text.lower().split("-")[0]+"_AccountInfoDetails1_"+ text.upper().split("-")[1] + "_bookvalue"), chat)
            send_message("Standalone value (Cr.) for  "+ text.upper().split("-")[0] + " is: " + eval(text.lower().split("-")[0]+"_StandaloneCustomer_" + text.upper().split("-")[1]), chat)
            keyboard = build_keyboard(["Products Menu","Main Menu"] + [(views.upper() + "-" + products.upper()) for products in PRODUCTS for views in list_views ])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif " ".join(text.lower().split(" ")[:-1]) in (list_of_products_mnths): #monyy
            send_message("#Accounts for " + " ".join(text.lower().split(" ")[-2:])  + " is: " + extract_info(eval("grpby_AccountInfoDetails1_" + text.upper().split(" ")[0] + "_noa_monyy"), key="TotalAccounts", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("Book Value (Cr.) for " + " ".join(text.lower().split(" ")[-2:])  + " is: " + extract_info(eval("grpby_AccountInfoDetails1_" +text.upper().split(" ")[0] + "_bookvalue_monyy"), key="EOPBalance", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("Standalone value(Cr.) for " + " ".join(text.lower().split(" ")[-2:])  + " is: "+ extract_info(eval("grpby_StandaloneCustomer1_" + text.upper().split(" ")[0] + "_monyy"), key="CustCount", value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) , chat)
            keyboard = build_keyboard(["Products Menu","Main Menu"])
            send_message("Please choose anyone or In case if you want to fetch values for a particular month, type 'product mon yyyy'\
e.g. sa apr 2017 to get April 2017 business values for Savings Account", chat, keyboard)

        #channel, here need to add %total failure and amount as well
        elif text.lower() == "channel" or text.lower() == "channel menu":
            keyboard = build_keyboard(["Channel-Mix", "%Transaction Failure Rate"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif text.lower() == "channel-mix":
            send_message("The below values are business done on yesterday and it is the default value", chat)
            send_message("Yesterday total transactions(#) for ATM is: " + str(float(mtd_channel_dict["ATM"]) - float(mtd_yesterday["mtd_channel_dict"]["ATM"])) + " with a value(Cr.) of " + str(round(float(mtd_channel_value_dict["ATM"]) - float(mtd_yesterday["mtd_channel_value_dict"]["ATM"]),2)) , chat)
            send_message("Yesterday total transactions(#) for POS is: " + str(float(mtd_channel_dict["Branch Banking"]) - float(mtd_yesterday["mtd_channel_dict"]["Branch Banking"])) + " with a value(Cr.) of " + str(round(float(mtd_channel_value_dict["Branch Banking"]) - float(mtd_yesterday["mtd_channel_value_dict"]["Branch Banking"]),2)), chat)
            send_message("Yesterday total transactions(#) for Internet Banking is: " + str(float(mtd_channel_dict["Internet Banking"]) - float(mtd_yesterday["mtd_channel_dict"]["Internet Banking"])) + " with a value(Cr.) of " + str(round(float(mtd_channel_value_dict["Internet Banking"]) - float(mtd_yesterday["mtd_channel_value_dict"]["Internet Banking"]),2)), chat)
            send_message("Yesterday total transactions(#) for Branch Banking is: " + str(float(mtd_channel_dict["Mobile Banking"]) - float(mtd_yesterday["mtd_channel_dict"]["Mobile Banking"])) + " with a value(Cr.) of " + str(round(float(mtd_channel_value_dict["Mobile Banking"]) - float(mtd_yesterday["mtd_channel_value_dict"]["Mobile Banking"]),2)), chat)
            send_message("Yesterday total transactions(#) for Mobile Banking is: " + str(float(mtd_channel_dict["POS"]) - float(mtd_yesterday["mtd_channel_dict"]["POS"])) + " with a value(Cr.) of " +  str(round(float(mtd_channel_value_dict["POS"]) - float(mtd_yesterday["mtd_channel_value_dict"]["POS"]),2)) , chat)
            keyboard = build_keyboard([(item + "-" + text.upper()) for item in list_views]+["Channel Menu", "Main Menu"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif text.lower() == "%transaction failure rate":
            send_message("This is under development", chat)
            keyboard = build_keyboard(["Channel Menu","Main Menu"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        ##channel is used as channel[0] due to the fact that sub categories(atm, pos, internet banking etc) are differnt
        elif text.lower() in " ".join([(views.lower() + "-" + channel.lower()) for channel in [CHANNEL[0]] for views in list_views] ).lower(): #MTD, YTD
            send_message(text.upper().split("-")[0] + " transactions(#) for "+ "for ATM is: " +  eval(text.lower().split("-")[0] + "_channel_dict")["ATM"] + " with a value(Cr.) of " + eval(text.lower().split("-")[0] + "_channel_value_dict")["ATM"], chat)
            send_message(text.upper().split("-")[0] + " transactions(#) for "+ "for POS is: " + eval(text.lower().split("-")[0] + "_channel_dict")["POS"] + " with a value(Cr.) of "+ eval(text.lower().split("-")[0] + "_channel_value_dict")["POS"], chat)
            send_message(text.upper().split("-")[0] + " transactions(#) for "+ "for Internet Banking is: " + eval(text.lower().split("-")[0] + "_channel_dict")["Internet Banking"] + " with a value(Cr.) of " + eval(text.lower().split("-")[0] + "_channel_value_dict")["Internet Banking"], chat)
            send_message(text.upper().split("-")[0] + " transactions(#) for "+ "for Branch Banking is: " + eval(text.lower().split("-")[0] + "_channel_dict")["Branch Banking"] + " with a value(Cr.) of " + eval(text.lower().split("-")[0] + "_channel_value_dict")["Branch Banking"], chat)
            #Add None for Branch Banking in case of %Transaction failure
            send_message("The " + text.upper().split("-")[0] + " value of "+ "-".join(text.lower().split("-")[1:]) +"(#) for Mobile Banking " + " is: " + eval(text.lower().split("-")[0] + "_channel_dict")["Mobile Banking"] + " with a value(Cr.) of " + eval(text.lower().split("-")[0] + "_channel_value_dict")["Mobile Banking"], chat)
            keyboard = build_keyboard(["Channel Menu","Main Menu"])
            send_message("Please select the appropriate option: ", chat, keyboard)

        ##channel is used as channel[0] due to the fact that sub categories(atm, pos, internet banking etc) are differnt
        # elif text.lower() in " ".join([(views.lower() + "-" + channel.lower()) for channel in [CHANNEL[1]] for views in list_views] ).lower(): #MTD, YTD
        #     send_message("The " + text.upper().split("-")[0] + " value of "+ "-".join(text.lower().split("-")[1:]) +"(#) for ATM " + " is: " +  eval(text.lower().split("-")[0] + "channel_dict")["ATM"], chat)
        #     send_message("The " + text.upper().split("-")[0] + " value of "+ "-".join(text.lower().split("-")[1:]) +"(#) for POS " + " is: " + eval(text.lower().split("-")[0] + "channel_dict")["POS"], chat)
        #     send_message("The " + text.upper().split("-")[0] + " value of "+ "-".join(text.lower().split("-")[1:]) +"(#) for Internet Banking " + " is: " + eval(text.lower().split("-")[0] + "channel_dict")["Internet Banking"], chat)
        #     send_message("The " + text.upper().split("-")[0] + " value of "+ "-".join(text.lower().split("-")[1:]) +"(#) for Branch Banking " + " is: " + eval(text.lower().split("-")[0] + "channel_dict")["Branch Banking"], chat)
        #     #Add None for Branch Banking in case of %Transaction failure
        #     send_message("The " + text.upper().split("-")[0] + " value of "+ "-".join(text.lower().split("-")[1:]) +"(#) for Mobile Banking " + " is: " + eval(text.lower().split("-")[0] + "channel_dict")["Mobile Banking"], chat)
        #     keyboard = build_keyboard(["Channel Menu","Main Menu"])
        #     send_message("Please select the appropriate option: ", chat, keyboard)

        elif " ".join(text.lower().split(" ")[:-1]) in  (list_of_channel_mnths[0:12]): #monyy for channel-mix grpby_mtd_FTM_ChannelTxn1_mix_value_monyy
            send_message( "For the month " + " ".join(text.lower().split(" ")[-2:]) + " #Accounts for ATM channel is "  + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="ATM",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) + " and business value(Cr.) is  " +  extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_value_monyy, key="TxnValue",groups="Channel",grp_value="ATM",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message( "For the month " + " ".join(text.lower().split(" ")[-2:]) + " #Accounts for POS channel is " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="POS",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) + " and business value(Cr.) is  " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_value_monyy, key="TxnValue",groups="Channel",grp_value="POS",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message( "For the month " + " ".join(text.lower().split(" ")[-2:]) + " #Accounts for Internet Banking is " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="Internet Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) + " and business value(Cr.) is  " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_value_monyy, key="TxnValue",groups="Channel",grp_value="Internet Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message( "For the month " + " ".join(text.lower().split(" ")[-2:]) + " #Accounts for Branch Banking is " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="Branch Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) + " and business value(Cr.) is  " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_value_monyy, key="TxnValue",groups="Channel",grp_value="Branch Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message( "For the month " + " ".join(text.lower().split(" ")[-2:]) + " #Accounts for Mobile Banking is " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="Mobile Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) + " and business value(Cr.) is  " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_value_monyy, key="TxnValue",groups="Channel",grp_value="Mobile Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            keyboard = build_keyboard(["Channel Menu","Main Menu"])
            send_message("Please choose anyone or In case if you want to fetch values for a particular month, type 'channel mon yyyy'\
e.g. channel-mix sep 2017 to get September 2017 business values", chat, keyboard)

        # elif " ".join(text.lower().split(" ")[:-1]) in  (list_of_channel_mnths[12:]): #monyy for cf %transaction failure
        #     send_message("#Accounts for " + " ".join(text.lower().split(" ")[-2:]) + " for ATM is: " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="ATM",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
        #     send_message("#Accounts for " + " ".join(text.lower().split(" ")[-2:]) + " for POS is: " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="POS",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
        #     send_message("#Accounts for " + " ".join(text.lower().split(" ")[-2:]) + " for Internet Banking is: " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="Internet Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
        #     send_message("#Accounts for " + " ".join(text.lower().split(" ")[-2:]) + " for Branch Banking is: " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="Branch Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
        #     send_message("#Accounts for " + " ".join(text.lower().split(" ")[-2:]) + " for Mobile Banking " + extract_info_with_grps(grpby_mtd_FTM_ChannelTxn1_mix_monyy, key="TxnCount",groups="Channel",grp_value="Mobile Banking",  value=outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
        #     keyboard = build_keyboard(["Channel Menu","Main Menu"])
        #     send_message("Please choose anyone or In case if you want to fetch values for a particular month, type 'channel mon yyyy'\
        #     e.g. %transaction failure rate apr 2017 to get April 2017 business values", chat, keyboard)

        elif text.lower() in ("branch","branch menu"):
            keyboard = build_keyboard(list_of_branches)
            send_message("Please select the appropriate option: ", chat, keyboard)
        #Branches

        elif text in  list_of_branches:
            send_message("The below values are business done on yesterday and it is the default value", chat)
            send_message("Total accounts(#) on yesterday is : "+ str(float(mtd_branch_account_dict[text]) - float(mtd_yesterday["mtd_branch_account_dict"][text])),chat)
            send_message("Total Book Value(Cr.) on yesterday is : "+ str(round(float(mtd_branch_eop_dict[text]) - float(mtd_yesterday["mtd_branch_eop_dict"][text]),2)) ,chat)
            send_message("The AMB(Cr.) on yesterday is : "+ str(round((float(mtd_branch_amb_dict[text]) - float(mtd_yesterday["mtd_branch_amb_dict"][text]))/float(mtd_yesterday["mtd_branch_amb_dict"][text]),2)),chat)
            #send_message("The New Customers on yesterday is : "+ str(mtd_NewCust_branch_mix[mtd_NewCust_branch_mix.index == text.split("-")[1].upper()].sum() - mtd_yesterday["mtd_NewCust_branch_mix"][mtd_yesterday["mtd_NewCust_branch_mix"].index == text.split("-")[1].upper()].sum()),chat)
            send_message("The % Active Clients on yesterday is : " + str(round(float(mtd_yesterday["mtd_ActiveCust_branch_temp"][mtd_yesterday["mtd_ActiveCust_branch_temp"].index == text]),2)) + "%",chat)
            send_message("The Cash Day End Balance(Cr.) on yesterday is : "+ str(round(float(mtd_yesterday["mtd_CashBalnces_branch_mix"].loc[mtd_yesterday["mtd_CashBalnces_branch_mix"].index == text,"DayEndBal"].sum()),2)),chat)
            keyboard = build_keyboard([ "Main Menu", "Branch Menu"]+[views.upper() + "-"+text.upper() for views in list_views])
            send_message("Please select the appropriate option: ", chat, keyboard)
        #text.lower() in " ".join([(views.lower() + "-" + branches.lower()) for branches in list_of_branches for views in list_views] )
        elif find_word_in_list(lyst=[(views.lower() + "-" + branches.lower()) for branches in list_of_branches for views in list_views], word = text.lower()):
            send_message("Total "+ text.split("-")[0] + " Accounts(#) for - " + text.split("-")[1] + " is: " + eval( text.lower().split("-")[0] +'_branch_account_dict[text.split("-")[1].upper()]') , chat )
            send_message("Total "+ text.split("-")[0] + " Book Value(Cr.) for -" + text.split("-")[1] + " is: " + eval( text.lower().split("-")[0] + '_branch_eop_dict[text.split("-")[1].upper()]'),chat)
            send_message("Total "+ text.split("-")[0] + " AMB(Cr.) for - " + text.split("-")[1] + " is: " + eval( text.lower().split("-")[0] + '_branch_amb_dict[text.split("-")[1].upper()]'),chat)
            send_message( text.split("-")[0] + " New Customers(#) for - "+ text.split("-")[1] + " is: " + str(float(eval( text.lower().split("-")[0] + '_NewCust_branch_mix[mtd_NewCust_branch_mix.index == text.split("-")[1].upper()]'))),chat)
            send_message( text.split("-")[0] + " % Active Clients for - " + text.split("-")[1] + " " + str(float(eval( text.lower().split("-")[0] + '_ActiveCust_branch_temp[mtd_ActiveCust_branch_temp.index == text.split("-")[1].upper()]'))) + "%" ,chat)
            send_message( text.split("-")[0] + " Cash Day End Balance(Cr.) for - "+ text.split("-")[1]+ " " + str(round(float(eval( text.lower().split("-")[0] + '_CashBalnces_branch_mix.loc[mtd_CashBalnces_branch_mix.index == text.split("-")[1].upper(),"DayEndBal"]').sum()),2)),chat)
            keyboard = build_keyboard([ "Main Menu", "Branch Menu"]+[views.upper() + "-"+text.upper().split("-")[-1] for views in list_views])
            send_message("Please select the appropriate option: ", chat, keyboard)

        elif " ".join(text.lower().split(" ")[:-1]) in  list_of_branches_mnths: #monyy, there is no point of fytd
            send_message("Total Accounts(#) on " + " ".join(text.lower().split(" ")[-2:]) + " is : " + extract_info_with_grps(grpby_mtd_AccountInfoDetaisl_branch_mix_monyy, key="TotalAccounts",groups="BRNCH_NME",grp_value=branch,  value= outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("Total Book Value(Cr.) on " + " ".join(text.lower().split(" ")[-2:]) + " is : " + extract_info_with_grps(grpby_mtd_AccountInfoDetaisl_branch_mix_monyy, key="EOPBalance",groups="BRNCH_NME",grp_value=branch,  value= outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The AMB(Cr.) on " + " ".join(text.lower().split(" ")[-2:]) + " is : " + extract_info_with_grps(grpby_mtd_AccountInfoDetaisl_branch_mix_monyy, key="AvgMTLBalnce",groups="BRNCH_NME",grp_value=branch,  value= outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The New Customers(#) on " + " ".join(text.lower().split(" ")[-2:]) + " is : " + extract_info_with_grps(NewCust_branch_mix_monyy, key="CustCount",groups="BRNCH_NME",grp_value=branch,  value= outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            send_message("The % Active Clients on " + " ".join(text.lower().split(" ")[-2:]) + " is : " + extract_info_with_grps(grpby_ActiveCust1_branch_monyy, key="percentage",groups="BRNCH_NME",grp_value=branch,  value= outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))) + "%", chat)
            send_message("The Cash Day End Balance(Cr.) on " + " ".join(text.lower().split(" ")[-2:]) + " is : " + extract_info_with_grps(grpby_cash_balances_branch_monyy, key="DayEndBal",groups="BRNCH_NME",grp_value=branch,  value= outcome_monthyr(" ".join(text.lower().split(" ")[-2:]))), chat)
            keyboard = build_keyboard([ "Main Menu", "Branch Menu"] + [views.upper() + "-"+text.upper() for views in list_views])
            send_message("Please choose anyone or In case if you want to fetch values for a particular month, type 'branch mon yyyy'\
e.g. cbd belapur apr 2017 to get April 2017 business values", chat, keyboard)

        else:
            send_message("Please type your options, In case in doubt type 'Hi' to got main menu:",chat) ##send_message

        # return None

##For tomorrow
##copying the present data into a namespace called mtd_today
##Here only copying is done of today's data

val = re.findall("mtd_\w+", " ".join(vars().keys()))
mtd_today = dict()

for item in val:
    try:
        mtd_today[item] = eval(item)
    except (NameError, KeyError) as e:
        pass
'''
In case anyone want to save every data point everyday, then comment the below
line, however it will make the pickle  file hugh over the period of time
'''
mtd_today["mtd_yesterday"]=None
with open("mtd_yesterday_"+datetime.strftime(date.today(), "%Y%b%d")+".pickle","wb") as pkl:
    pickle.dump(mtd_today, pkl)


def main():
    ###For tomorrow---------------------------------------------------------------------------------------

    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            response_all(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
