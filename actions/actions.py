# version 2.2.29

from collections import OrderedDict

from typing import Any, Text, Dict, List
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# TODO: GET DATA DYNAMICALLY FROM SETTINGS?

# RASA SLOTS (ENTITIES) MUST BE NAMED THE SAME AS VALUES, e.g. "password"
# RASA SOLUTION SLOTS MUST BE NAMED AS "solution_" + key, e.g. "solution_password_1"
# ORDER OF RIDDLES IS DEFINED HERE!
slotNameDict = OrderedDict()
slotNameDict["password_1"]   = "password"
slotNameDict["store_1"]      = "store"
slotNameDict["restaurant_1"] = "restaurant"
slotNameDict["pier_1"]       = "pier"
slotNameDict["password_2"]   = "password"

# RASA solution slot prefix
solutionPrefix = "solution_"

# name of RASA agent should solve slot
agentShouldSolveName = 'agent_should_solve'

# name of RASA hint counter slot
hintCounterName = 'hint_counter'

# name of RASA already told slot
alreadyToldGoalName = 'already_told_goal'

# convert keys to list that contains solution slot names
# IMPORTANT: RASA slots need to follow the same naming convention of solutionPrefix + slotName
solutionSlotNameList = [solutionPrefix + key for key in list(slotNameDict.keys())]

# answers are defined here
answerDict = {}
answerDict["password_1"]   = "123456"
answerDict["store_1"]      = "Alphabet Soup"
answerDict["restaurant_1"] = "Spago"
answerDict["pier_1"]       = "Pier 49"
answerDict["password_2"]   = "456789"

# defined answers to what's next questions
whatsNextDict = {}
whatsNextDict["password_1"]   = "I need you to help me find the passcode for the tablet."
whatsNextDict["store_1"]      = "You need to find out where Derek went from his apartment."
whatsNextDict["restaurant_1"] = "I need to know which restaurant the group went to."
whatsNextDict["pier_1"]       = "Derek is held captive somewhere. You need to find out the location."
whatsNextDict["password_2"]   = "I need the passcode to open the door to the warehouse."

# hints are defined here
hintsDict = {}
hintsDict["password_1"] = [
	"it should be a 6 digit code",
	"check the background picture on the tablet",
	"it has something to do with chess",
	"there is a chess trophy in the room",
	"the date on the trophy seems to be important",
	"it should be US date format (MM/DD/YY)"]
hintsDict["store_1"]      = ["store_hint1", "store_hint2", "store_hint3"]
hintsDict["restaurant_1"] = ["rest_hint1", "rest_hint2", "rest_hint3"]
hintsDict["pier_1"]       = ["pier_hint1", "pier_hint2", "pier_hint3"]
hintsDict["password_2"]   = ["pw2_hint1", "pw2_hint2", "pw2_hint3"]


class ActionVerifyGuess(Action):
	def name(self) -> Text:
		return "action_verify_guess"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		# get intent from last message
		intent = tracker.latest_message.get('intent').get('name')

		# utter fallback message if no intent or intent name was found or if intent is no riddle intent
		if intent == None or intent not in set(slotNameDict.values()):
			dispatcher.utter_message(response = "utter_default")
			return []
		else:
			# get entity from RASA message
			entity = tracker.get_slot(intent)
			
			# utter fallback message if entity could not be found
			if entity == None:
				dispatcher.utter_message(response = "utter_default")
				return []
			else:

				# store all solution slot values from RASA bot in list
				rasaSolutionSlotList = [tracker.get_slot(solutionSlotName) for solutionSlotName in solutionSlotNameList]

				# go through solution list and find active riddle index
				# (first index where entry is None)
				if None not in rasaSolutionSlotList:
					# TODO: HANDLE INPUT WHEN EVERYTHING IS SOLVED?
					dispatcher.utter_message(response = "utter_everything_solved")
					return []
				else:
					activeRiddleIndex = rasaSolutionSlotList.index(None)

				# find index list of active riddles with same intent (e.g. all active password riddles)
				index_list = [idx for idx, value in enumerate(solutionSlotNameList[activeRiddleIndex:]) if intent in value]

				# check if there are any active riddles of the matching type left
				if not index_list:
					# give user feedback about the mismatching categories and exit action
					dispatcher.utter_message(response = "utter_wrong_category")
					return []

				# save index of matching riddle (e.g. first "password") in active riddle list
				inputRiddleIndex = activeRiddleIndex + index_list[0]

				# #correct_answer = Answer[SlotName(intent).name].value
				# dispatcher.utter_message(text = "inputRiddleIndex: {}".format(inputRiddleIndex))
				# dispatcher.utter_message(text = "activeRiddleIndex: {}".format(activeRiddleIndex))
				# dispatcher.utter_message(text = "solutionSlotNameList[activeRiddleIndex]: {}".format(solutionSlotNameList[activeRiddleIndex]))
				
				# check if intent matches the active riddle and an entity was recognized
				if inputRiddleIndex == activeRiddleIndex:        
					# save correct answer for intent in variable
					correct_answer = answerDict[list(slotNameDict.keys())[inputRiddleIndex]]    

					# verify if given answer is correct (not case sensitive)
					if entity.lower() == correct_answer.lower():
						dispatcher.utter_message(response = "utter_correct_" + intent) #, store=correct_answer)
						# set correct answer in solution slot, reset hint counter and agent_should_solve slots
						return [SlotSet(solutionSlotNameList[activeRiddleIndex], correct_answer), SlotSet(hintCounterName, 0), SlotSet(agentShouldSolveName, False), SlotSet(alreadyToldGoalName, False)]
					else:
						dispatcher.utter_message(response = "utter_incorrect_" + intent) #, store=entity)
						return [SlotSet(intent, None)]

				# when the current riddle category doesn't match
				else:
					# give user feedback about the mismatching categories and exit action
					dispatcher.utter_message(response = "utter_wrong_category")
					return [SlotSet(intent, None)]


class ActionNextGoal(Action):
	def name(self) -> Text:
		return "action_next_goal"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		# store all solution slot values from RASA bot in respective lists
		rasaSolutionSlotList = [tracker.get_slot(solutionSlotName) for solutionSlotName in solutionSlotNameList]
		# get current hint counter value
		alreadyToldGoal = tracker.get_slot(alreadyToldGoalName)
		
		dispatcher.utter_message(text = "alreadyToldGoal: {}".format(alreadyToldGoal))

		# go through solution list and find active riddle index
		# (first index where entry is None)
		if None not in rasaSolutionSlotList:
			# TODO: HANDLE INPUT WHEN EVERYTHING IS SOLVED?			
			dispatcher.utter_message(response = "utter_everything_solved")
			return []
		else:
			if alreadyToldGoal:
				dispatcher.utter_message(response = "utter_offer_help")
				return []
			else:
				# define active riddle index
				activeRiddleIndex = rasaSolutionSlotList.index(None)
				# find active riddle name
				activeRiddleName = list(slotNameDict.keys())[activeRiddleIndex]

				dispatcher.utter_message(text = whatsNextDict[activeRiddleName])
				return [SlotSet(alreadyToldGoalName, True)]


class ActionHelpUser(Action):
	def name(self) -> Text:
		return "action_help_user"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		# store all solution slot values from RASA bot in respective lists
		rasaSolutionSlotList = [tracker.get_slot(solutionSlotName) for solutionSlotName in solutionSlotNameList]
		# get current hint counter value
		rasaHintCounter = tracker.get_slot(hintCounterName)
	
		# go through solution list and find active riddle index
		# (first index where entry is None)
		if None not in rasaSolutionSlotList:
			# TODO: HANDLE INPUT WHEN EVERYTHING IS SOLVED?
			dispatcher.utter_message(response = "utter_everything_solved")
			return []
		else:
			# define active riddle index
			activeRiddleIndex = rasaSolutionSlotList.index(None)
			# get name of active riddle	
			currentRiddleName = list(slotNameDict.keys())[activeRiddleIndex]
			# check if there is a hint left
			if rasaHintCounter < len(hintsDict[currentRiddleName]):
				# give the hint and increase the hint counter by one
				currentHint = hintsDict[currentRiddleName][rasaHintCounter]
				dispatcher.utter_message(text = currentHint)
				return [SlotSet(hintCounterName, rasaHintCounter + 1)]
			else:
				# ask if agent should solve the riddle and set slot to true
				dispatcher.utter_message(response = "utter_should_i_solve")
				# set agent_should_solve slot to true
				return [SlotSet(agentShouldSolveName, True)]


class ActionSolveRiddleOrWait(Action):
	def name(self) -> Text:
		return "action_solve_riddle_or_wait"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		# get intent from last message and current slot value
		intent = tracker.latest_message.get('intent').get('name')
		agentShouldSolve = tracker.get_slot(agentShouldSolveName)

		# create return list with standard slot set (reset agent_should_solve) 
		returnList = [SlotSet(agentShouldSolveName, False)]

		# check if agent should solve the riddle
		if agentShouldSolve:
			if intent == "affirm":
				# TODO: Solve riddle
				dispatcher.utter_message(text = "TODO: I WILL SOLVE FOR YOU")
				# add reset hint counter and reset already told goal return list
				returnList.append([SlotSet(hintCounterName, 0), SlotSet(alreadyToldGoalName, False)])
			elif intent == "deny":
				dispatcher.utter_message(response = "utter_do_not_solve")
			else:
				dispatcher.utter_message(response = "utter_default")
		# otherwise respond with normal reaction
		else:
			if intent == "affirm":
				# TODO: VERIFY IF RESPONSE TO HINTS MAKES SENSE
				dispatcher.utter_message(response = "utter_affirm")
			elif intent == "deny":
				# TODO: VERIFY IF RESPONSE TO HINTS MAKES SENSE
				dispatcher.utter_message(response = "utter_please")
			else:
				dispatcher.utter_message(response = "utter_default")

		# return SlotSets based on input
		return returnList



# class ActionHelpUser(Action):

#     def name(self) -> Text:
#         return "action_help_user"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # store all help slots in local variables
#         help_city = tracker.get_slot("help_city")
#         help_street = tracker.get_slot("help_street")
#         help_password = tracker.get_slot("help_password")

#         # store story progress slots in local variable
#         solution_city = tracker.get_slot("solution_city")
#         solution_street = tracker.get_slot("solution_street")
#         solution_password = tracker.get_slot("solution_password")

#         # print(solution_city)
#         # print(help_city)
#         # print(solution_street)
#         # print(help_street)
#         # print(solution_password)
#         # print(help_password)

#         # offer help based on story progress
#         if solution_password != None:
#             dispatcher.utter_message(text="The mission has been finished.")
#         elif solution_street != None:
#             # increase help counter by one
#             help_password += 1
#             # ask if serious hint is required
#             if help_password >= 3:
#                 dispatcher.utter_message(response="utter_need_hint")
#             # utter standard help
#             else:
#                 dispatcher.utter_message(response="utter_help_password")
#             # return increased help slot
#             return [SlotSet("help_password", help_password)] 
#         elif solution_city != None:
#             # increase help counter by one
#             help_street += 1
#             # ask if serious hint is required
#             if help_street >= 3:
#                 dispatcher.utter_message(response="utter_need_hint")
#             # utter standard help
#             else:
#                 dispatcher.utter_message(response="utter_help_street")
#             # return increased help slot
#             return [SlotSet("help_street", help_street)]  
#         else:
#             # increase help counter by one
#             help_city += 1
#             # ask if serious hint is required
#             if help_city >= 3:
#                 dispatcher.utter_message(response="utter_need_hint")
#             # utter standard help
#             else:
#                 dispatcher.utter_message(response="utter_help_city")
#             # return increased help slot
#             return [SlotSet("help_city", help_city)]           



# class ActionOfferHint(Action):

#     def name(self) -> Text:
#         return "action_offer_hint"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # store all help slots in local variables
#         help_city = tracker.get_slot("help_city")
#         help_street = tracker.get_slot("help_street")
#         help_password = tracker.get_slot("help_password")

#         # store story progress slots in local variable
#         solution_city = tracker.get_slot("solution_city")
#         solution_street = tracker.get_slot("solution_street")
#         solution_password = tracker.get_slot("solution_password")

#         # offer hints based on story progress
#         if solution_password != None:
#             dispatcher.utter_message(text="The mission has been finished.")
#         elif solution_street != None:
#             # give serious hint if help was requested 3 times
#             if help_password >= 3:
#                 # increase help counter by one
#                 help_password += 1
#                 dispatcher.utter_message(response="utter_hint_password")
#             # otherwise just affirm back
#             else:
#                 dispatcher.utter_message(response="utter_affirm") 
#             # return increased help slot
#             return [SlotSet("help_password", help_password)]  
#         elif solution_city != None:
#             # give serious hint if help was requested 3 times
#             if help_street >= 3:
#                 # increase help counter by one
#                 help_street += 1
#                 dispatcher.utter_message(response="utter_hint_street")
#             # otherwise just affirm back
#             else:
#                 dispatcher.utter_message(response="utter_affirm")
#             # return increased help slot
#             return [SlotSet("help_street", help_street)]  
#         else:
#             # give serious hint if help was requested 3 times
#             if help_city >= 3:
#                 # increase help counter by one
#                 help_city += 1
#                 dispatcher.utter_message(response="utter_hint_city")    
#             # otherwise just affirm back
#             else:
#                 dispatcher.utter_message(response="utter_affirm")                
#             # return increased help slot
#             return [SlotSet("help_city", help_city)]



# class ActionNextGoal(Action):

#     def name(self) -> Text:
#         return "action_next_goal"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # store story progress slots in local variable
#         solution_city = tracker.get_slot("solution_city")
#         solution_street = tracker.get_slot("solution_street")
#         solution_password = tracker.get_slot("solution_password")

#         if solution_password != None:
#             dispatcher.utter_message(text="The mission has been finished.")
#             return[]
#         elif solution_street != None:
#             dispatcher.utter_message(response="utter_goal_password") 
#             return[]
#         elif solution_city != None:
#             dispatcher.utter_message(response="utter_goal_street") 
#             return[]
#         else:
#             dispatcher.utter_message(response="utter_goal_city") 
#             return[]



	   
# class FacilityForm(FormValidationAction):

#     def name(self) -> Text:
#         return "validate_facility_form"

#     # @staticmethod
#     # def required_slots(tracker: Tracker) -> List[Text]:        
#     #     return ["facility_type", "city"]

#     def validate_slot_facility_type(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:

#         print("VALIDATING FACILITY SLOT")

#         return {"slot_facility_type": slot_value}
