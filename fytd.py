
import pandas as pd
from datetime import datetime, date
import re
import os
#import numpy as np

PATH = r"C:\Users\pradeep4.kumar\Downloads\telegrambot\data_new_bot"
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

# df_final.columns = [c.replace(' ', '_') for c in df_final.columns]


def change_date_string_date(dframe,dt_colname=None,delim=" "):
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


###fYTD LOGIC-------------------------------------------------------------------------------

def get_the_date_fytd(dframe=None ):
    if date.today().month in (1,2,3):
        range_year_min = date( date.today().year-1,4,1)
        range_year_max = date(date.today(),3,31)
        final_value = dframe.loc[(range_year_max >= dframe.date) & ( dframe.date >= range_year_min),:]
    else:
        range_year_min = date(date.today().year, 4, 1)
        range_year_max = date(date.today().year+1,3,31)
        final_value = dframe.loc[(range_year_max >= dframe.date) & ( dframe.date >= range_year_min),:]
    return final_value


###For Banks Menu---------------------------------------------------------------------------
#Total Acc, AMB, BookValue------------------------------------------------------------------


AccountInfoBank_dt = change_date_string_date(AccountInfoBank, dt_colname="MonthNam")
AccountInfoBank1 = pd.concat([AccountInfoBank.reset_index(drop=True),pd.DataFrame(AccountInfoBank_dt)], axis=1)
AccountInfoBank1.sort_values(by="date", inplace=True)
AccountInfoBank1_fytd = get_the_date_fytd(dframe=AccountInfoBank1)

fytd_totalaccounts = str(float(AccountInfoBank1_fytd.TotalAccounts.sum(0)))
fytd_EOPBalance = str(round(float(AccountInfoBank1_fytd.EOPBalance.sum(0)/(10**7)),2))
fytd_AvgMTLBalnce = str(round(float(AccountInfoBank1_fytd.AvgMTLBalnce.sum(0)/(10**7)),2))

# df_monyy_fytd = AccountInfoBank1_fytd.loc[:,["date", "TotalAccounts", "EOPBalance", "AvgMTLBalnce"]]
# df_monyy_fytd = df_monyy_fytd.set_index(df_monyy_fytd.date.astype("str")).loc[:,["TotalAccounts", "EOPBalance", "AvgMTLBalnce" ]]

#NewCust---------------------------------------------------------------------------------------

NewCust_dt = change_date_string_date(NewCust, dt_colname="AsOnYrMonName")
NewCust1 = pd.concat([NewCust.reset_index(drop=True),pd.DataFrame(NewCust_dt)], axis=1)
NewCust1.sort_values(by="date", inplace=True)
NewCust1_fytd = get_the_date_fytd(dframe=NewCust1)

fytd_NewCust = str(round(float(NewCust1_fytd.loc[:, "CustCount"].sum(0)),2))

#grpby_NewCust_monyy_fytd = pd.DataFrame(NewCust1_fytd['CustCount'].groupby([NewCust1_fytd['date']]).sum())
# grpby_NewCust_monyy_fytd.index = grpby_NewCust_monyy_fytd.index.astype("str")


#----------------------------------------------------------------------------------------------
#IPFlag---------------------------------------------------------------------------------------
IPFlag_0 = IPFlag.loc[IPFlag.IPFlag == 0, :]
IPFlag_1 = IPFlag.loc[IPFlag.IPFlag == 1, :]
IPFlag_0_dt = change_date_string_date(IPFlag_0, dt_colname="YrMon_Acc_Opn_Date")
IPFlag_01 = pd.concat([IPFlag_0.reset_index(drop=True),pd.DataFrame(IPFlag_0_dt)], axis=1)
IPFlag_01.sort_values(by="date", inplace=True)
IPFlag_01_fytd = get_the_date_fytd(dframe=IPFlag_01)

IPFlag_1_dt = change_date_string_date(IPFlag_1, dt_colname="YrMon_Acc_Opn_Date")
IPFlag_11 = pd.concat([IPFlag_1.reset_index(drop=True),pd.DataFrame(IPFlag_1_dt)], axis=1)
IPFlag_11.sort_values(by="date", inplace=True)
IPFlag_11_fytd = get_the_date_fytd(dframe=IPFlag_11)

last_value_ip_0 = list(IPFlag_01_fytd.tail(1)["date"])
last_value_ip_1 = list(IPFlag_11_fytd.tail(1)["date"])

if last_value_ip_1[0] < last_value_ip_0[0]:
    last_value_ip_0 = list(IPFlag_11_fytd.tail(1)["YrMon_Acc_Opn_Date"])
    last_value_ip_1 = list(IPFlag_11_fytd.tail(1)["YrMon_Acc_Opn_Date"])
elif last_value_ip_1[0] > last_value_ip_0[0]:
    last_value_ip_0 = list(IPFlag_01_fytd.tail(1)["YrMon_Acc_Opn_Date"])
    last_value_ip_1 = list(IPFlag_01_fytd.tail(1)["YrMon_Acc_Opn_Date"])
else:
    last_value_ip_0 = list(IPFlag_01_fytd.tail(1)["YrMon_Acc_Opn_Date"])
    last_value_ip_1 = list(IPFlag_11_fytd.tail(1)["YrMon_Acc_Opn_Date"])

#The above logic is not incorporated for fytd
fytd_IPFlag_11 = float(IPFlag_11_fytd.loc[:, "Count(ACCT_NBR)"].sum(0))
fytd_IPFlag_01 = float(IPFlag_01_fytd.loc[:, "Count(ACCT_NBR)"].sum(0))

fytd_IPFlag_percentage = str(round(fytd_IPFlag_11/(fytd_IPFlag_01+fytd_IPFlag_11),2)*100) + "%"


#----------------------------------------------------------------------------------------------
#CashBalnces----------------------------------------------------------------------------------

cashbalances_dt = change_date_string_date(CashBalnces, dt_colname="YrMon")
CashBalnces1 = pd.concat([CashBalnces.reset_index(drop=True),pd.DataFrame(cashbalances_dt)], axis=1)
CashBalnces1.sort_values(by="date", inplace=True)
CashBalnces1_fytd = get_the_date_fytd(dframe=CashBalnces1)

fytd_CashBalnces = str(round(float(CashBalnces1_fytd.loc[:, "DayEndBal"].sum(0)/10**7),2))

#----------------------------------------------------------------------------------------------


#Active Customers------------------------------------------------------------------------------

ActiveCust_dt = change_date_string_date(ActiveCust, dt_colname="YrMon_AsOnDate")
ActiveCust1 = pd.concat([ActiveCust.reset_index(drop=True),pd.DataFrame(ActiveCust_dt)], axis=1)
ActiveCust1.sort_values(by="date", inplace=True)
ActiveCust1_fytd = get_the_date_fytd(dframe=ActiveCust1)

fytd_ActiveCust_temp = ActiveCust1_fytd.loc[:, ["TxnActCusts", "CountAccs"]].sum(0)
fytd_ActiveCust = str(round(float(fytd_ActiveCust_temp.TxnActCusts / fytd_ActiveCust_temp.CountAccs)*100,2)) + "%"


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

AccountInfoDetails1_fytd = get_the_date_fytd(dframe=AccountInfoDetails1)

#Extra Step for cleanup
AccountInfoDetails1_fytd.loc[:,"BRNCH_NME"] = AccountInfoDetails1_fytd.loc[:,"BRNCH_NME"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()

# Book value and total accounts & AMB
#AccountInfoDetails1_fytd2 = AccountInfoDetails1_fytd.loc[AccountInfoDetails1_fytd["MonthNam"] == last_value_ad[0]]

AccountInfoDetails1_fytd2_mix = pd.DataFrame(AccountInfoDetails1_fytd[["TotalAccounts","EOPBalance","AvgMTLBalnce"]].groupby(AccountInfoDetails1_fytd["BRNCH_NME"]).sum())
AccountInfoDetails1_branch_account_fytd2_mix = AccountInfoDetails1_fytd2_mix.loc[:, "TotalAccounts"]
AccountInfoDetails1_branch_eop_fytd2_mix = AccountInfoDetails1_fytd2_mix.loc[:, "EOPBalance"]
AccountInfoDetails1_branch_amb_fytd2_mix = AccountInfoDetails1_fytd2_mix.loc[:, "AvgMTLBalnce"]
fytd_branch_account_dict = {iterx : str(round(float(AccountInfoDetails1_branch_eop_fytd2_mix[AccountInfoDetails1_branch_eop_fytd2_mix.index == iterx].sum(0)/1),2)) for iterx in list_of_branches}
fytd_branch_eop_dict = {iterx : str(round(float(AccountInfoDetails1_branch_eop_fytd2_mix[AccountInfoDetails1_branch_eop_fytd2_mix.index == iterx].sum(0)/10**7),2)) for iterx in list_of_branches}
fytd_branch_amb_dict = {iterx : str(round(float(AccountInfoDetails1_branch_amb_fytd2_mix[AccountInfoDetails1_branch_amb_fytd2_mix.index == iterx].sum(0)/10**7),2)) for iterx in list_of_branches}

# New Customers

NewCust_dt = change_date_string_date(NewCust, dt_colname="AsOnYrMonName")
NewCust1 = pd.concat([NewCust.reset_index(drop=True),pd.DataFrame(NewCust_dt)], axis=1)
NewCust1.sort_values(by="date", inplace=True)
NewCust1_fytd = get_the_date_fytd(dframe=NewCust1)

#Extra Step for cleanup
NewCust1_fytd["BName"] = NewCust1_fytd["BName"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()

fytd_NewCust_branch_mix = NewCust1_fytd.loc[:, "CustCount"].groupby(NewCust1_fytd["BName"]).sum()

# %Active Clients

ActiveCust_dt = change_date_string_date(ActiveCust, dt_colname="YrMon_AsOnDate")
ActiveCust1 = pd.concat([ActiveCust.reset_index(drop=True),pd.DataFrame(ActiveCust_dt)], axis=1)
ActiveCust1.sort_values(by="date", inplace=True)
ActiveCust1_fytd = get_the_date_fytd(dframe=ActiveCust1)

#Extra Step for cleanup
ActiveCust1_fytd["BRNCH_NME"] = ActiveCust1_fytd["BRNCH_NME"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()


fytd_ActiveCust_branch_temp = ActiveCust1_fytd.loc[:, ["TxnActCusts", "CountAccs"]].groupby(ActiveCust1_fytd["BRNCH_NME"]).sum()
fytd_ActiveCust_branch_temp["percentage"] = round(fytd_ActiveCust_branch_temp.TxnActCusts / fytd_ActiveCust_branch_temp.CountAccs*100,2)
fytd_ActiveCust_branch_temp = fytd_ActiveCust_branch_temp.loc[:, "percentage"]

# Cash Day End Balance

cashbalances_dt = change_date_string_date(CashBalnces, dt_colname="YrMon")
CashBalnces1 = pd.concat([CashBalnces.reset_index(drop=True),pd.DataFrame(cashbalances_dt)], axis=1)
CashBalnces1.sort_values(by="date", inplace=True)
CashBalnces1_fytd = get_the_date_fytd(dframe=CashBalnces1)
#Extra Step for cleanup
CashBalnces1_fytd["BRNCH_NME"] = CashBalnces1_fytd["BRNCH_NME"].apply(lambda x : re.sub("\s+"," ", x)).str.upper()

fytd_CashBalnces_branch_mix = round(CashBalnces1_fytd.loc[:, ["DayEndBal", "BRNCH_NME"]].groupby(CashBalnces1_fytd["BRNCH_NME"]).sum()/10**7,2)

###For Products------------------------------------------------------------------------------

#AccountInfoDetails --------------------------------------------------------------------------

AccountInfoDetails_dt = change_date_string_date(AccountInfoDetails, dt_colname="MonthNam", delim="-")
AccountInfoDetails1 = pd.concat([AccountInfoDetails.reset_index(drop=True),pd.DataFrame(AccountInfoDetails_dt)], axis=1)
AccountInfoDetails1.sort_values(by="date", inplace=True)
AccountInfoDetails1_fytd = get_the_date_fytd(dframe=AccountInfoDetails1)

AccountInfoDetails1_fytd_temp = pd.DataFrame(AccountInfoDetails1_fytd.loc[:, ["TotalAccounts", "EOPBalance"]].sum(0)).T
fytd_AccountInfoDetails1_bookvalue =  str(round(float(AccountInfoDetails1_fytd_temp.EOPBalance/10**7),2))
fytd_AccountInfoDetails1_noa =  str(round(float(AccountInfoDetails1_fytd_temp.TotalAccounts),2))

#--------SA--------------------------------------------------------------------------

AccountInfoDetails1_SA_temp_fytd = pd.DataFrame(AccountInfoDetails1_fytd.loc[(AccountInfoDetails1_fytd.ProdGroup == "SA"),["TotalAccounts","EOPBalance"]].sum(0)).T
fytd_AccountInfoDetails1_SA_bookvalue =  str(round(float(AccountInfoDetails1_SA_temp_fytd.EOPBalance/10**7),2))
fytd_AccountInfoDetails1_SA_noa =  str(round(float(AccountInfoDetails1_SA_temp_fytd.TotalAccounts),2))

#--------RD--------------------------------------------------------------------------

AccountInfoDetails1_RD_fytd_temp = pd.DataFrame(AccountInfoDetails1_fytd.loc[(AccountInfoDetails1_fytd.ProdGroup == "RD"),["TotalAccounts","EOPBalance"]].sum(0)).T
fytd_AccountInfoDetails1_RD_bookvalue =  str(round(float(AccountInfoDetails1_RD_fytd_temp.EOPBalance/10**7),2))
fytd_AccountInfoDetails1_RD_noa =  str(round(float(AccountInfoDetails1_RD_fytd_temp.TotalAccounts),2))

#--------FD--------------------------------------------------------------------------

AccountInfoDetails1_FD_fytd_temp = pd.DataFrame(AccountInfoDetails1_fytd.loc[(AccountInfoDetails1_fytd.ProdGroup == "FD"),["TotalAccounts","EOPBalance"]].sum(0)).T
fytd_AccountInfoDetails1_FD_bookvalue =  str(round(float(AccountInfoDetails1_FD_fytd_temp.EOPBalance/10**7),2))
fytd_AccountInfoDetails1_FD_noa =  str(round(float(AccountInfoDetails1_FD_fytd_temp.TotalAccounts),2))

#--------CA--------------------------------------------------------------------------

AccountInfoDetails1_CA_fytd_temp = pd.DataFrame(AccountInfoDetails1_fytd.loc[(AccountInfoDetails1_fytd.ProdGroup == "CA"),["TotalAccounts","EOPBalance"]].sum(0)).T
fytd_AccountInfoDetails1_CA_bookvalue =  str(round(float(AccountInfoDetails1_CA_fytd_temp.EOPBalance/10**7),2))
fytd_AccountInfoDetails1_CA_noa =  str(round(float(AccountInfoDetails1_CA_fytd_temp.TotalAccounts),2))


#Standalone --------------------------------------------------------------------------

StandaloneCustomer_dt = change_date_string_date(StandaloneCustomer, dt_colname="YrMon_AsOnDate")
StandaloneCustomer1 = pd.concat([StandaloneCustomer.reset_index(drop=True),pd.DataFrame(StandaloneCustomer_dt)], axis=1)
StandaloneCustomer1.sort_values(by="date", inplace=True)
StandaloneCustomer1_fytd = get_the_date_fytd(dframe=StandaloneCustomer1)


fytd_StandaloneCustomer = StandaloneCustomer1_fytd.loc[:, ["CustCount"]].sum(0)
fytd_StandaloneCustomer =  str(round(float(fytd_StandaloneCustomer),2))
#---SA--------------------------------

fytd_StandaloneCustomer_SA = StandaloneCustomer1_fytd.loc[(StandaloneCustomer1_fytd.ProdGroup=="SA"), ["CustCount"]].sum(0)
fytd_StandaloneCustomer_SA =  str(round(float(fytd_StandaloneCustomer_SA),2))
#---RD--------------------------------

fytd_StandaloneCustomer_RD = StandaloneCustomer1_fytd.loc[ (StandaloneCustomer1_fytd.ProdGroup=="RD"), ["CustCount"]].sum(0)
fytd_StandaloneCustomer_RD =  str(round(float(fytd_StandaloneCustomer_RD),2))
#---CA--------------------------------

fytd_StandaloneCustomer_CA = StandaloneCustomer1_fytd.loc[(StandaloneCustomer1_fytd.ProdGroup=="CA"), ["CustCount"]].sum(0)
fytd_StandaloneCustomer_CA =  str(round(float(fytd_StandaloneCustomer_CA),2))
#---FD--------------------------------

fytd_StandaloneCustomer_FD = StandaloneCustomer1_fytd.loc[ (StandaloneCustomer1_fytd.ProdGroup=="FD"), ["CustCount"]].sum(0)
fytd_StandaloneCustomer_FD =  str(round(float(fytd_StandaloneCustomer_FD),2))


#Channel--------------------------------------------------------------------------------------------

##Total Transactions--------------------------------------------------------------------------------
# FTM_ChannelTxn

FTM_ChannelTxn_dt = change_date_string_date(FTM_ChannelTxn, dt_colname="AS_ON_DATE_YrMon",delim="-")
FTM_ChannelTxn1 = pd.concat([FTM_ChannelTxn.reset_index(drop=True),pd.DataFrame(FTM_ChannelTxn_dt)], axis=1)
FTM_ChannelTxn1.sort_values(by="date", inplace=True)
FTM_ChannelTxn1_fytd = get_the_date_fytd(dframe=FTM_ChannelTxn1)


fytd_FTM_ChannelTxn = FTM_ChannelTxn1_fytd.loc[:, ["TxnCount"]].sum(0)
fytd_FTM_ChannelTxn =  str(round(float(fytd_FTM_ChannelTxn),2))

#Channel Mix----------------------------------------------------------------------------------------
FTM_ChannelTxn_dt = change_date_string_date(FTM_ChannelTxn, dt_colname="AS_ON_DATE_YrMon",delim="-")
FTM_ChannelTxn1 = pd.concat([FTM_ChannelTxn.reset_index(drop=True),pd.DataFrame(FTM_ChannelTxn_dt)], axis=1)
FTM_ChannelTxn1.sort_values(by="date", inplace=True)
FTM_ChannelTxn1_fytd = get_the_date_fytd(dframe=FTM_ChannelTxn1)

FTM_ChannelTxn_fytd_mix = pd.DataFrame(FTM_ChannelTxn1_fytd.loc[:,"TxnCount"].groupby(FTM_ChannelTxn1_fytd["Channel"]).sum())
channel_indices = list(FTM_ChannelTxn_fytd_mix.index)
fytd_channel_dict = {items : str(round(float(FTM_ChannelTxn_fytd_mix[FTM_ChannelTxn_fytd_mix.index == items].sum(0)),2)) for items in channel_indices}

#----------Added later for Transaction value------------------------------------------------------------------------------

FTM_ChannelTxn_value_mix = pd.DataFrame(FTM_ChannelTxn1.loc[:,"TxnValue"].groupby(FTM_ChannelTxn1["Channel"]).sum())
channel_indices = list(FTM_ChannelTxn_value_mix.index)
fytd_channel_value_dict = {items : str(round(float(FTM_ChannelTxn_value_mix[FTM_ChannelTxn_value_mix.index == items].sum(0))/10**7,2)) for items in channel_indices}
