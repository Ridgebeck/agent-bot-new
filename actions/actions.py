# version 2.5.2
from collections import OrderedDict

from typing import Any, Text, Dict, List
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction

# use firebase admin SDK via service account
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore





# FOR TESTING
testingRoom = "NEQIBR"

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
whatsNextField = u'whatsNext'
#missionField = u'mission'
#goalsField = u'currentGoals'
entityField = u'entity'
solutionField = u'solution'
hintCounterField = u'hintCounter'
hintsField = u'hints'
wrongGuessCounterField = u'wrongGuessCounter'



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

# TODO: ONE TRANSACTION OBJECT EACH?
# prepare for transactions
transaction = db.transaction()


@firestore.transactional
def offer_hint(transaction, dynamicDataDocRef, dispatcher):
	# get snapshot of doc and data as dict
	snapshot = dynamicDataDocRef.get(transaction=transaction)
	dynamicData = snapshot.to_dict()

	# read current goals list (whole list)
	goalList = dynamicData[goalsField]

	# find current goals
	currentGoals = goalList[dynamicData[gameProgressIDField]][goalsField]
	shouldISolve = False

	# check if current goals are present
	if not currentGoals:
		dispatcher.utter_message(response = "utter_no_hints")
	else:
		hintCounters = []
		for goal in currentGoals:
			# check if any hints exist
			if goal[hintsField]:
				# add hint counter number to list
				hintCounters.append(goal[hintCounterField])
			else:
				# add high number if goal with no hints 
				hintCounters.append(9999)

		# find index of goal with least hints
		lowestCount = min(hintCounters)
		# check if lowest hints is a goal with no hints at all
		if lowestCount == 9999:
			dispatcher.utter_message(response = "utter_no_hints")
		else:
			# save goal with least hints
			goalLeastHints = currentGoals[hintCounters.index(lowestCount)]

			# check if there are hints left to give
			if goalLeastHints[hintCounterField] < len(goalLeastHints[hintsField]):
				# give next hint
				dispatcher.utter_message(text = "{}".format(goalLeastHints[hintsField][goalLeastHints[hintCounterField]]))
				# increase hint counter by one
				goalList[dynamicData[gameProgressIDField]][goalsField][currentGoals.index(goalLeastHints)][hintCounterField] += 1
				# update goalList in dynamic data document
				transaction.update(dynamicDataDocRef, {goalsField: goalList})
			else:
				shouldISolve = True

	return shouldISolve



@firestore.transactional
def increase_wrongGuess_counter(transaction, dynamicDataDocRef, matchingGoalIndex):
	# get snapshot of doc and data as dict
	snapshot = dynamicDataDocRef.get(transaction=transaction)
	dynamicData = snapshot.to_dict()

	# read current goals list (whole list)
	goalList = dynamicData[goalsField]

	# increase wrongGuessCounter for specific goal 
	goalList[dynamicData[gameProgressIDField]][goalsField][matchingGoalIndex][wrongGuessCounterField] += 1

	# update goalList in dynamic data document
	transaction.update(dynamicDataDocRef, {goalsField: goalList})


@firestore.transactional
def move_forward_and_lock(transaction, dynamicDataDocRef):
	# get snapshot of doc and data as dict
	snapshot = dynamicDataDocRef.get(transaction=transaction)
	dynamicData = snapshot.to_dict()

	# check if document is locked (already guessed correctly)
	if dynamicData[lockedForBotField] == False:
		# increase current progress ID and lock document for bot
		transaction.update(dynamicDataDocRef, {gameProgressIDField: dynamicData[gameProgressIDField] + 1, lockedForBotField: True})



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
				roomID = testingRoom

			# store reference to document with dynamic data
			dynamicDataDocRef = db.collection(roomCollection).document(roomID).collection(dataCollection).document(dynamicDataDocument)
			
			# get room document from reference
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

				# save current goal
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
						move_forward_and_lock(transaction=transaction, dynamicDataDocRef=dynamicDataDocRef)
						dispatcher.utter_message(response = "utter_correct_" + intent)
						return []
					else:
						# offer help if 3 times guessed wrong
						if int(matchingGoal[wrongGuessCounterField]) > 2:
							dispatcher.utter_message(response = "utter_incorrect_" + intent)
							return [FollowupAction(name = "utter_offer_help")]
						else:
							dispatcher.utter_message(response = "utter_incorrect_" + intent)
							return []

						# increase wrongGuess counter by one
						increase_wrongGuess_counter(transaction=transaction, dynamicDataDocRef=dynamicDataDocRef, matchingGoalIndex=matchingGoalIndex)

				# handle wrong intent (no matching goal)
				else:
					dispatcher.utter_message(response = "utter_wrong_category")
					return [SlotSet(intent, None)]



class ActionNextGoal(Action):
	def name(self) -> Text:
		return "action_next_goal"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		# save roomID (aka. senderID)
		roomID = tracker.sender_id


		# TESTING: allow for trouble shooting through RASA X UI
		if len(roomID) > 10:
			roomID = testingRoom

		# store reference to document with dynamic data
		dynamicDataDocRef = db.collection(roomCollection).document(roomID).collection(dataCollection).document(dynamicDataDocument)
		
		# get room document from reference
		dynamicDataDoc = dynamicDataDocRef.get()

		# check if the document exists
		if dynamicDataDoc.exists == False:
			# TODO: error handling when room cannot be found?!
			dispatcher.utter_message(text = "room {} does not exist".format(roomID))
			return []
		else:
			# save room data as a dict
			dynamicData = dynamicDataDoc.to_dict()

			# save current goal
			currentGoals = dynamicData[goalsField][dynamicData[gameProgressIDField]][goalsField]

			# check if there are any current goals
			if not currentGoals:
				dispatcher.utter_message(text = "no goals found.")
				return []
			else:

				# check if multiple goals are active
				if len(currentGoals) == 1:
					dispatcher.utter_message(text = "{}".format(currentGoals[0][whatsNextField]))
					return []
				else:
					# TODO: USE UTTER VARIATION TEXT INSTEAD
					dispatcher.utter_message(text = "There are {} things to do right now:".format(len(currentGoals)))
					for goal in currentGoals:
						dispatcher.utter_message(text = "{}".format(goal[whatsNextField]))
					return []




class ActionHelpUser(Action):
	def name(self) -> Text:
		return "action_help_user"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		# save roomID (aka. senderID)
		roomID = tracker.sender_id


		# TESTING: allow for trouble shooting through RASA X UI
		if len(roomID) > 10:
			roomID = testingRoom		

		# store reference to document with dynamic data
		dynamicDataDocRef = db.collection(roomCollection).document(roomID).collection(dataCollection).document(dynamicDataDocument)

		# give hint, check if there are hints left
		shouldISolve = offer_hint(transaction=transaction, dynamicDataDocRef=dynamicDataDocRef, dispatcher=dispatcher)

		# offer to solve riddle if no hints are left
		if shouldISolve:
			return [FollowupAction(name = "utter_should_i_solve")]
		else:
			return[]


class ActionSolveRiddle(Action):
	def name(self) -> Text:
		return "action_solve_riddle"
	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


		# get intent from last message and current slot value
		#intent = tracker.latest_message.get('intent').get('name')
		#agentShouldSolve = tracker.get_slot(agentShouldSolveName)

		dispatcher.utter_message(text = "SOLVING RIDDLE FOR YOU...(TODO)")






	   
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