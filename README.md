# BlobTrigger - Python

The `BlobTrigger` makes it incredibly easy to react to new Blobs inside of Azure Blob Storage. This sample demonstrates a simple use case of processing data from a given Blob using Python.

## How it works

For a `BlobTrigger` to work, you provide a path which dictates where the blobs are located inside your container, and can also help restrict the types of blobs you wish to return. For instance, you can set the path to `samples/{name}.png` to restrict the trigger to only the samples path and only blobs with ".png" at the end of their name.

## Create a Trigger from the Command Line
1. Initialize the Project
   ```bash
    func init blob_trigger --python
    ```
2. Create the Blob Trigger Function:
   ```bash
    cd blob_trigger
    func new --name StatesBlobTrigger --template "Azure Blob Storage trigger" --language Python
    ```
3. Edit local.settings.json and function.json as needed.
4. Start your function with func start.

### Finding a Blob Connection String in Azure
Option 1 - Portal: In the storage account's settings menu, scroll down to the Security + networking section and click on Access keys. You will see two keys: key1 and key2. Each key has a corresponding connection string.

Option 2 - Azure CLI: You can also use the Azure CLI to get the connection string. Run the following command in the Azure CLI:
```bash
az storage account show-connection-string --name <YourStorageAccountName> --resource-group <YourResourceGroupName>
```


### Examining the functions.json file
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "blob",
      "type": "blobTrigger",
      "direction": "in",
      "path": "states/PA/{name}",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```
- **bindings:**
This is an array that defines all the bindings for the function. In this case, there's only one binding that sets up a trigger for Azure Blob Storage.

- **name: "blob"`**
This defines the name of the parameter that your function will use to access the blob data. In your Python code, you refer to this as the blob parameter (e.g., def main(blob: func.InputStream)).

- **type: "blobTrigger"`**
Specifies that this function is triggered by a change in Azure Blob Storage. This means the function will run every time a new blob is added, modified, or deleted in the specified path.

- **direction: "in"`**
Indicates that this is an input binding, meaning that data will be passed into the function.

- **path: "states/PA/{name}"`**
This defines the path within the Azure Blob Storage container that you want to monitor.
In this case, the container name is states, and it monitors the PA folder within that container.
The {name} is a wildcard that captures the name of any blob within the PA folder. This allows your function to respond to changes for any blob added or modified in that location.

- **connection: "AzureWebJobsStorage"`**
This refers to the connection string used to access the Azure Blob Storage account.
AzureWebJobsStorage is a placeholder name that the Azure Function runtime expects to be defined in your configuration settings.


## Examining host.json file
The host.json file contains global configuration options that apply to all functions within the Azure Function App. This file is used to configure runtime settings such as logging, retry policies, and more.

```json
{
  "version": "2.0",
  "logging": {
    "logLevel": {
      "Function": "Information"
    }
  },
  "extensions": {
    "queues": {
      "batchSize": 16,
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30"
    }
  }
}
```

- **version:** Specifies the schema version of the host.json file. Use "version": "2.0" or "version": "3.0" for Azure Functions V2 and V3.

- **logging:** Configures logging settings.

- **logLevel:** Defines the log level for the function app. Common levels are Information, Warning, Error, and None.

- **extensions:** Contains configuration settings for different bindings/extensions used in your function app. For example:

- **queues:** If you’re using queue triggers, you can configure properties like batchSize (number of queue messages processed simultaneously) or maxDequeueCount (maximum retries for a message).

## Exaiming the local.settings.json file
The local.settings.json file is used only for local development. It stores environment variables and configuration settings needed for running your Azure Function locally, such as connection strings, API keys, or runtime settings.

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "MY_CUSTOM_SETTING": "customValue"
  },
  "ConnectionStrings": {
    "MyDatabase": "Server=localhost;Database=mydb;User Id=myuser;Password=mypassword;"
  }
}
```

- **IsEncrypted:** Indicates whether the file's content is encrypted. It's usually false for local development.

- **Values:** Contains key-value pairs of settings and environment variables:

- **AzureWebJobsStorage:** Defines the connection string for Azure Storage, used by triggers/bindings. UseDevelopmentStorage=true points to a local storage emulator (e.g., Azurite).

- **FUNCTIONS_WORKER_RUNTIME:** Specifies the language runtime for the function app (e.g., python, node, dotnet).

- **ConnectionStrings:** Optional section where you can define database connection strings. This allows you to manage your connection settings separately from other values.


### You won't have a functions.json file
There won't be a *functions.json* file when working with Azure Functions V2 and higher. In Azure Functions V2 and later, the function.json file is automatically managed by the Azure Functions runtime and tooling.

- In earlier versions of Azure Functions (V1), you had to manually create and manage the function.json file to define your function's bindings and triggers.
- Starting from Azure Functions V2 and V3, the function.json file is auto-generated based on attributes or decorators in your code or from the template when you create a new function using the Azure Functions Core Tools (func command).


## AzureWebJobsStorage and STORAGE_CONNECTION
The **AzureWebJobsStorage** and **STORAGE_CONNECTION** (or whatever you call your connection) serve different purposes in an Azure Function app, but it's common for them to be the same when your function app relies on the same storage account for both its internal operations and for accessing the external Blob Storage trigger. Let’s break down the roles of each:

1. **AzureWebJobsStorage**
**Purpose:**
AzureWebJobsStorage is a required configuration setting that the Azure Functions runtime uses for its own internal operations. This includes:
- Storing function execution metadata (e.g., function checkpoints, status, and logs for durable functions).
- Managing triggers and bindings (e.g., Blob Triggers, Queue Triggers) to track function executions.
- Enabling scalability for the function app by keeping track of the function's execution state.

**Usage:**
- Every Azure Function app requires an AzureWebJobsStorage setting to function correctly, even if your function doesn't explicitly interact with Blob Storage or other storage services.
- For local development, you might use UseDevelopmentStorage=true to connect to Azurite, the local storage emulator.
- In a production environment, this connection string should point to a real Azure Storage account.

2. **STORAGE_CONNECTION**
**Purpose:**
- STORAGE_CONNECTION is a custom application setting you've defined in your local.settings.json file. - It represents the connection string specifically for the Blob Storage account your Blob Trigger function needs to monitor.
- This is the connection that your function will use to access blobs in the specified container and path (e.g., states/{state}/{name}) for reading or writing data.


## Using a specific python version with Function Apps
```bash
env languageWorkers:python:defaultExecutablePath=../venv/bin/python func start
```