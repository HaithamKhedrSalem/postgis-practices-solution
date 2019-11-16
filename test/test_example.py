from .dbtest import (
    DbTest,
    dbconnect
)

import os
from psycopg2.extras import (
    RealDictCursor,
    RealDictRow
)


PATH_TO_SQL_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "sql"
    )
)

class TestExample(DbTest):
    @dbconnect
    def test_select_organizations(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "organizations.sql")
        )

        sql = """
        SELECT * FROM organizations;
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            organizations = cur.fetchall()
            
            assert len(organizations) == 7

    @dbconnect
    def test_count_the_number_of_subordinates(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "organizations.sql")
        )

        sql = """
        SELECT COUNT(enterprise_sales_enterprise_customers.sales_organization_id) as subordinates_count, organizations."id" from organizations
        LEFT JOIN enterprise_sales_enterprise_customers ON organizations.id=enterprise_sales_enterprise_customers.sales_organization_id
        GROUP BY enterprise_sales_enterprise_customers.sales_organization_id, organizations."id" ORDER BY organizations."id";
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            actual = cur.fetchall()
            assert len(actual) == 7
            assert actual == [
                RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 1,
                })
                , RealDictRow(**{
                    "subordinates_count": 4,
                    "id": 2,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 3,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 4,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 5,
                })
                , RealDictRow(**{
                    "subordinates_count": 1,
                    "id": 6,
                })
                , RealDictRow(**{
                    "subordinates_count": 0,
                    "id": 7,
                })
            ]

    @dbconnect
    def test_calculate_center_of_each_segment(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "japan_segments.sql")
        )

        sql = """
        SELECT sub_query.id, ST_X(sub_query.bounds_center) as longitude, ST_Y(sub_query.bounds_center) as latitude
        FROM (SELECT japan_segments.id as id, st_centroid(bounds) as bounds_center FROM japan_segments) as sub_query;
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            actual = cur.fetchall()
            assert len(actual) == 10
            assert actual == [
                RealDictRow(**{
                    "id": "KAGOSHIMA_1",
                    "longitude": 130.642228315775,
                    "latitude": 30.7045454545455,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_2",
                    "longitude": 130.694183864916,
                    "latitude": 30.7045454545455,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_3",
                    "longitude": 130.746139414057,
                    "latitude": 30.7045454545455,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_4",
                    "longitude": 129.707028431231,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_5",
                    "longitude": 129.758983980373,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_6",
                    "longitude": 129.810939529514,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_7",
                    "longitude": 129.862895078655,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_8",
                    "longitude": 129.914850627797,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_9",
                    "longitude": 129.966806176937,
                    "latitude": 30.75,
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_10",
                    "longitude": 130.018761726079,
                    "latitude": 30.75,
                })
            ]

    @dbconnect
    def test_segments_using_geojson_boundary(self, conn):
        self.load_fixtures(
            conn,
            os.path.join(PATH_TO_SQL_DIR, "japan_segments.sql")
        )

        sql = """
        SELECT sub.id from (SELECT * from japan_segments, (SELECT ST_GeomFromEWKT('SRID=4326;POLYGON((130.27313232421875 30.519681272749402,131.02020263671875 30.519681272749402,
        131.02020263671875 30.80909017893796,130.27313232421875 30.80909017893796,130.27313232421875 30.519681272749402))') as boundary) as sub_query) as sub where ST_Contains(sub.boundary, sub.bounds)
        """
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            actual = cur.fetchall()
            print(actual)
            assert len(actual) == 3
            assert actual == [
                RealDictRow(**{
                    "id": "KAGOSHIMA_1",
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_2",
                })
                , RealDictRow(**{
                    "id": "KAGOSHIMA_3",
                })
            ]
