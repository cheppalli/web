import logging
from logging.handlers import RotatingFileHandler

import MySQLdb
import tornado.ioloop
import tornado.options
import tornado.web
import json
import custom_erro as CE
from collections import OrderedDict

class State:
    REQ_INIT        = 0
    REQ_MODIFIED    = 1
    RES_RECEIVED    = 2
    RES_CONSTRUCTED = 3
    REQ_COMPLETE    = 4
    REQ_ERROR       = -1

#tornado.options.options['log_file_prefix'].set( + str(PORT))
#tornado.options.parse_command_line()
class MainHandler(tornado.web.RequestHandler):
    
    '''Common initializations added here'''
    def initialize(self, other_params=None):
        
        self.state=State().REQ_INIT
        self.db=''
        self.cursor=''
        try:  
            # Open database connection
            self.db = MySQLdb.connect("127.0.0.1","root","","test" )
            logger.info("Database connection Established")
            # prepare a cursor object using cursor() method
            self.cursor = self.db.cursor()
            
        except Exception as e:
            self.state=State().REQ_ERROR
            logger.info("Error: %s"%e)
            logger.info("Database Connection is not established")
            self.state=State().REQ_ERROR
            response = CE.get_response(self, 100, "Database Connection is not established")
            self.send_error(**response)

    @tornado.gen.coroutine
    def write_error(self, status_code, **kwargs):
        response_dict = kwargs.get('response')
        http_status_code = response_dict.get('status')
        self.set_status(http_status_code)
        self.write(json.dumps(response_dict))


    def on_finish(self):
        # disconnect from server
        self.db.close()
        logger.info("Connection closed")

    def json_to_dict(self, json_string):
        response_dict={}
        try:
            response_dict = json.loads(json_string)
        except ValueError, error:
            logger.info("Improper content in request body")
            self.state=State().REQ_ERROR
            response = CE.get_response(self, 100, "Improper json in request body")
            self.send_error(**response)
        return response_dict
   
    @tornado.gen.coroutine
    def get(self):
        if self.state==State().REQ_INIT:     
            data=OrderedDict()
            data["First_Name"]=[]
            sql = "SELECT * FROM EMPLOYEE WHERE FIRST_NAME = %s"
            name=self.request.arguments.get("name",None)
            try:
                if name:
                    # Execute the SQL command
                    self.check=False
                    self.cursor.execute(sql,self.request.arguments.get("name",""))
                    logger.info("Query Executed")
                    self.state=State().RES_RECEIVED
                    for row in self.cursor:
                        self.check=True
                        fname = row[0]
                        data["First_Name"].append(fname) 
                        logger.info("Response %s"%data)
                    self.state=State().RES_CONSTRUCTED
                else:
                    logger.info("Name parameter is mandatory")
                    self.state=State().REQ_ERROR
                    error_resp=CE.get_response(self, 100, error_msg="Name parameter is not passed")
                    self.send_error(**error_resp)
            except Exception as e:
                logger.info("Error: %s"%e)
                error_resp=CE.get_response(self, 100, error_msg=str(e))
                self.send_error(**error_resp)
            if self.state!=State().REQ_ERROR and self.state==State().RES_CONSTRUCTED:
                if self.check:
                    self.write(json.dumps({"Resonse":data}))
                else:
                    self.write(json.dumps({"Resonse":"Record not found"}))
                        
    @tornado.gen.coroutine
    def post(self):
        if self.state==State().REQ_INIT:
            body_dict=self.json_to_dict(self.request.body)
            name=''
            if body_dict and body_dict.get("name",None): #and type(body_dict.get("name",None))==type(""):
                name=body_dict.get("name",'')
                # Prepare SQL query to INSERT a record into the database.
                sql = "INSERT INTO EMPLOYEE(FIRST_NAME) VALUES ('%s')" %(name)
                try:
                   # Execute the SQL command
                   self.cursor.execute(sql)
                   logger.info("Query Executed")
                   # Commit your changes in the database
                   self.db.commit()
                   logger.info("Commited")
                   self.state=State().RES_CONSTRUCTED
                except Exception as e:
                    logger.info("Exception: %s" %e)
                    self.state=State().REQ_ERROR
                    # Rollback in case there is any error
                    self.db.rollback()
                    logger.info("Error Rollbacking")
                    error_resp=CE.get_response(self, 100, error_msg=str(e))
                    self.send_error(**error_resp)
            else:
                logger.info("Empty or Incorrect Request body")
                self.state=State().REQ_ERROR
                error_resp=CE.get_response(self, 100, error_msg="Empty or Incorrect Request body")
                self.send_error(**error_resp)
            if self.state!=State().REQ_ERROR and self.state==State().RES_CONSTRUCTED:
                self.write(json.dumps({"Record Inserted":name}))
                self.set_header("Content-Type", "application/json")
                self.set_header("Accept-Ranges", "bytes")

        
    @tornado.gen.coroutine
    def put(self):
        sql = """CREATE TABLE EMPLOYEE (FIRST_NAME  VARCHAR(1000))"""
        logger.info("Table Created")
        try:
            self.cursor.execute(sql)
        except Exception as e:
            logger.info("Exception at Table creation: %s "%e)
            self.state=State().REQ_ERROR
            error_resp=CE.get_response(self, 100, error_msg=e)
            self.send_error(**error_resp)
        if self.state!=State().REQ_ERROR:   
            self.write(json.dumps({"Response":"Created a Table"}))
        
    @tornado.gen.coroutine
    def delete(self):
        if self.state==State().REQ_INIT:   
            body_dict=self.json_to_dict(self.request.body)
            name=''
            if body_dict and body_dict.get("name",None):
                name=body_dict.get("name",'')
                # Prepare SQL query to DELETE required records
                sql = "DELETE FROM EMPLOYEE WHERE FIRST_NAME =%s"
                try:
                   sql1 = "SELECT * FROM EMPLOYEE WHERE FIRST_NAME = %s"
                   self.cursor.execute(sql1,(name,))
                   check=self.cursor.fetchone()
                   print check
                   if check:
                       self.deleted=True
                   else:
                       self.deleted=False
                   # Execute the SQL command
                   self.cursor.execute(sql,(name,))
                   # Commit your changes in the database
                   self.db.commit()
                   logger.info("Deleted the entry")
                except Exception as e:
                    logger.info("Exception: %s"%e)
                    self.state=State().REQ_ERROR
                    # Rollback in case there is any error 
                    self.db.rollback()
                    error_resp=CE.get_response(self, 100, error_msg=e)
                    self.send_error(**error_resp)
                    
            if self.state!=State().REQ_ERROR:
                if self.deleted:
                    self.write(json.dumps({"Deleted entry":name}))
                else:
                    self.write(json.dumps({"Message":"No Entry Found to Delete"}))
        
 
application = tornado.web.Application([(r"/mainhand", MainHandler),])
if __name__ == "__main__":
    fmt=logging.Formatter('[%(asctime)s; %(filename)s:%(lineno)d] %(levelname)s:%(name)s msg:%(message)s ', datefmt="%Y-%m-%d %H:%M:%S")
    handler = RotatingFileHandler('/Users/sgumpalli/Documents/gumpalli/logs/logg.log', maxBytes=10000000,
                                  backupCount=5)
    handler.setFormatter(fmt)
    logger=logging.getLogger("application.py")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()