from Sensors import Sensor
import sqlite3

class Zone:
    statusReady = False
    statusArmed = False
    sensors = {}
    id = None
    name = None

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

    def getZoneById (self, sqlValue = None):
        if self.isConn == False:
            print "You need a DB connection in order to get..."
            return None

        if sqlValue != None:
            c = self.conn.cursor()
            queryParams = (sqlValue,)
            query = "select * from zones where id = ?"
            c.execute(query, queryParams)
            
            resultSet = []
            returnRS = {}

            for row in c:
                resultSet.append(row)


            if len(resultSet) == 1:
                self.id = returnRS['id'] = resultSet[0][0]
                self.name = returnRS['name'] = resultSet[0][1]
               
                return returnRS
            else:
                print "Wrong number of records returned (0 or more than 1)"
                return None

        else:
            print "You didn't pass the value"
            return None

    def getZoneByName (self, sqlValue = None):
        if self.isConn == False:
            print "You need a DB connection in order to get..."
            return None

        if sqlValue != None:
            c = self.conn.cursor()
            queryParams = (sqlValue,)
            query = "select * from zones where name = ?"
            c.execute(query, queryParams)
            
            resultSet = []

            for row in c:
                resultSet.append(row)

            if len(resultSet) == 1:
                self.id = resultSet[0][0]
                self.name = resultSet[0][2]
              
                return None # No Need To Return Anything, Even On Positive Outcume
            else:
                print "Wrong number of records returned (0 or more than 1)"
                return None

        else:
            print "You didn't pass the value"
            return None

    def getLinkedSensors (self):
        if self.isConn == False:
            print "You need a DB connection in order to get..."
            return None

        c = self.conn.cursor()
        queryParams = (self.id,)
        query = "select s.hexid from zones z, sensors s, zones_sensors_linked zsl where zsl.zoneid= ? and zsl.sensorid = s.id and zsl.zoneid = z.id"
        c.execute(query, queryParams)
            
        resultSet = []
        sensorHexIds = []

        for row in c:
            resultSet.append(row)
        
        for sHexIds in resultSet:
            sensorHexIds.append(sHexIds[0])

        for sHexId in sensorHexIds:
            s = Sensor()
            s.getSingleSensor('hexid', sHexId)
            self.sensors[sHexId] = s
            del s

    def isReady(self):
        for sensor in self.sensors:
            status = sensor.getStatus(sensor.id)
            if status == "alert":
                print "Sensor: " + sensor.name + "Reported Alert Status."
                self.statusReady = False
                return False
        print "All Sensors Reported Normal Status"
        self.statusReady = True
        return True
