# MongoDB Persistence provider for LiteFlow

Provides support to persist workflows running on LiteFlow to a MongoDB database.

## Installing

Install the "liteflow.providers.mongo" package

```
> pip install liteflow.providers.mongo
```

## Usage

Pass an instance of MongoPersistenceProvider to `configure_workflow_host` when configuring your workflow node host.

```python
from liteflow.core import *
from liteflow.providers.mongo import MongoPersistenceProvider

mongodb = MongoPersistenceProvider('mongodb://localhost:27017/', 'liteflow')

host = configure_workflow_host(persistence_service=mongodb)
host.start()

```
