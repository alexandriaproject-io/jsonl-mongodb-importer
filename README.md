# jsonl-mongodb-importer
Imports jsonl datasets to mongodb with remapping

Each dataset is different so this project will contain a collection of scripts each for its own type of dataset. \
The datasets will be coverted to a strict data structure as follows:

### Dataset Source Card
```json
{
  "_id": "Mongo ObjectId",
  "datasetName": "String - Name of the dataset",
  "datasetUrl": "String - Dataset URL for reference",
  "datasetType": "String - Training data type: One of['llm-chat','llm-instruct','llm-completion']",
  "datasetTargetLength": "String - Target context size: One of ['4k','8k','16k','32k','64k','128k']",
  "datasetOrigin": "String - Data origin: One of ['human','generated','mixed']"
}
```
NOTE: datacard should be created manually in the DB ( the ID is required for the data items remapping )
### Dataset data row
```json
{
   "_id": "Mongo ObjectId",
   "datasetId": "Mongo ObjectId@index - Id of the dataset card",
   "systemMessage": "String@empty - System message for the LLM",
   "contextMessage": "Context@empty - System message for the LLM",
   "textMessage": "String@empty - Raw text message if type is 'llm-completion'",
   "userAssistantMessages": [
     {
       "provider": "String - One of ['user','assistant']",
       "message": "String"
     },
     {
       "provider": "String - One of ['user','assistant']",
       "message": "String"
     },
     ...
   ]
}
```

## Virtual environment activation

windows:
```
.\env\Scripts\activate
```

Linux
```
source env/bin/activate

```