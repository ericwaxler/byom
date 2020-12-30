import boto3
import pymysql
import os
import json

from repo.robinhoodrepository import robinhoodRepository

import logging
logging.basicConfig(format='%(asctime)s - %(name)s %(levelname)s - %(message)s',level=logging.DEBUG)
logger = logging.getLogger()
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('botocore.credentials').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)


class SQLHelper:
    def __init__(self, region_name='us-east-1', timezone='-5:00'):
        self.username = self._getUsername()
        self.DBName = self._getDBName()
        self.region_name = region_name
        self.DBHost = self._getHost()

        self.timezone = timezone

    def getConnection(self):
        logger.debug(f"Connecting to MySQL: {self.DBHost} on {self.region_name} as: {self.username}, DB: {self.DBName}")

        connect_kwargs = {
            'host': self.DBHost,
            'user': self.username,
            'db': self.DBName,
            'password': self.getSecret(),
            'cursorclass': pymysql.cursors.DictCursor,
            'init_command': f"SET SESSION time_zone='{self.timezone}'"
        }

        # Check if we're running in a lambda
        if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
            connect_kwargs['ssl'] = {'ca': '/opt/rds-ca-2019-root.pem'}

        # Connect
        return pymysql.connect(**connect_kwargs)

    def _getUsername(self):
        return os.environ.get("DBUsername")

    def _getHost(self):
        # Check if we're in a lambda, else use a local tunnel (See README)
        if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
            return os.environ.get("DBHost")
        else:
            return "127.0.0.1"

    def _getDBName(self):
        return os.environ.get("DBName")

    def _listSecrets(self):
        print(self.secretmanager.list_secrets())

    def getSecret(self):
        if os.environ.get("DBPasswd", None):
            return os.environ.get("DBPasswd")
        secretManager = boto3.client('secretsmanager', region_name=self.region_name)
        secretName = ""
        if os.environ.get("SecretName") is not None:
            secretName = os.environ.get("SecretName")
        else:
            secretName = "BYOM"
        SecretString = secretManager.get_secret_value(SecretId=secretName)['SecretString']
        return json.loads(SecretString)["password"]

    def _createTables(self, conn):
        robinhoodTable = """
        CREATE TABLE IF NOT EXISTS robinhood_holdings (
            stock_id      integer NOT NULL AUTO_INCREMENT,
            company     varchar(100),
            symbol        varchar(5),
            units    double,
            price     double,
            avg_cost         double,
            total_return  double,
            equity         double,
            total_gain         double,
            allocation         float,
            PRIMARY KEY ( stock_id ),
            INDEX ( stock_id )
        );
        """

        with conn.cursor() as cursor:
            logger.info("Creating table (if not exists): robinhood_holdings")
            logger.debug(robinhoodTable)
            cursor.execute(robinhoodTable)
        conn.commit()

    def _fieldInTable(self, table_name, field_name):
        conn = self.getConnection()
        with conn.cursor() as cursor:
            sql = "SELECT COLUMN_NAME FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE TABLE_NAME = %s"
            cursor.execute(sql, table_name)
        table_def = cursor.fetchall()
        for i in table_def:
            if i["COLUMN_NAME"].lower() == field_name.lower():
                return True
        return False

    # def _executeAlter(self, table_name, field_name, field_type):
    #     if not table_name.replace("_", "").isalpha() or not field_name.replace("_", "").isalpha() or not field_type.replace("(", "").replace(")", "").isalnum():
    #         raise Exception("you have malformed inputs for either table_name, field_name or field_type.")
    #     conn = self.getConnection()
    #     try:
    #         with conn.cursor() as cursor:
    #             sql = "ALTER TABLE %s ADD COLUMN %s %s" % (table_name, field_name, field_type.upper())
    #             logger.debug(sql)
    #             cursor.execute(sql)
    #             conn.commit()
    #             logger.info(f"Executed ALTER statement on {table_name}, added column: {field_name} {field_type.upper()}")
    #     finally:
    #         conn.close()


    def setupTables(self):
        conn = self.getConnection()
        try:
            with conn.cursor() as cursor:
                sql = 'SHOW TABLES'
                cursor.execute(sql)
                tables = cursor.fetchall()

                logger.info("Setting up Tables")
                self._createTables(conn)

        finally:
            conn.close()

    def dropTables(self):
        # Only for development
        logger.info("Dropping tables")
        conn = self.getConnection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS robinhood_holdings ;")
            conn.commit()
        finally:
            conn.close()


def populateTestData(helper):
    # Vaccines fill-up
    robinhood = robinhoodRepository(helper.getConnection())
    robinhood.insertStock(company="CrowdStrike Holdings", symbol="CRWD", units="30", price="222.15", avg_cost="51.4676", total_return="5120.472", equity="6664.5", total_gain="331.6308", allocation="15.4322")  # These values are just a placeholder for now. Verify them.
    robinhood.insertStock(company="Sony", symbol="SNE", units="6.021219", price="96.2601", avg_cost="58.9897", total_return="224.4132", equity="579.6031", total_gain="63.1812", allocation="1.3421")
    robinhood.insertStock(company="JPMorgan Chase", symbol="JPM", units="11.100124", price="124.4899", avg_cost="92.0638", total_return="359.9337", equity="1381.8533", total_gain="35.2213", allocation="3.1998")
    robinhood.insertStock(company="Virgin Galactic Holdings", symbol="SPCE", units="30", price="25.83", avg_cost="16.4468", total_return="281.496", equity="774.9", total_gain="57.0518", allocation="1.7943")
    robinhood.insertStock(company="Okta", symbol="OKTA", units="4", price="275.6", avg_cost="101.035", total_return="698.26", equity="1102.4", total_gain="172.7768", allocation="2.5527")  
    robinhood.insertStock(company="Bristol-Myers Squibb", symbol="BMY", units="10.150651", price="61.095", avg_cost="43.4484", total_return="179.1245", equity="620.154", total_gain="40.6151", allocation="1.436")
    robinhood.insertStock(company="Disney", symbol="DIS", units="9", price="173.73", avg_cost="134.6656", total_return="351.5796", equity="1563.57", total_gain="29.0084", allocation="3.6206")
    robinhood.insertStock(company="Tesla", symbol="TSLA", units="10", price="660", avg_cost="46.078", total_return="6139.22", equity="6600", total_gain="1332.3538", allocation="15.2829")
    robinhood.insertStock(company="Microsoft", symbol="MSFT", units="9.022068", price="222.5", avg_cost="160.6626", total_return="557.9012", equity="2007.4101", total_gain="38.489", allocation="4.6483")
    robinhood.insertStock(company="Visa", symbol="V", units="10.044366", price="208.7", avg_cost="169.8404", total_return="390.32", equity="2096.2592", total_gain="22.8801", allocation="4.8541")
    robinhood.insertStock(company="Seagate Technology", symbol="STX", units="10", price="62.95", avg_cost="53.528", total_return="94.22", equity="629.5", total_gain="17.602", allocation="1.4577")
    robinhood.insertStock(company="ProShares S&P 500 Dividend Aristocrats ETF", symbol="NOBL", units="31.150722", price="78.98", avg_cost="73.1975", total_return="180.129", equity="2460.284", total_gain="7.8999", allocation="5.697")
    robinhood.insertStock(company="Square", symbol="SQ", units="12", price="228.135", avg_cost="171.9184", total_return="674.5992", equity="2737.62", total_gain="32.6996", allocation="6.3392")
    robinhood.insertStock(company="NextEra Energy", symbol="NEE", units="20.069832", price="74.41", avg_cost="74.4889", total_return="-1.5835", equity="1493.3962", total_gain="-0.1059", allocation="3.4581")
    robinhood.insertStock(company="Vanguard High Dividend Yield ETF", symbol="VYM", units="13.999683", price="90.38", avg_cost="81.1683", total_return="128.9609", equity="1265.2913", total_gain="11.3489", allocation="2.9299")
    robinhood.insertStock(company="CareTrust REIT", symbol="CTRE", units="30.863452", price="22.33", avg_cost="20.5706", total_return="54.3012", equity="689.1809", total_gain="8.553", allocation="1.5959")
    robinhood.insertStock(company="Brookfield Infrastructure", symbol="BIP", units="10.093859", price="50.23", avg_cost="45.501", total_return="47.7339", equity="507.0145", total_gain="10.3932", allocation="1.174")
    robinhood.insertStock(company="Coca-Cola", symbol="KO", units="8.072422", price="53.4999", avg_cost="40.8452", total_return="102.1541", equity="431.8738", total_gain="30.9821", allocation="1")
    robinhood.insertStock(company="Apple", symbol="AAPL", units="10", price="131.98", avg_cost="72.466", total_return="595.14", equity="1319.8", total_gain="82.1268", allocation="3.0561")
    robinhood.insertStock(company="Mastercard", symbol="MA", units="6.006107", price="336", avg_cost="265.523", total_return="423.2924", equity="2018.052", total_gain="26.5427", allocation="4.673")
    robinhood.insertStock(company="Waste Management", symbol="WM", units="5.074384", price="117", avg_cost="100.2328", total_return="85.0832", equity="593.7029", total_gain="16.7283", allocation="1.3748")
    robinhood.insertStock(company="Raytheon Technologies", symbol="RTX", units="20.295389", price="70.27", avg_cost="62.2663", total_return="162.4382", equity="1426.157", total_gain="12.854", allocation="3.3024")
    robinhood.insertStock(company="AMD", symbol="AMD", units="5", price="91.5", avg_cost="52.46", total_return="195.2", equity="457.5", total_gain="74.4186", allocation="1.0594")
    robinhood.insertStock(company="Schrodinger", symbol="SDGR", units="3", price="83.5", avg_cost="73.76", total_return="29.22", equity="250.5", total_gain="13.205", allocation="0.5801")
    robinhood.insertStock(company="Cloudflare", symbol="NET", units="12", price="84.5", avg_cost="34.22", total_return="603.36", equity="1014", total_gain="146.9316", allocation="2.348")
    robinhood.insertStock(company="Palantir Technologies", symbol="PLTR", units="10", price="27.76", avg_cost="27.729", total_return="0.31", equity="277.6", total_gain="0.1118", allocation="0.6428")
    robinhood.insertStock(company="Nano-X Imaging", symbol="NNOX", units="8", price="52.98", avg_cost="42.94", total_return="80.32", equity="423.84", total_gain="23.3815", allocation="0.9814")
    robinhood.insertStock(company="Salesforce", symbol="CRM", units="3", price="225.5", avg_cost="226.29", total_return="-2.37", equity="676.5", total_gain="-0.3491", allocation="1.5665")




    logger.info("------DUMPING Database Information for debugging purposes")
    logger.info(f"Requests: {robinhood.getAllStocks()}\n")
    #logger.info(f"Sample Employee ID: {requests.getExistingRequestsForEmployee('TEST-04534')}\n")


# Testing/Debug only
if __name__ == "__main__":
    helper = SQLHelper()
    helper.dropTables()
    helper.setupTables()
    populateTestData(helper)
