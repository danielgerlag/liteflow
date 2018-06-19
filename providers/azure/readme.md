# Azure synchronization providers for LiteFlow

Provides support to use Azure storage as a shared work queue and distributed lock service for LiteFlow 

## Installing

Install the "liteflow.providers.azure" package

```
> pip install liteflow.providers.azure
```

## Usage

Pass an instances of AzureQueueProvider and AzureLockProvider to `configure_workflow_host` when configuring your workflow node host.

```python
from azure.storage.common import CloudStorageAccount
from liteflow.core import *
from liteflow.providers.azure import AzureQueueProvider, AzureLockProvider


azure_storage_account = CloudStorageAccount(account_name='my account', account_key='my key')
azure_queue_service = AzureQueueProvider(azure_storage_account)
azure_lock_service = AzureLockProvider(azure_storage_account)

host = configure_workflow_host(queue_service=azure_queue_service,
                               lock_service=azure_lock_service)
host.start()

```
