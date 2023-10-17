# SmartRouting--AgentPerformance
Build scorecard system for agents' performance Improve customer experience Create an API to transfer data\


Agent Performance
Why we need to do it
According to the previous analysis, we know that the efficiency and performance of the same agent dealing with different issues are different, and the different agents dealing with the same issue's performance are different. Therefore, our target is to arrange appropriate agent to handle appropriate issue to improve the customer experience when customers ask for help.

Goal
•	Build scorecard system for agents' performance
•	Improve customer experience
•	Create an API to transfer data 

What we are trying to get
•	Which attributes could measure agent's performance
•	what attributes we need to use during data modeling
•	how to get customer's feedback on this scorecard system

Agent's performance Measurement
Here we cannot just use csatscore to measure agent's performance, because there are so many conversasions that do not have the csatscore; here, we created a new attributes - CHS (conversasion health score), this is created by using NLP methods in the conversasion flow.

KPI	Description	Value
CHS	conversasion health score	-1: bad conversasion
  1: comfortable conversasion
probability score

