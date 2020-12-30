import logging

logger = logging.getLogger()


class robinhoodRepository:
    def __init__(self, sql_connection):
        self.conn = sql_connection

    def insertStock(self, company, symbol, units, price, avg_cost, total_return, equity, total_gain, allocation, description=None):
        sql = """
        INSERT INTO robinhood_holdings (company, symbol, units, price, avg_cost, total_return, equity, total_gain, allocation)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """
        if None in (company, symbol, units, price, avg_cost, total_return, equity, total_gain, allocation):
            raise Exception("Stock does not contain enough information")
        else:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (company, symbol, units, price, avg_cost, total_return, equity, total_gain, allocation))
            self.conn.commit()

    # def getDaysForSecondDose(self, id):
    #     with self.conn.cursor() as cursor:
    #         sql = 'SELECT min_days_between_doses, max_days_between_doses FROM vaccines WHERE id = %s'
    #         cursor.execute(sql, (id))
    #         days_between_doses = cursor.fetchall()
    #     return days_between_doses[0]

    def getAllStocks(self):
        with self.conn.cursor() as cursor:
            sql = 'SELECT * FROM robinhood_holdings'
            cursor.execute(sql)
            rows = cursor.fetchall()
        return rows

    # def getDateRangeForSecondVaccineFromToken(self, token):
    #     # Gets min_days_between_doses, max_days_between_doses
    #     # Returns a range based on vaccine_date for user
    #     with self.conn.cursor() as cursor:
    #         sql = """
    #         SELECT vaccine_id, vaccine_date, min_days_between_doses, max_days_between_doses, 
    #                DATE_ADD(vaccine_date, INTERVAL min_days_between_doses DAY) as min_date, 
    #                DATE_ADD(vaccine_date, INTERVAL max_days_between_doses DAY) as max_date 
    #                FROM requests JOIN vaccines on requests.vaccine_id = vaccines.id 
    #                WHERE token = %s ORDER BY request_time DESC LIMIT 1;
    #         """
    #         cursor.execute(sql, token)
    #         rows = cursor.fetchall()
    #     if rows:
    #         return rows[0]
    #     else:
    #         return []

