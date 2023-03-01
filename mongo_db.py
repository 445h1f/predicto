from pymongo import MongoClient
from datetime import datetime

# creating connection with mongo db
mongo = MongoClient(host="localhost:27017")

db = mongo["predicto"] # getting the database
predictons = db["predictions"] # getting predicto collection from database
users = db["users"]



class PredictoData:
    """Class to manage data for predictions. """

    __VALID_KEYS = ["from_user", "pair",  "direction", "timeframe", "old_price", "new_price", "start_price", "price_change", "start_time", "end_time", "inserted_at", "updated_at", "status", "profit"]

    def __init__(self) -> None:
        self.__getAllData()

    def __filterData(self, data:dict):
        """Removes invalid key in data by checking each in specified valid keys list."""

        # creating deep copy of data for deleting
        filterdData = data.copy()
        # checking each key in details
        for key in data:
            if key not in self.__VALID_KEYS:
                # deleting invalid keys
                del filterdData[key]

        return filterdData # returning filtered data

    def __getAllData(self):
        """Returns all data in predicto collection."""

        allData = [] # list to add all documents

        find = predictons.find({}) #getting all documents

        # adding all documents from search
        for doc in find:
            allData.append(doc)

        # print(allData)

        return allData

    def addPredictionData(self, data:dict):
        """Add prediction detail to mongo db. Removes not allowed keys in data."""

        # inserting time key in document
        data["inserted_at"] = datetime.now()
        data["updated_at"] = None

        # removing unallowed keys
        data = self.__filterData(data)

        # adding data in db
        add = predictons.insert_one(data)
        return add.inserted_id

    def updatePredictionData(self, id, data:dict):
        """Updates the prediction document if provided id is valid else returns false."""

        # checking user id
        check = predictons.find_one(id)
        if check:
            # adding updated time to data
            data["updated_at"] = datetime.now()

            # filtering data
            data = self.__filterData(data)

            # updating data of prediction id
            predictons.update_one({"_id":id}, {"$set": data})
            return True
        else:
            return False


class PredictoUser:

    __USER_ID_START = 100_000_000

    def __init__(self, userId:int=None) -> None:
        # if user id is none creating new user
        # print("Init fired of predicto user")
        # print(userId)
        if userId is None:
            self.id = self.addUser()
        else:
            # verifying user id is it is not none
            # print("else part")
            verify = self.verifyUser(userId)
            # if verified then assigning user id to id attribute
            if verify:
                self.id = verify
            else:
                # creating user
                self.id = self.addUser()
            # else user id attribute will not be assigned



    def verifyUser(self, userId:int):
        """Verifies whether user id is in collection or not"""
        # querying mongodb to find document assciated with given _id value
        check = users.find_one({"_id": userId})
        # print(f'check user result' , check)
        if check:
            # means userId exits so returning True
            return check["_id"]
        else:
            # else returning false in case of user id not found
            return False


    def __generateUserId(self):
        """Generates user id for new user by checking if it is already not in db."""
        # getting total count of users
        totalUsers = users.count_documents({})
        newUserId = self.__USER_ID_START + totalUsers + 1
        return newUserId

    def getUserData(self):
        """Returns user data."""
        return users.find_one({"_id" : self.id})


    def addUser(self):
        """Adds user to database and returns user id of added user."""
        # user data schema that is to be added in database
        userDataSchema = {
            "_id": self.__generateUserId(),
            "balance": 1000,
            "predictions": [],
            "stats" : {
                "predicted_pairs" : {},
                "total_predictions": 0,
                "total_wins": 0,
                "total_losses": 0,
                "total_draws": 0,
                "total_profit" : 0
            },
            "created_at" : datetime.now(),
            "updated_at" : datetime.now()
        }

        # adding user to database
        add = users.insert_one(userDataSchema)
        return add.inserted_id # returning user id of user


    def addUserPrediction(self, pairName:str, predictionId):
        """Updates prediction stats of of given pair."""
        # changing pair name to uppercase for matching case
        pairName = pairName.upper()

        # getting all data of user
        userData = self.getUserData()
        stats = userData["stats"] # stat dict
        pairs = stats["predicted_pairs"] # pair dict

        userData["predictions"].append(predictionId) # adding prediction id to array

        # checking if pairName is in users predicted pair
        if pairName in pairs:
            # yes, so incrementing pairName count by 1
            pairs[pairName]["count"] += 1
        else:
            # no, so adding pairName in users predicted pairs and setting count to 1
            pairs[pairName] = {
                "count" : 1,
                "wins" : 0,
                "losses" : 0,
                "draws": 0,
                "profit": 0,
            }

        stats["total_predictions"] += 1 # incrementing total predictions by 1
        userData["updated_at"] = datetime.now() # updating document update time

        # updating stats
        users.update_one({"_id" : self.id}, {"$set" : userData})


    def updatePredictionResult(self, pairName:str, status:str, profit:float):
        """Updates prediction result of user."""
        # changing case to match with case
        status = status.lower()
        pairName = pairName.upper()

        # checking is status is valid else returning false
        if status not in ["won", "loss", "draw"]:
            return {"error": "invalid result status"}

        # getting data for updating stats
        userData = self.getUserData()
        stats = userData["stats"]
        pairStats = stats["predicted_pairs"][pairName]

        stats["total_profit"] += profit # updating total profit
        pairStats["profit"] += profit #updating pair profit
        userData["balance"] += profit

        if status == "win":
            # updating stat for win
            stats["total_wins"] += 1 # incrementing total wins
            pairStats["wins"] += 1 # incrementing pair wins
        elif status == "loss":
            # updating stat for loss
            stats["total_losses"] += 1 # incrementing total losses
            pairStats["losses"] += 1 # incrementing pair losses
        else:
            # for draw
            stats["total_draws"] += 1 # incrementing total draws
            pairStats["draws"] += 1 # incrementing pair wins

        userData["updated_at"] = datetime.now() # updating document update time

        # updating stats
        users.update_one({"_id" : self.id}, {"$set" : userData})



if __name__ == "__main__":
    user = PredictoUser()
    print(user.id)