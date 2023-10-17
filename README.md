# SmartRouting--AgentPerformance
Build scorecard system for agents' performance Improve customer experience Create an API to transfer data\


**#Agent Performance**
Why we need to do it
According to the previous analysis, we know that the efficiency and performance of the same agent dealing with different issues are different, and the different agents dealing with the same issue's performance are different. Therefore, our target is to arrange appropriate agent to handle appropriate issue to improve the customer experience when customers ask for help.

**Goal**
•	Build scorecard system for agents' performance
•	Improve customer experience
•	Create an API to transfer data 

**What we are trying to get**
•	Which attributes could measure agent's performance
•	what attributes we need to use during data modeling
•	how to get customer's feedback on this scorecard system

**Agent's performance Measurement**
Here we cannot just use csatscore to measure agent's performance, because there are so many conversasions that do not have the csatscore; here, we created a new attributes - CHS (conversasion health score), this is created by using NLP methods in the conversasion flow.

**KPI	Description	Value**
CHS	conversasion health score
-1: bad conversasion
  1: comfortable conversasion

Attribute	Understanding
wait time	customers' waiting time
complete duration	complete duration time
avg_response_cust	average response time for customers
avg_response_agnt	average response time for agents
agent_handle_time	average handling time
no_of_turns_conversasion	the number of turns in the whole conversasion
no_of_agents	the number of agents handling the whole case
agent_tenure_days	agent tenure days
resolution_days	resolution days
customer_tenure_days	customer tenure
working hours	average workings hours for agents
billable hours	average billing hours for agents
CPH	contact per hour

