import pytest
import os
import sys

# Add dags folder to sys path so airflow can parse it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../dags')))

def test_dag_loaded():
    from airflow.models import DagBag
    dagbag = DagBag(dag_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../dags')), include_examples=False)
    
    # Check that there are no import errors
    assert len(dagbag.import_errors) == 0, f"DAG import errors: {dagbag.import_errors}"
    
    dag_id = 'daily_transit_aggregation'
    assert dag_id in dagbag.dags
    
    dag = dagbag.dags[dag_id]
    assert len(dag.tasks) == 2
    
    # Check the idempotency logic
    aggregate_task = dag.get_task('aggregate_delays')
    assert "ON CONFLICT" in aggregate_task.sql
    assert "DO UPDATE" in aggregate_task.sql
