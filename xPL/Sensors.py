import sqlite3

class Sensor:
    status = None
    id = None
    hexid = None
    name = None
    type = None

    try:
        conn = sqlite3.connect('devices.db')
        isConn = True
        print "Connection to devices.db established"
    except:
        isConn = False
        print "DB Connection Failed"

    def __init__(self):
        pass

    def closeDBConn(self):
        if self.isConn == True:
            self.conn.close()
            self.isConn = False
            print "Connection object closed, no DB operations will work unless you sqlite3.connect(db) again."
        else:
            print "Connection Doesn't Exist"

    def getSingleSensor (self, sqlColumn = None, sqlValue = None):
        if self.isConn == False:
            print "You need a DB connection in order to get..."
            return None

        if sqlColumn == 'type':
            print "Use getSensorsOfType(type) function to get all " + sqlValue + " devices"
            return None
        
        if sqlColumn != None and sqlValue != None:
            c = self.conn.cursor()
            queryParams = (sqlValue,)
            query = "select * from sensors where " + sqlColumn + " = ?"
            c.execute(query, queryParams)
            
            resultSet = []
            returnRS = {}

            for row in c:
                resultSet.append(row)


            if len(resultSet) == 1:
                self.id = returnRS['id'] = resultSet[0][0]
                self.hexid = returnRS['hexid'] = resultSet[0][1]
                self.name = returnRS['name'] = resultSet[0][2]
                self.type = returnRS['type'] = resultSet[0][3]
                self.status = returnRS['status'] = resultSet[0][4]
               
                return returnRS
            else:
                print "Query: " + query + ", Params: " + str(queryParams)
                print "Result Set: " + str(resultSet)
                print "Wrong number of records returned (0 or more than 1)"

                return None

        else:
            print "You didn't pass the column and/or value"
            return None

    def getSensorsOfType(self, sensorType):
        if self.isConn == False:
            print "You need a DB connection in order to get..."
            return None

        if sensorType != None:
            c = self.conn.cursor()
            queryParams = (sensorType,)

            if sensorType == "all" or sensorType == "ALL":
                query = "select * from sensors"
                c.execute(query)
            else:
                query = "select * from sensors where type = ?"
                c.execute(query, queryParams)
            
            resultSet = []
            for row in c:
                resultSet.append(row)

            if len(resultSet) == 0:
                print "0 records returned"
                return None
            else:
                print str(len(resultSet)) + " record(s) returned"
                return resultSet

        else:
            print "You didn't pass the column and/or value"
            return None

    def getStatus(self, sensorId = None):
        if self.isConn == False:
            print "You need a DB connection in order to get..."
            return None

        if sensorId != None:
            c = self.conn.cursor()
            queryParams = (sensorId,)
            query = "select status from sensors where id = ?"
            c.execute(query, queryParams)
            
            resultSet = []

            for row in c:
                resultSet.append(row)


            if len(resultSet) == 1:
                self.status = resultSet[0][0]
                return self.status
            else:
                print "Query: " + query + ", Params: " + str(queryParams)
                print "Result Set: " + str(resultSet)
                print "Wrong number of records returned (0 or more than 1)"

                return None

        else:
            print "You didn't pass the ID"
            return None

    def setStatus(self, sensorId = None, sensorStatus = None):
        if self.isConn == False:
            print "You need a DB connection in order to get..."
            return False

        if sensorId != None and sensorStatus != None:
            c = self.conn.cursor()
            queryParams = (sensorId, sensorStatus)
            query = "update sensors set status = ? where id = ?"

            try:
                c.execute(query, queryParams)
                self.conn.commit()
                self.getStatus(sensorId)
                return True
            except:
                print "Update Failed..."
                return False

        else:
            print "You didn't pass the ID"
            return False
