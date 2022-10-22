WITH T0(i, re, im) AS (
  VALUES (CAST(0 AS INTEGER), CAST(1.0 AS DOUBLE PRECISION), CAST(0.0 AS DOUBLE PRECISION))
), T1(i,j, re, im) AS (
  VALUES (CAST(0 AS INTEGER), CAST(0 AS INTEGER), CAST(0.5 AS DOUBLE PRECISION), CAST(0.5 AS DOUBLE PRECISION)), (0, 1, 0.5, -0.5),
  (1, 0, 0.5, -0.5), (1, 1, 0.5, 0.5)
), T2(i,j, re, im) AS (
  VALUES (CAST(0 AS INTEGER), CAST(0 AS INTEGER), CAST(0.7071067811865476 AS DOUBLE PRECISION), CAST(-0.0 AS DOUBLE PRECISION)), (0, 1, -0.4999999999999999, -0.4999999999999999),
  (1, 0, 0.4999999999999999, -0.4999999999999999), (1, 1, 0.7071067811865476, -0.0)
), T3(i,j, re, im) AS (
  VALUES (CAST(0 AS INTEGER), CAST(0 AS INTEGER), CAST(0.5 AS DOUBLE PRECISION), CAST(0.5 AS DOUBLE PRECISION)), (0, 1, -0.5, -0.5),
  (1, 0, 0.5, 0.5), (1, 1, 0.5, 0.5)
), K1 AS (
  SELECT T3.i AS i, T1.j AS j, SUM(T3.re * T1.re - T3.im * T1.im) AS re, SUM(T3.re * T1.im + T3.im * T1.re) AS im FROM T3, T3 T1 WHERE T3.j=T1.i GROUP BY T3.i, T1.j
), K2 AS (
  SELECT T1.i AS i, SUM(T1.re * T0.re - T1.im * T0.im) AS re, SUM(T1.re * T0.im + T1.im * T0.re) AS im FROM T1, T0 WHERE T1.j=T0.i GROUP BY T1.i
), K3 AS (
  SELECT T1.i AS i, T2.j AS j, SUM(T1.re * T2.re - T1.im * T2.im) AS re, SUM(T1.re * T2.im + T1.im * T2.re) AS im FROM T1, T2 WHERE T1.j=T2.i GROUP BY T1.i, T2.j
), K4 AS (
  SELECT T2.i AS i, SUM(K2.re * T2.re - K2.im * T2.im) AS re, SUM(K2.re * T2.im + K2.im * T2.re) AS im FROM K2, T2 WHERE K2.i=T2.j GROUP BY T2.i
), K5 AS (
  SELECT T1.i AS i, T3.j AS j, SUM(T1.re * T3.re - T1.im * T3.im) AS re, SUM(T1.re * T3.im + T1.im * T3.re) AS im FROM T1, T3 WHERE T1.j=T3.i GROUP BY T1.i, T3.j
), K6 AS (
  SELECT T1.i AS i, SUM(T1.re * T0.re - T1.im * T0.im) AS re, SUM(T1.re * T0.im + T1.im * T0.re) AS im FROM T1, T0 WHERE T1.j=T0.i GROUP BY T1.i
), K7 AS (
  SELECT T2.i AS i, T3.j AS j, SUM(T2.re * T3.re - T2.im * T3.im) AS re, SUM(T2.re * T3.im + T2.im * T3.re) AS im FROM T2, T3 WHERE T2.j=T3.i GROUP BY T2.i, T3.j
), K8 AS (
  SELECT K7.i AS i, T3.j AS j, SUM(K7.re * T3.re - K7.im * T3.im) AS re, SUM(K7.re * T3.im + K7.im * T3.re) AS im FROM K7, T3 WHERE K7.j=T3.i GROUP BY K7.i, T3.j
), K9 AS (
  SELECT T3.i AS i, T2.j AS j, SUM(T3.re * T2.re - T3.im * T2.im) AS re, SUM(T3.re * T2.im + T3.im * T2.re) AS im FROM T3, T2 WHERE T3.j=T2.i GROUP BY T3.i, T2.j
), K10 AS (
  SELECT K8.j AS i, T3.i AS j, SUM(K8.re * T3.re - K8.im * T3.im) AS re, SUM(K8.re * T3.im + K8.im * T3.re) AS im FROM K8, T3 WHERE K8.i=T3.j GROUP BY K8.j, T3.i
), K11 AS (
  SELECT T3.i AS i, T1.j AS j, SUM(T3.re * T1.re - T3.im * T1.im) AS re, SUM(T3.re * T1.im + T3.im * T1.re) AS im FROM T3, T1 WHERE T3.j=T1.i GROUP BY T3.i, T1.j
), K12 AS (
  SELECT T2.i AS i, T1.j AS j, SUM(T2.re * T1.re - T2.im * T1.im) AS re, SUM(T2.re * T1.im + T2.im * T1.re) AS im FROM T2, T2 T1 WHERE T2.j=T1.i GROUP BY T2.i, T1.j
), K13 AS (
  SELECT K12.j AS i, T1.i AS j, SUM(K12.re * T1.re - K12.im * T1.im) AS re, SUM(K12.re * T1.im + K12.im * T1.re) AS im FROM K12, T1 WHERE K12.i=T1.j GROUP BY K12.j, T1.i
), K14 AS (
  SELECT K1.i AS i, T1.j AS j, SUM(K1.re * T1.re - K1.im * T1.im) AS re, SUM(K1.re * T1.im + K1.im * T1.re) AS im FROM K1, T1 WHERE K1.j=T1.i GROUP BY K1.i, T1.j
), K15 AS (
  SELECT K13.j AS i, SUM(K13.re * K6.re - K13.im * K6.im) AS re, SUM(K13.re * K6.im + K13.im * K6.re) AS im FROM K13, K6 WHERE K13.i=K6.i GROUP BY K13.j
), K16 AS (
  SELECT K11.i AS i, T2.j AS j, SUM(K11.re * T2.re - K11.im * T2.im) AS re, SUM(K11.re * T2.im + K11.im * T2.re) AS im FROM K11, T2 WHERE K11.j=T2.i GROUP BY K11.i, T2.j
), K17 AS (
  SELECT T1.i AS i, T3.j AS j, SUM(T1.re * T3.re - T1.im * T3.im) AS re, SUM(T1.re * T3.im + T1.im * T3.re) AS im FROM T1, T3 WHERE T1.j=T3.i GROUP BY T1.i, T3.j
), K18 AS (
  SELECT T2.i AS i, T1.j AS j, SUM(T2.re * T1.re - T2.im * T1.im) AS re, SUM(T2.re * T1.im + T2.im * T1.re) AS im FROM T2, T2 T1 WHERE T2.j=T1.i GROUP BY T2.i, T1.j
), K19 AS (
  SELECT K17.j AS i, T1.i AS j, SUM(K17.re * T1.re - K17.im * T1.im) AS re, SUM(K17.re * T1.im + K17.im * T1.re) AS im FROM K17, T1 WHERE K17.i=T1.j GROUP BY K17.j, T1.i
), K20 AS (
  SELECT K14.i AS i, SUM(K14.re * K4.re - K14.im * K4.im) AS re, SUM(K14.re * K4.im + K14.im * K4.re) AS im FROM K14, K4 WHERE K14.j=K4.i GROUP BY K14.i
), K21 AS (
  SELECT K19.i AS i, T3.i AS j, SUM(K19.re * T3.re - K19.im * T3.im) AS re, SUM(K19.re * T3.im + K19.im * T3.re) AS im FROM K19, T3 WHERE K19.j=T3.j GROUP BY K19.i, T3.i
), K22 AS (
  SELECT T2.i AS i, SUM(K20.re * T2.re - K20.im * T2.im) AS re, SUM(K20.re * T2.im + K20.im * T2.re) AS im FROM K20, T2 WHERE K20.i=T2.j GROUP BY T2.i
), K23 AS (
  SELECT K21.j AS i, SUM(K22.re * K21.re - K22.im * K21.im) AS re, SUM(K22.re * K21.im + K22.im * K21.re) AS im FROM K22, K21 WHERE K22.i=K21.i GROUP BY K21.j
), K24 AS (
  SELECT K3.j AS i, T1.i AS j, SUM(K3.re * T1.re - K3.im * T1.im) AS re, SUM(K3.re * T1.im + K3.im * T1.re) AS im FROM K3, T1 WHERE K3.i=T1.j GROUP BY K3.j, T1.i
), K25 AS (
  SELECT K5.i AS i, SUM(K15.re * K5.re - K15.im * K5.im) AS re, SUM(K15.re * K5.im + K15.im * K5.re) AS im FROM K15, K5 WHERE K15.i=K5.j GROUP BY K5.i
), K26 AS (
  SELECT K24.j AS i, K9.j AS j, SUM(K24.re * K9.re - K24.im * K9.im) AS re, SUM(K24.re * K9.im + K24.im * K9.re) AS im FROM K24, K9 WHERE K24.i=K9.i GROUP BY K24.j, K9.j
), K27 AS (
  SELECT K26.j AS i, T3.i AS j, SUM(K26.re * T3.re - K26.im * T3.im) AS re, SUM(K26.re * T3.im + K26.im * T3.re) AS im FROM K26, T3 WHERE K26.i=T3.j GROUP BY K26.j, T3.i
), K28 AS (
  SELECT K16.j AS i, T1.i AS j, SUM(K16.re * T1.re - K16.im * T1.im) AS re, SUM(K16.re * T1.im + K16.im * T1.re) AS im FROM K16, T1 WHERE K16.i=T1.j GROUP BY K16.j, T1.i
), K29 AS (
  SELECT K10.j AS i, SUM(K23.re * K10.re - K23.im * K10.im) AS re, SUM(K23.re * K10.im + K23.im * K10.re) AS im FROM K23, K10 WHERE K23.i=K10.i GROUP BY K10.j
), K30 AS (
  SELECT K18.j AS i, T1.i AS j, SUM(K18.re * T1.re - K18.im * T1.im) AS re, SUM(K18.re * T1.im + K18.im * T1.re) AS im FROM K18, T1 WHERE K18.i=T1.j GROUP BY K18.j, T1.i
), K31 AS (
  SELECT K30.j AS i, SUM(K30.re * K25.re - K30.im * K25.im) AS re, SUM(K30.re * K25.im + K30.im * K25.re) AS im FROM K30, K25 WHERE K30.i=K25.i GROUP BY K30.j
), K32 AS (
  SELECT K27.j AS i, T2.j AS j, SUM(K27.re * T2.re - K27.im * T2.im) AS re, SUM(K27.re * T2.im + K27.im * T2.re) AS im FROM K27, T2 WHERE K27.i=T2.i GROUP BY K27.j, T2.j
), K33 AS (
  SELECT K32.i AS i, SUM(K32.re * K31.re - K32.im * K31.im) AS re, SUM(K32.re * K31.im + K32.im * K31.re) AS im FROM K32, K31 WHERE K32.j=K31.i GROUP BY K32.i
), K34 AS (
  SELECT T2.i AS i, SUM(K33.re * T2.re - K33.im * T2.im) AS re, SUM(K33.re * T2.im + K33.im * T2.re) AS im FROM K33, T2 WHERE K33.i=T2.j GROUP BY T2.i
), K35 AS (
  SELECT K28.j AS i, SUM(K29.re * K28.re - K29.im * K28.im) AS re, SUM(K29.re * K28.im + K29.im * K28.re) AS im FROM K29, K28 WHERE K29.i=K28.i GROUP BY K28.j
), K36 AS (
  SELECT T2.i AS i, SUM(K34.re * T2.re - K34.im * T2.im) AS re, SUM(K34.re * T2.im + K34.im * T2.re) AS im FROM K34, T2 WHERE K34.i=T2.j GROUP BY T2.i
) SELECT K36.i AS i, K35.i AS j, SUM(K36.re * K35.re - K36.im * K35.im) AS re, SUM(K36.re * K35.im + K36.im * K35.re) AS im FROM K36, K35 GROUP BY K36.i, K35.i ORDER BY i, j