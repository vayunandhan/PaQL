import sys
import time
import pandas as pd
import pulp
from sqlalchemy import create_engine
from src.pulp_ilp_solver import ILPSolver


class DirectAlgo:
    def __init__(self, connection_string):
        alchemyEngine = create_engine(connection_string, pool_recycle=3600)
        connection = alchemyEngine.connect()
        ilp_solver = ILPSolver()
        self.connection = connection
        self.ilp_solver = ilp_solver

    def direct_wrapper(self, table_name, objective, objective_attribute, constraints, count_constraint, repeat, sr_constraints=[]):
        df = pd.read_sql("select * from tpch", self.connection)
        try:
            if sys.argv[2] == 'local':
                df = df.head(int(round(len(df) * 0.1)))
        except Exception as e:
            print('Running on 100% data')
        df.reset_index(inplace=True)
        print('Loaded the Table of Size: {}'.format(len(df)))
        return self.implement(table_name, objective, objective_attribute, constraints, count_constraint, df, repeat, sr_constraints)

    def implement(self, table_name, objective, objective_attribute, constraints, count_constraint, df, repeat, sr_constraints=[]):
        # Direct Algorithm
        start_time = time.time()

        print('Called The ILP Solver')
        status, package_rows = self.ilp_solver.solve_ilp_using_pulp(df, table_name, objective, objective_attribute, constraints, count_constraint, repeat,
                                                                    sr_constraints)
        print('ILP Solver Completed')
        print('Status: {}'.format(pulp.LpStatus[status]))
        if pulp.LpStatus[status] == 'Not Solved':
            sys.exit('Is the default setting before a problem has been solved')
        elif pulp.LpStatus[status] == 'Infeasible':
            sys.exit('The problem has no feasible solution')
        elif pulp.LpStatus[status] == 'Unbounded':
            sys.exit('The cost function is unbounded')
        elif pulp.LpStatus[status] == 'Undefined':
            sys.exit('Feasible solution hasn\'t been found (but may exist)')
        else:
            print('Found the optimal Solution\nPackage rows: {}'.format(package_rows))
        print('Execution time: {} s'.format(round(time.time() - start_time, 2)))
        return package_rows
