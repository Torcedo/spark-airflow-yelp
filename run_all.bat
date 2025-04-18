@echo off
set SPARK_CMD=docker-compose run --rm spark spark-submit ^
 --conf spark.jars.ivy=/tmp/.ivy2 ^
 --conf spark.hadoop.security.authentication=NOSASL ^
 --conf spark.hadoop.security.authorization=false ^
 --conf spark.hadoop.fs.file.impl=org.apache.hadoop.fs.LocalFileSystem

%SPARK_CMD% spark/review_transform.py
%SPARK_CMD% spark/business_transform.py
%SPARK_CMD% spark/user_transform.py
%SPARK_CMD% spark/tip_transform.py
%SPARK_CMD% spark/checkin_transform.py

echo.
echo Toutes les transformations sont terminées.
pause
