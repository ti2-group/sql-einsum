# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Generate SQL-code
This folder a stand alone file, that shows how to generate sql-code with our compiler.

## Requirements
See [requirements](../README.md#Requirements) of the whole repository.

## Online Interface
We have an online interface for creating SQL queries from einstein notation. You can check it out at 
https://sql-einsum.ti2.uni-jena.de/.

## Usage 
You can start the experiments with 
````commandline
>>> python generate_sql_code.py

WITH A(i, j, val) AS (
  VALUES (CAST(0 AS INTEGER), CAST(0 AS INTEGER), CAST(0.7056014072212418 AS DOUBLE PRECISION)), (0, 1, 0.45971589315238937), 
         (1, 0, 0.35489758282488826), (1, 1, 0.29359389730739716)
), B(i, j, val) AS (
  VALUES (CAST(0 AS INTEGER), CAST(0 AS INTEGER), CAST(0.22951224078373988 AS DOUBLE PRECISION)), (0, 1, 0.5675223248600516), 
         (0, 2, 0.40707012918777563), (0, 3, 0.9604683213986135), (0, 4, 0.4737084865351948), (1, 0, 0.9452823353846342), 
         (1, 1, 0.29468652270266804), (1, 2, 0.7796228987151677), (1, 3, 0.9852058160883493), (1, 4, 0.1183786073900277)
), C(i, val) AS (
  VALUES (CAST(0 AS INTEGER), CAST(0.18847560525837315 AS DOUBLE PRECISION)), (1, 0.5453807869796465), 
         (2, 0.33211095396533385), (3, 0.6498585676438938), (4, 0.8004577043178819)
),  K1 AS (
  SELECT B.i AS i, SUM(C.val * B.val) AS val FROM C, B WHERE C.i=B.j GROUP BY B.i
) SELECT A.i AS i, SUM(K1.val * A.val) AS val FROM K1, A WHERE K1.i=A.j GROUP BY A.i ORDER BY i
````