import sqlite3

class Sensor:
    statusReady = False
    statusArmed = False

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
                returnRS['id'] = resultSet[0][0]
                returnRS['hexid'] = resultSet[0][1]
                returnRS['name'] = resultSet[0][2]
                returnRS['type'] = resultSet[0][3]
               
                return returnRS
            else:
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

