#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 20:24:39 2022

@author: yuxia
"""

# firstly, need to get connection to the database, here we need to get connection to the API 



import pandas as pd
import numpy as np


# first query: case data
query = """

SELECT
        crm.employee_key, crm.employee_name, 
        call_chat.case_key, call_chat.incidentlevel2reason, crm.sub_line_of_business__c, call_chat.wait_time, call_chat.complete_duration, call_chat.avg_response_cust, call_chat.avg_response_agnt, call_chat.agent_handle_time, call_chat.close_time,
        call_chat.no_of_upfront_sla_breach, call_chat.no_of_turns_per_conversation, call_chat.no_of_agents, call_chat.agent_tenure_days, Z.resolution_days, Z.customer_tenure_days,
        call_chat.csatscore, call_chat.cesscore, call_chat.agentsatisfactionscore, call_chat.fcrscore, call_chat.fiscal_qtr
    FROM
    (SELECT * FROM
    ce_analytics.fact_agg_call_chat) call_chat
    join
    (select * from ce_analytics.dim_Crm_employee) crm
    on 
    crm.employee_key = call_chat.latest_employee_key
    
  
    JOIN
    (SELECT transaction_no, resolution_days, customer_tenure_days from ce_analytics.fact_closed_case) Z
    ON
    call_chat.case_key = Z.transaction_no
    WHERE
    call_chat.language_key = '13'
    AND
    call_chat.data_source = 'LE'
    
 

"""

all_data = connection.read_sql(query, conn = conn) # 11: 06

# adding more agent data

query = """
select agent_case_handling_number.*, employee_key, Date, day_working_hours, day_billable_hour

from
( select latest_employee_key, date(date_parse(interaction_starttime,'%Y-%m-%d %H:%i:%s')) as day,  
    count(vendorid) as number_cases
    from ce_analytics.fact_agg_call_chat group by latest_employee_key, date(date_parse(interaction_starttime,'%Y-%m-%d %H:%i:%s'))
    ) agent_case_handling_number

right join
(
select employee_key, date(date_parse(cal_date,'%Y-%m-%d %H:%i:%s')) as Date, sum(login_time)/3600.00 as day_working_hours, 
sum(billable_hour)/3600.00 as day_billable_hour  
from ce_analytics.fact_agent_productivity_combined group by employee_key, 
date(date_parse(cal_date,'%Y-%m-%d %H:%i:%s')) 
) agent_working_hours
on agent_case_handling_number.latest_employee_key = agent_working_hours.employee_key
and agent_case_handling_number.day = agent_working_hours.Date

"""

agent_data = connection.read_sql(query, conn = conn)
# fillna
agent_data['latest_employee_key'] = agent_data['latest_employee_key'].fillna(agent_data['employee_key'])
# calculate CPH for agent level
agent_data['day'] = agent_data['day'].fillna(agent_data['Date'])
agent_data.number_cases = agent_data.number_cases.astype(float)
agent_data.day_billable_hour = agent_data.day_billable_hour.astype(float)
agent_data['CPH'] = agent_data.number_cases / agent_data.day_billable_hour 
# fill na
agent_data.replace([np.inf], np.nan, inplace=True) 
agent_data = agent_data[agent_data.CPH <= 10]



agent_data.day_working_hours = agent_data.day_working_hours.astype(float)
agent_data.day_billable_hour = agent_data.day_billable_hour.astype(float)
agent_data.CPH = agent_data.CPH.astype(float)
agent = pd.DataFrame(agent_data.groupby('latest_employee_key').agg({'day_working_hours':'mean',
                                                             'day_billable_hour': 'mean', 'CPH': np.nanmean,
                                                                   'number_cases': 'mean'})).reset_index()


  

# CHS data
query = """

select * from ragupt.fact_chs_scoring

"""
chs = connection.read_sql(query = query, conn = conn)


# merge all the infomation

all_data_new = pd.merge(left = all_data, right = chs[['case_key', 'chs']], on = 'case_key')
all_data.shape  

all_data_new = pd.merge(left = all_data_new, right = agent[['latest_employee_key', 'day_working_hours', 'day_billable_hour', 'CPH']]
                       ,left_on = 'employee_key', right_on = 'latest_employee_key')



# modeling
import pandas as pd
from optbinning import Scorecard, BinningProcess
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Load the train dataset
df_all_data_new = all_data_new[['employee_name', 'incidentlevel2reason', 'sub_line_of_business__c',
       'wait_time', 'complete_duration', 'avg_response_cust',
       'avg_response_agnt', 'agent_handle_time', 'close_time',
       'no_of_upfront_sla_breach', 'no_of_turns_per_conversation',
       'no_of_agents', 'agent_tenure_days', 'resolution_days', 'csatscore', 'day_working_hours',
       'day_billable_hour', 'CPH', 'chs']]
df_all_data_new.csatscore = df_all_data_new.csatscore.astype(float)
df_all_data_new['chs'] = df_all_data_new['chs'].map({1: 'good', -1: 'bad'})

df_all_data_new['chs'] = df_all_data_new['chs'].map({'good': 1, 'bad': 0})


X = df_all_data_new.loc[:, df_all_data_new.columns != 'chs']
y = df_all_data_new['chs']

# Split the dataset into train and test
df_application_train, df_application_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42)

# Define the feature list from dataset (including categorical and numerical)
list_features = df_application_train.columns.values

# Define categorical features list
list_categorical = df_application_train.select_dtypes(include=['object', 'category']).columns.values

# Define selection criteria for BinningProcess
selection_criteria = {"iv": {"min": 0.005, 'max':0.5, "strategy": "highest"}}
logreg = LogisticRegression(C=5, max_iter=1000, random_state=161)
# Define scaling method and values
import numpy as np
scaling_method = "min_max"
scaling_method_data = {"min": 0, "max": 100}
variable_names = np.array(X.columns)
# Instatiate and fit Scorecard
scorecard = Scorecard(
    binning_process= BinningProcess(variable_names),
    estimator=logreg,
    scaling_method="min_max",
     scaling_method_params={"min": 0, "max": 100},
    reverse_scorecard=True)

scorecard.fit(df_application_train, list(y_train))

# check model performance

from optbinning.scorecard.plots import plot_ks, plot_auc_roc
# ROC-AUC plot
plot_auc_roc(y_test, df_application_test.score) 

scorecard.table(style="detailed").to_excel('model_summary.xlsx')

X['score'] = scorecard.score(X)
final_score = pd.DataFrame(X.groupby(['employee_name','sub_line_of_business__c', 'incidentlevel2reason']).agg({'score':'mean', 'chs': 'count'})).reset_index()
final_score = final_score.rename(columns = {'chs': 'count'})

# final output
final_score.pivot(index=['employee_name','sub_line_of_business__c'] ,columns='incidentlevel2reason',values=['score']).reset_index().to_excel('scorecard.xlsx')



