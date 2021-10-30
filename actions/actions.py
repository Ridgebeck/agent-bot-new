# version 2.0.2

from typing import Any, Text, Dict, List

from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

correct_answer_password = "123456"
correct_answer_store = "Alphabet Soup"

# correct_answer_city = "Chicago"
# correct_answer_street_1 = "First Street"
# correct_answer_street_2 = "Oak Street"


class ActionVerifyPassword(Action):

    def name(self) -> Text:
        return "action_verify_password"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # store password slot in local variable
        passcode = tracker.get_slot("password")

        # store story progress slots in local variable
        solution_password = tracker.get_slot("solution_password")

        # respond if password riddle has already been solved         
        if solution_password != None:
            dispatcher.utter_message(response="utter_no_password_needed")
            return []
        # otherwise progress (user is supposed to work on password riddle)
        else:
            # remove everything thats not a digit
            passcode = "".join(filter(str.isdigit, passcode))       
            #print(passcode)

            # check if length is correct
            if len(passcode) != len(correct_answer_password):
                dispatcher.utter_message(response="utter_wrong_length_password", password=passcode)
                return [SlotSet("password", None)]
            else:
                if passcode == correct_answer_password:
                    dispatcher.utter_message(response="utter_correct_password", password=correct_answer_password)
                    return [SlotSet("solution_password", correct_answer_password)]
                else:
                    dispatcher.utter_message(response="utter_incorrect_password", password=passcode)
                    return [SlotSet("password", None)]


class ActionVerifyStore(Action):

    def name(self) -> Text:
        return "action_verify_store"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # store city slot in local variable
        store = tracker.get_slot("store")

        # store story progress slot in local variable
        solution_password = tracker.get_slot("solution_password")
        solution_store = tracker.get_slot("solution_store")
        solution_restaurant = tracker.get_slot("solution_restaurant")
        solution_pier = tracker.get_slot("solution_pier")


        # check if pier riddle was already solved (final)
        if solution_pier != None:
            #dispatcher.utter_message(response="utter_mission_finished")
            return []
        # check if restaurant riddle was already solved (looking for pier)
        elif solution_restaurant != None:
            dispatcher.utter_message(response="utter_pier_not_store")
            return []
        # check if store riddle was already solved (looking for restaurant)
        elif solution_store != None:
            dispatcher.utter_message(response="utter_restaurant_not_store")
            return []
        # check if first password riddle is still active
        elif solution_password == None:
            dispatcher.utter_message(response="utter_password_not_store")
            return []
        else:
        	# check if store entity was provided
            if store == None:
                #dispatcher.utter_message(response="utter_no_store")
                return []
            # verify given store entity
            elif store.lower() == correct_answer_store.lower():
                dispatcher.utter_message(response="utter_correct_store", store=correct_answer_store)
                return [SlotSet("solution_store", correct_answer_store)]
            else:
                dispatcher.utter_message(response="utter_incorrect_store", store=store)
                return [SlotSet("store", None)]



# class ActionVerifyCity(Action):

#     def name(self) -> Text:
#         return "action_verify_city"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # store city slot in local variable
#         city = tracker.get_slot("city")

#         # store story progress slot in local variable
#         solution_city = tracker.get_slot("solution_city")

#         # check if riddle was already solved
#         if solution_city != None:
#             dispatcher.utter_message(response="utter_city_old")
#             return []
#         else:
#             if city == None:
#                 dispatcher.utter_message(response="utter_no_city")
#                 return []
#             elif city.lower() == correct_answer_city.lower():
#                 dispatcher.utter_message(response="utter_correct_city", city=correct_answer_city)
#                 return [SlotSet("solution_city", correct_answer_city)]
#             else:
#                 dispatcher.utter_message(response="utter_incorrect_city", city=city)
#                 return [SlotSet("city", None)]


# class ActionVerifyStreet(Action):

#     def name(self) -> Text:
#         return "action_verify_street"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # get slot of last single street guess
#         last_street_guess = tracker.get_slot("last_street_guess")

#         # store story progress slots in local variable
#         solution_city = tracker.get_slot("solution_city")
#         solution_street = tracker.get_slot("solution_street")


#         # respond if city riddle has not yet been solved
#         if solution_city == None:
#             dispatcher.utter_message(response="utter_city_not_street")
#             return []
#         # respond if street riddle has already been solved         
#         elif solution_street != None:
#             dispatcher.utter_message(response="utter_street_old")
#             return []
#         # otherwise progress (user is supposed to work on street riddle)
#         else:

#             # list for detected street values
#             streets = []

#             # assemble solution string of correct intersection
#             solution_string = "{} & {}".format(correct_answer_street_1, correct_answer_street_2)

#             # go through all entities from last message   
#             for entity in tracker.latest_message['entities']:
#                 # check if entity was detected as a street and append text value
#                 if entity['entity'] == 'street':
#                     streets.append(entity['value'])

#             # validate if solution is correct if two streets were given (both have to be correct)
#             if len(streets) == 2:
#                 if streets[0].lower() == correct_answer_street_1.lower() and streets[1].lower() == correct_answer_street_2.lower() or streets[1].lower() == correct_answer_street_1.lower() and streets[0].lower() == correct_answer_street_2.lower():
#                     dispatcher.utter_message(response="utter_correct_intersection", intersection=solution_string)
#                     return [SlotSet("solution_street", "{} & {}".format(correct_answer_street_1, correct_answer_street_2))]
#                 else:
#                     dispatcher.utter_message(response="utter_incorrect_intersection")
#                     return [SlotSet("last_street_guess", None)]

#             # validate if solution is correct if only one street was given
#             elif len(streets) == 1:
#                 # if last_street_guess has no saved value
#                 if last_street_guess == None:
#                     dispatcher.utter_message(response="utter_one_street", street=streets[0])
#                     return [SlotSet("last_street_guess", streets[0])]
#                 # if there was a saved street name
#                 else:
#                     streets.append(last_street_guess)
#                     if streets[0].lower() == correct_answer_street_1.lower() and streets[1].lower() == correct_answer_street_2.lower() or streets[1].lower() == correct_answer_street_1.lower() and streets[0].lower() == correct_answer_street_2.lower():
#                         dispatcher.utter_message(response="utter_correct_intersection", intersection=solution_string)
#                         return [SlotSet("solution_street", "{} & {}".format(correct_answer_street_1, correct_answer_street_2))]
#                     else:
#                         dispatcher.utter_message(response="utter_incorrect_intersection")
#                         return [SlotSet("last_street_guess", None)]
                    
#             # complain if 0 or more than 2 street names were given 
#             else:
#                 dispatcher.utter_message(response="utter_no_two_streets")
#                 return [SlotSet("last_street_guess", None)]





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
