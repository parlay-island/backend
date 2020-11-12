def pluralized(s: str) -> str:
    return s + 's'


def id_ize(s: str) -> str:
    return s + '_id'


# Configuration variables
PAGE_SIZE = 10

# Fields
ID = 'id'
PAGE = 'page'
DISTANCE = 'distance'
PLAYER = 'player'
PLAYERS = pluralized(PLAYER)
PLAYER_ID = id_ize(PLAYER)
QUESTION = 'question'
QUESTIONS = pluralized(QUESTION)
QUESTION_ID = id_ize(QUESTION)
CHOICE = 'choice'
CHOICES = pluralized(CHOICE)
CHOICE_ID = id_ize(CHOICE)
RESULT = 'result'
RESULTS = pluralized(RESULT)
USER = 'user'
LEVEL = 'level'
LEVELS = pluralized(LEVEL)
LEVEL_ID = id_ize(LEVEL)
NAME = 'name'
ACCURACY = 'accuracy'
AWARD_LIST = 'award_list'
BODY = 'body'
TIMES_ANSWERED = 'times_answered'
TIMES_CORRECT = 'times_correct'
TIMES_CHOSEN = 'times_chosen'
TAGS = 'tags'
ANSWER = 'answer'
TAG = 'tag'

# Request types
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# Error
ERROR = 'ERROR'
