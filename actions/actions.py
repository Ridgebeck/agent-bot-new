# version 2.3.83

from collections import OrderedDict

from typing import Any, Text, Dict, List
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# use firebase admin SDK via service account
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# initialize firebase app with credentials
credDict =	{
  "type": "service_account",
  "project_id": "strix-3b648",
  "private_key_id": "5552c9242ab9aeaca592004edbf233e9a097b788",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDT0l1Raw1thupU\nPuL6kDxjDIj6cf3bnRpi5bW7RJsOG8II8dLYAo2LDD3AbhY5aWB15mV7F9C0LKHJ\nl6X9kv7ugitGKW4yJozKg0jgydBuWay/SRzgYEmgGva4GywOJfYSM3qXuqhGNFa+\nMnRSV6cjUC7Sr5VdQh1HD4ysaiYrEGPa4NhT8TD5SIYfvYygwC+ua+9DYF3g+7UM\nw99c8mMOcEJhvD690ivjelcnDGW8y6Yu9ukBpLfyRjbM8dFNY4qOmxwXWuJS76l7\nO/Uc8T2bW0skPLqG4BEswASn88+v2G1DqHOlKASrrNamZaWv64fgiGxCz7YezmwN\n0MV+SANzAgMBAAECggEAC4B/c2MDa6XJJkyejp8zvZJ6Av9wRXNBHOBUVJg5GImx\nU5hYq+9s4tawqQ5RQ/TQ5BYKqfsfvhOJBXqn7MkFRsuSsKX3RzSIrfEgYp8SzlXY\nPNrU0pTn6pBhl/BXHWg6SxVjMXH/89qhCzA6Lhkhs5fbCF24bUP1ywdbytDzbvXE\n66DncaufX6IzGvlTO8uS6PvYI8t4d0HIUfTM0W5YN0V2thnGzzh4f6XGH+MZLknB\nhXK3AkvDH7v52/YxSbofR+6tGUuBHKU7uiz5nrBcwsxFFrf0RpgyAalETzlDeSKg\nGampHzi0UB/86GAi2T+ffvXYYb12lLBLiEY/Y9b5AQKBgQDr5tvMnIL990EVHukD\nQcNtwJs1SVOE033IwHsy1M3FVUQSNnQc9EvCsmN2N1qIKnaROIo8qdVPyUUHwf8z\nQWWhr+IxRwie0Yca+CvzdZUW5hcBeBJNVQC5sRJW1HstXELnMTaolDAkePQe5bY8\nyZZTJat39dx7Icd71I42yAqT4QKBgQDl3k6uG+v3TkPdBCgEQT5D83fTzdxkOPjS\na2BC9aS8x6GK79/m0rBYr4j8ungkpD/NXtww04jOcWPc2OA1HtV02whbhGiI8B5j\nAjJb71ikUpdDajJEoXwfC/0NOi4a6YqxNquGteiQDG3sxKN534ltOwGkPZEVz1sj\nBKp1boRB0wKBgQDgQeEmDIvCnzDxwSbGf9gnF/j0mTaaiOuE0ubLld3gAITrw3Ry\nqhLzjd5b3Zdk5uk8eMGBlfpBFRdYnqXatgrFwIyJR/v77zg+/TnbAiavVCD+toS/\nm1VLMfg7L1fB8Xlwiypo7CcwJQP982ZhN0p+1MrDCamGLMCVCaYAkf7sQQKBgQCX\nwdvKAK8ZV3dgO/U7UeOMsvlCQR+mnyJOsQsdSdVXuKhC9LiqSCCafFEBIQ5ein2A\n1YajSZSBTsTyMdBb4Z5lBpIO8WyeM4CsNvAOWAb6fXhVzo+fVcl/KcgH6ogzxkmF\nU6WMSx5ds4cDEJMoy9aL4a/kway+bGYryVHMM4lndwKBgGq22Dx3FzHUOW75S9Zj\n9Q0Eduik5rngUNjBkQgjbatYFKkCeNiJUhGUSMjZxoWmmXMMjc0YFooe+s1YbkAc\npIhgBqvlcOVDtAhtJlWjptaDssXP8rbKJKviLWMlL6G2nrUfsfLPwwFF3ZMk0UnA\n7OPVm7uVnkFAC5swQhQ+0oDG\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fj4ol@strix-3b648.iam.gserviceaccount.com",
  "client_id": "107409023459416415651",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fj4ol%40strix-3b648.iam.gserviceaccount.com"
}

cred = credentials.Certificate(credDict)
firebase_admin.initialize_app(cred)

# save database reference
db = firestore.client()

# prepare for transactions
transaction = db.transaction()


@firestore.transactional
def increase_wrongGuess_counter(transaction, dynamicDataDocRef, matchingGoalIndex):
	# get snapshot of doc and data as dict
	snapshot = dynamicDataDocRef.get(transaction=transaction)
	dynamicData = snapshot.to_dict()

	# read current goals list (whole list)
	goalList = dynamicData[goalsField]

	# increase wrongGuessCounter for specific goal 
	goalList[dynamicData[gameProgressIDField]][goalsField][matchingGoalIndex][wrongGuessField] += 1

	# update goalList in dynamic data document
	transaction.update(dynamicDataDocRef, {goalsField: goalList})


@firestore.transactional
def move_forward_and_lock(transaction, dynamicDataDocRef, dispatcher):
	# get snapshot of doc and data as dict
	snapshot = dynamicDataDocRef.get(transaction=transaction)
	dynamicData = snapshot.to_dict()

	# check if document is locked (already guessed correctly)
	if dynamicData[lockedForBotField] == False:
		# increase current progress ID and lock document for bot
		transaction.update(dynamicDataDocRef, {gameProgressIDField: dynamicData[gameProgressIDField] + 1, lockedForBotField: True})



# collection and document references
roomCollection = u'activeRooms'
chatCollection = u'chat'
dataCollection = u'data'
chatDocument = u'chatData'
dynamicDataDocument = u'dynamicData'

# field references
gameProgressField = u'gameProgress'
gameProgressIDField = u'gameProgressID'
lockedForBotField = u'lockedForBot'
settingField = u'settings'
goalsField = u'goals'
availableAssetsField = u'availableAssets'
missionField = u'mission'
#goalsField = u'currentGoals'
entityField = u'entity'
solutionField = u'solution'
wrongGuessField = u'wrongGuessCounter'



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

# # answers are defined here
# answerDict = {}
# answerDict["password_1"]   = "123456"
# answerDict["store_1"]      = "Alphabet Soup"
# answerDict["restaurant_1"] = "Spago"
# answerDict["pier_1"]       = "Pier 49"
# answerDict["password_2"]   = "456789"

# # defined answers to what's next questions
# whatsNextDict = {}
# whatsNextDict["password_1"]   = "I need you to help me find the passcode for the tablet."
# whatsNextDict["store_1"]      = "You need to find out where Derek went from his apartment."
# whatsNextDict["restaurant_1"] = "I need to know which restaurant the group went to."
# whatsNextDict["pier_1"]       = "Derek is held captive somewhere. You need to find out the location."
# whatsNextDict["password_2"]   = "I need the passcode to open the door to the warehouse."

# # hints are defined here
# hintsDict = {}
# hintsDict["password_1"] = [
# 	"it should be a 6 digit code",
# 	"check the background picture on the tablet",
# 	"it has something to do with chess",
# 	"there is a chess trophy in the room",
# 	"the date on the trophy seems to be important",
# 	"it should be US date format (MM/DD/YY)"]
# hintsDict["store_1"]      = ["store_hint1", "store_hint2", "store_hint3"]
# hintsDict["restaurant_1"] = ["rest_hint1", "rest_hint2", "rest_hint3"]
# hintsDict["pier_1"]       = ["pier_hint1", "pier_hint2", "pier_hint3"]
# hintsDict["password_2"]   = ["pw2_hint1", "pw2_hint2", "pw2_hint3"]


class ActionVerifyGuess(Action):
	def name(self) -> Text:
		return "action_verify_guess"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		# save intent, guess and roomID (aka. senderID)
		intent = str(tracker.get_intent_of_latest_message())
		guess = str(tracker.get_slot(intent))
		roomID = tracker.sender_id

		# utter fallback message if no intent was found
		if intent == None or guess == None:
			dispatcher.utter_message(response = "utter_default")
			return []
		# proceed if an intent was given
		else:

			# TESTING: allow for trouble shooting through RASA X UI
			if len(roomID) > 10:
				# use an existing room as dummy
				roomID = "NEQIBR"

			# store reference to document with dynamic data
			dynamicDataDocRef = db.collection(roomCollection).document(roomID).collection(dataCollection).document(dynamicDataDocument)
			
			# # get room document from reference
			dynamicDataDoc = dynamicDataDocRef.get()

			# check if the document exists
			if dynamicDataDoc.exists == False:
				# TODO: error handling when room cannot be found
				dispatcher.utter_message(text = "room {} does not exist".format(roomID))
				return []
			else:				

				# save room data as a dict
				dynamicData = dynamicDataDoc.to_dict()

				# create empty dict for an intent-matching goal
				matchingGoal = {}
				matchingGoalIndex = None

				# # TODO: create constants with field names
				currentGoals = dynamicData[goalsField][dynamicData[gameProgressIDField]][goalsField]

				for idx, goal in enumerate(currentGoals):
					if entityField in goal:
						if intent == goal[entityField]:
							# save first matching goal and exit loop
							# WARNING: cannot have multiple riddles with same intent at the same time!
							matchingGoal = goal
							matchingGoalIndex = idx
							break

				# check if a matching goal was found
				if matchingGoal:
					# save correct answer in variable
					correctAnswer = str(matchingGoal[solutionField])

					# check if guess is correct
					if guess.lower() == correctAnswer.lower():
						# progress and lock for bot to avoid multiple correct guesses
						move_forward_and_lock(transaction=transaction, dynamicDataDocRef=dynamicDataDocRef, dispatcher=dispatcher)
						dispatcher.utter_message(response = "utter_correct_" + intent)
						return []
					else:
						# increase wrongGuess counter by one 
						increase_wrongGuess_counter(transaction=transaction, dynamicDataDocRef=dynamicDataDocRef, matchingGoalIndex=matchingGoalIndex)

						# offer help if 3 times guessed wrong
						if int(matchingGoal[wrongGuessField]) > 3:
							dispatcher.utter_message(response = "utter_offer_help")
							return []
						else:
							dispatcher.utter_message(response = "utter_incorrect_" + intent)
							return []

				# handle wrong intent (no matching goal)
				else:
					dispatcher.utter_message(response = "utter_wrong_category")
					return [SlotSet(intent, None)]




				# set indices of arrays to None
				#matchingGoalIndex = None

				# # find the current assets based on game progress
				# currentAssets = {}
				# for idx, assetEntry in enumerate(availableAssets):
				# 	# save current assetEntry
				# 	if list(assetEntry.keys())[0] == roomData[gameProgressField]:
				# 		currentAssetIndex = idx
				# 		currentAssets = assetEntry[roomData[gameProgressField]]

				# # check if current assetEntry has mission field
				# if missionField not in currentAssets:
				# 	# TODO: error handling when mission field cannot be found
				# 	dispatcher.utter_message(text = "no mission field entry")
				# 	return []
				# else:
				# 	# check if mission entry has goal field
				# 	if goalsField not in currentAssets[missionField]:
				# 		# TODO: error handling when goals field cannot be found
				# 		dispatcher.utter_message(text = "no goal field entry")
				# 		return []
				# 	else:

						# # go through all current goals (list)
						# for idx, goal in enumerate(currentAssets[missionField][goalsField]):					
						# 	# check if any entity of current goals matches the intent
						# 	if entityField in goal:								
						# 		if intent == goal[entityField]:
						# 			# save first matching goal and its index, and exit loop
						# 			# WARNING: cannot have multiple riddles with same intent at the same time!
						# 			matchingGoal = goal
						# 			matchingGoalIndex = idx
						# 			break




						# # check if a matching goal was found
						# if matchingGoal:							
						# 	# save correct answer in variable
						# 	correctAnswer = matchingGoal[solutionField]

						# 	# convert guess and answer to string if necessary
						# 	if not isinstance(guess, str):
						# 		guess = str(guess)
						# 	if not isinstance(correctAnswer, str):
						# 		correctAnswer = str(correctAnswer)								

						# 	# check if guess is correct
						# 	if guess.lower() == correctAnswer.lower():
						# 		# TODO: MOVE FORWARD IN STORY IF CORRECT
						# 		dispatcher.utter_message(response = "utter_correct_" + intent)
						# 		return []
						# 	else:
						# 		# CHECK IF ALREADY 3X guessed wrong
						# 		if matchingGoal[wrongGuessField] >= 3:
						# 			# TODO: utter_offer_help
						# 			dispatcher.utter_message(text = "Offer help!")
						# 		else:
						# 			# increase wrongGuess counter by one
						# 			increase_wrongGuess_counter(transaction=transaction, roomDocRef=roomDocRef, currentAssetIndex=currentAssetIndex, matchingGoalIndex=matchingGoalIndex)

						# 			dispatcher.utter_message(response = "utter_incorrect_" + intent)
						# 			return []
						
						# # handle wrong intent
						# else:
						# 	#dispatcher.utter_message(text = "wrong category!")
						# 	dispatcher.utter_message(response = "utter_wrong_category")
						# 	return [SlotSet(intent, None)]



		# # get intent from last message
		# intent = tracker.latest_message.get('intent').get('name')

		# # utter fallback message if no intent or intent name was found or if intent is no riddle intent
		# if intent == None or intent not in set(slotNameDict.values()):
		# 	dispatcher.utter_message(response = "utter_default")
		# 	return []
		# else:
		# 	# get entity from RASA message
		# 	entity = tracker.get_slot(intent)
			
		# 	# utter fallback message if entity could not be found
		# 	if entity == None:
		# 		dispatcher.utter_message(response = "utter_default")
		# 		return []
		# 	else:

		# 		# store all solution slot values from RASA bot in list
		# 		rasaSolutionSlotList = [tracker.get_slot(solutionSlotName) for solutionSlotName in solutionSlotNameList]

		# 		# go through solution list and find active riddle index
		# 		# (first index where entry is None)
		# 		if None not in rasaSolutionSlotList:
		# 			# TODO: HANDLE INPUT WHEN EVERYTHING IS SOLVED?
		# 			dispatcher.utter_message(response = "utter_everything_solved")
		# 			return []
		# 		else:
		# 			activeRiddleIndex = rasaSolutionSlotList.index(None)

		# 		# find index list of active riddles with same intent (e.g. all active password riddles)
		# 		index_list = [idx for idx, value in enumerate(solutionSlotNameList[activeRiddleIndex:]) if intent in value]

		# 		# check if there are any active riddles of the matching type left
		# 		if not index_list:
		# 			# give user feedback about the mismatching categories and exit action
		# 			dispatcher.utter_message(response = "utter_wrong_category")
		# 			return []

		# 		# save index of matching riddle (e.g. first "password") in active riddle list
		# 		inputRiddleIndex = activeRiddleIndex + index_list[0]

		# 		# #correct_answer = Answer[SlotName(intent).name].value
		# 		# dispatcher.utter_message(text = "inputRiddleIndex: {}".format(inputRiddleIndex))
		# 		# dispatcher.utter_message(text = "activeRiddleIndex: {}".format(activeRiddleIndex))
		# 		# dispatcher.utter_message(text = "solutionSlotNameList[activeRiddleIndex]: {}".format(solutionSlotNameList[activeRiddleIndex]))
				
		# 		# check if intent matches the active riddle and an entity was recognized
		# 		if inputRiddleIndex == activeRiddleIndex:        
		# 			# save correct answer for intent in variable
		# 			correct_answer = answerDict[list(slotNameDict.keys())[inputRiddleIndex]]    

		# 			# verify if given answer is correct (not case sensitive)
		# 			if entity.lower() == correct_answer.lower():
		# 				dispatcher.utter_message(response = "utter_correct_" + intent) #, store=correct_answer)
		# 				# set correct answer in solution slot, reset hint counter and agent_should_solve slots
		# 				return [SlotSet(solutionSlotNameList[activeRiddleIndex], correct_answer), SlotSet(hintCounterName, 0), SlotSet(agentShouldSolveName, False), SlotSet(alreadyToldGoalName, False)]
		# 			else:
		# 				dispatcher.utter_message(response = "utter_incorrect_" + intent) #, store=entity)
		# 				return [SlotSet(intent, None)]

		# 		# when the current riddle category doesn't match
		# 		else:
		# 			# give user feedback about the mismatching categories and exit action
		# 			dispatcher.utter_message(response = "utter_wrong_category")
		# 			return [SlotSet(intent, None)]


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


		dispatcher.utter_message(text = "OFFER HINT!")


		# # store all solution slot values from RASA bot in respective lists
		# rasaSolutionSlotList = [tracker.get_slot(solutionSlotName) for solutionSlotName in solutionSlotNameList]
		# # get current hint counter value
		# rasaHintCounter = tracker.get_slot(hintCounterName)
	
		# # go through solution list and find active riddle index
		# # (first index where entry is None)
		# if None not in rasaSolutionSlotList:
		# 	# TODO: HANDLE INPUT WHEN EVERYTHING IS SOLVED?
		# 	dispatcher.utter_message(response = "utter_everything_solved")
		# 	return []
		# else:
		# 	# define active riddle index
		# 	activeRiddleIndex = rasaSolutionSlotList.index(None)
		# 	# get name of active riddle
		# 	currentRiddleName = list(slotNameDict.keys())[activeRiddleIndex]
		# 	# check if there is a hint left
		# 	if rasaHintCounter < len(hintsDict[currentRiddleName]):
		# 		# give the hint and increase the hint counter by one
		# 		currentHint = hintsDict[currentRiddleName][rasaHintCounter]
		# 		dispatcher.utter_message(text = currentHint)
		# 		return [SlotSet(hintCounterName, rasaHintCounter + 1)]
		# 	else:
		# 		# ask if agent should solve the riddle and set slot to true
		# 		dispatcher.utter_message(response = "utter_should_i_solve")
		# 		# set agent_should_solve slot to true
		# 		return [SlotSet(agentShouldSolveName, True)]







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