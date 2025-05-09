# GenAI-System-

This systen is created to ingest a picture of a document with information on it,

then classify the document based on its contents

the system supports a redis cache to change experience A/B testing.

The system also takes the information from the document and vectorizes it and puts it into pgvector.


create service that monitors the db and updates the cache with new vectors for each query.