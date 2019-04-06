'''
Migrate from initial schema to the model formed in dbext.
This includes moving away from JSON columns to more tables
with metrics and attributes for measurement instances.
'''

import logging
from netspryte.manager import Manager, MeasurementInstance


def up(mgr):
    with mgr.database.atomic() as txn:
        try:
            mgr.database.execute_sql("ALTER TABLE measurement_instance ADD COLUMN title character varying(255)")
            mgr.database.execute_sql("ALTER TABLE measurement_instance ADD COLUMN description character varying(255)")
            cursor = mgr.database.execute_sql("SELECT id, presentation->'title', presentation->'description' from measurement_instance")
            for id, title, descr, in cursor:
                MeasurementInstance.update(title=title, description=descr).where(MeasurementInstance.id==id).execute()
            mgr.database.execute_sql("ALTER TABLE measurement_instance DROP COLUMN attrs")
            mgr.database.execute_sql("ALTER TABLE measurement_instance DROP COLUMN metrics")
            mgr.database.execute_sql("ALTER TABLE measurement_instance DROP COLUMN presentation")
        except Exception as e:
            logging.error("failed to run transaction: %s", str(e))
            txn.rollback()
            return False
    mgr.create_tables()
    return True


def down(mgr):
    with mgr.database.atomic() as txn:
        try:
            mgr.database.execute_sql("ALTER TABLE measurement_instance ADD COLUMN attrs JSONB")
            mgr.database.execute_sql("ALTER TABLE measurement_instance ADD COLUMN metrics JSONB")
            mgr.database.execute_sql("ALTER TABLE measurement_instance ADD COLUMN presentation JSONB")
            cursor = mgr.database.execute_sql("SELECT id, title, description from measurement_instance")
            for id, title, descr, in cursor:
                title = title or ""
                descr = descr or ""
                mgr.database.execute_sql("UPDATE measurement_instance SET presentation = " +
                                         "'{\"title\": \"" + title + "\", " +
                                         "\"description\": \"" + descr + "\"}'::json " +
                                         "WHERE id = %s" % (id))
            mgr.database.execute_sql("ALTER TABLE measurement_instance DROP COLUMN title")
            mgr.database.execute_sql("ALTER TABLE measurement_instance DROP COLUMN description")
            mgr.database.execute_sql("DROP TABLE host_snmp_attrs")
            mgr.database.execute_sql("DROP TABLE ipaddress_attrs")
            for tbl in ["interface", "cbqos", "hostups"]:
                mgr.database.execute_sql("DROP TABLE %s_attrs" % tbl)
                mgr.database.execute_sql("DROP TABLE %s_metrics" % tbl)
                logging.warn("removed tables related to attributes and metrics")
        except Exception as e:
            logging.error("failed to run transaction: %s", str(e))
            txn.rollback()
            return False
    return True
