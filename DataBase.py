from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId


class Database:

    def __init__(self):
        """
        Initialize the Database class with a MongoClient, database, and collection.
        """
        self.__private__client = MongoClient()
        self.__private__db = self.__private__client['grad']
        self.__private__collections = self.__private__db['users']

    def insertUser(self, doc):
        """
        Insert a new user document into the 'users' collection.

        Parameters:
        - doc (dict): The user document to insert.

        Returns:
        - str: A status message indicating the success or failure of the operation.
        """
        try:
            self.__private__collections.insert_one(doc)
            return "Done !!"
        except DuplicateKeyError:
            return "Duplicated name or email"

    def insertVideo(self, id, name, path):
        """
        Insert a new video document into the 'videos' array of a user.

        Parameters:
        - id (str): The ObjectId of the user.
        - name (str): The name of the video.
        - path (str): The path to the video file.

        Returns:
        - str: A status message indicating the success or failure of the operation.
        """
        doc = {"name": name, "path": path}
        if self.__private__collections.count_documents({'_id': ObjectId(id), 'videos.name': name}, limit=1) == 0:
            self.__private__collections.update_one({'_id': ObjectId(id)}, {'$addToSet': {'videos': doc}})
            return "Video inserted successfully!"
        else:
            return f"Video with name '{name}' already exists. Video not inserted."

    def insertPowerPoint(self, id, name, path):
        """
        Insert a new PowerPoint document into the 'pptx' array of a user.

        Parameters:
        - id (str): The ObjectId of the user.
        - name (str): The name of the PowerPoint presentation.
        - path (str): The path to the PowerPoint file.

        Returns:
        - str: A status message indicating the success or failure of the operation.
        """
        doc = {"name": name, "path": path}
        if self.__private__collections.count_documents({'_id': ObjectId(id), 'pptx.name': name}, limit=1) == 0:
            self.__private__collections.update_one({'_id': ObjectId(id)}, {'$addToSet': {'pptx': doc}})
            return "PowerPoint inserted successfully!"
        else:
            return f"PowerPoint with name '{name}' already exists. PowerPoint not inserted."

    def getVideos(self, id):
        """
        Retrieve all videos associated with a user.

        Parameters:
        - id (str): The ObjectId of the user.

        Returns:
        - dict: A dictionary containing video names as keys and their paths as values.
        """
        videos = self.__private__collections.find_one({'_id': ObjectId(id)}, {"videos": 1})
        dic = {}
        if len(videos) > 1:
            for video in videos['videos']:
                dic[video['name']] = video['path']
        return dic

    def getPowerPoint(self, id):
        """
        Retrieve all PowerPoint presentations associated with a user.

        Parameters:
        - id (str): The ObjectId of the user.

        Returns:
        - dict: A dictionary containing PowerPoint names as keys and their paths as values.
        """
        pp = self.__private__collections.find_one({'_id': ObjectId(id)}, {"pptx": 1})
        dic = {}
        if len(pp) > 1:
            for video in pp['pptx']:
                dic[video['name']] = video['path']
        return dic

    def getIdByName(self, name):
        """
        Retrieve the ObjectId of a user by their name.

        Parameters:
        - name (str): The name of the user.

        Returns:
        - str or int: The ObjectId of the user or -1 if not found.
        """
        try:
            doc = self.__private__collections.find_one({'name': name})
            return doc['_id']
        except:
            return '-1'

    def getIdbyEmail(self, email):
        """
        Retrieve the ObjectId of a user by their email.

        Parameters:
        - email (str): The email of the user.

        Returns:
        - str or int: The ObjectId of the user or -1 if not found.
        """
        try:
            doc = self.__private__collections.find_one({'email': email})
            return doc['_id']
        except:
            return '-1'

    def getUser(self, id):
        """
        Retrieve a user document by their ObjectId.

        Parameters:
        - id (str): The ObjectId of the user.

        Returns:
        - dict: The user document.
        """
        doc = self.__private__collections.find_one({'_id': ObjectId(id)})
        return doc

    def updatePass(self, email, newpass):

        query = {"email": email}
        new_values = {"$set": {"password": newpass}}
        result = self.__private__collections.update_one(query, new_values)
        if result.modified_count == 1:
            return True
        else:
            return False

    def updateSalt(self, email, newsalt):

        query = {"email": email}
        new_values = {"$set": {"salt": newsalt}}
        result = self.__private__collections.update_one(query, new_values)
        if result.modified_count == 1:
            return True
        else:
            return False

    def deleteVideo(self, id, videoname):

        object_id = ObjectId(id)
        update_operation = {
            '$pull': {
                'videos': {'name': videoname}
            }
        }
        self.__private__collections.update_one({'_id': object_id}, update_operation)

    def deletePowerPoint(self, id, ppname):

        object_id = ObjectId(id)
        update_operation = {
            '$pull': {
                'pptx': {'name': ppname}
            }
        }
        self.__private__collections.update_one({'_id': object_id}, update_operation)

    def updateGender(self, id, gender):

        object_id = ObjectId(id)
        update_operation = {
            '$set': {
                'gender': gender
            }
        }
        self.__private__collections.update_one({'_id': object_id}, update_operation)

    def updateAge(self, id, age):

        object_id = ObjectId(id)
        update_operation = {
            '$set': {
                'age': age
            }
        }
        self.__private__collections.update_one({'_id': object_id}, update_operation)

    def updateName(self, id, name):

        object_id = ObjectId(id)
        update_operation = {
            '$set': {
                'name': name
            }
        }
        self.__private__collections.update_one({'_id': object_id}, update_operation)

    def updateEmail(self, id, email):

        object_id = ObjectId(id)
        update_operation = {
            '$set': {
                'email': email
            }
        }
        self.__private__collections.update_one({'_id': object_id}, update_operation)

