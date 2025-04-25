#!/bin/bash

gcloud functions deploy trigger_yelp_dag `
>>   --gen2 `
>>   --runtime=python310 `
>>   --region=europe-west1 `
>>   --entry-point=trigger_dag `
>>   --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" `
>>   --trigger-event-filters="bucket=datasparkyelp-yelp-raw" `
>>   --source=. `
>>   --set-env-vars=COMPOSER_ENV_NAME=ton-env-composer