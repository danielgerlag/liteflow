# LiteFlow

LiteFlow is a Python library for running workflows.  Think: long running processes with multiple tasks that need to track state.  It supports pluggable persistence and concurrency providers to allow for multi-node clusters.

* [Installation](#installation)
* [Basic Concepts](#basic-concepts)
	* [Steps](#steps)
	* [Passing data between steps](#passing-data-between-steps)
	* [Events](#events)
* [Flow control](#flow-control)
	* [Parallel ForEach](#parallel-foreach)
	* [While condition](#while-condition)
	* [If condition](#if-condition)
* [Host](#host)
* [Persistence](#persistence)
* [Multi-node clusters](#multi-node-clusters)
* [Samples](#samples)

## Installation

Install the "liteflow.core" package

```
> pip install liteflow.core
```


## Basic Concepts

### Steps

A workflow consists of a series of connected steps.  Each step produces an outcome value and subsequent steps are triggered by subscribing to a particular outcome of a preceeding step.
Steps are usually defined by inheriting from the StepBody abstract class and implementing the *run* method.

First we define some steps

```python
from liteflow.core import *


class Hello(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Hello world")
        
        
class Goodbye(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Goodbye")
        return ExecutionResult.next()

```

Then we define the workflow structure by composing a chain of steps.

```python
class MyWorkflow(Workflow):

    def id(self):
        return "MyWorkflow"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello)\
            .then(Goodbye)

```
The `id` and `version` properties are used by the workflow host to identify a workflow definition.

Each running workflow is persisted to the chosen persistence provider between each step, where it can be picked up at a later point in time to continue execution.  The outcome result of your step can instruct the workflow host to defer further execution of the workflow until a future point in time or in response to an external event.

The first time a particular step within the workflow is called, the persistenceData property on the context object is *None*.  The ExecutionResult produced by the *run* method can either cause the workflow to proceed to the next step by providing an outcome value, instruct the workflow to sleep for a defined period or simply not move the workflow forward.  If no outcome value is produced, then the step becomes re-entrant by setting persistenceData, so the workflow host will call this step again in the future buy will popluate the persistenceData with it's previous value.


### Passing data between steps

Each step is intended to be a black-box, therefore they support inputs and outputs.  Each workflow instance carries a data property for holding 'workflow wide' data that the steps can use to communicate.

The following sample shows how to define inputs and outputs on a step, it then shows how to map the inputs and outputs to properties on the workflow data property.

```python
#Our workflow step with inputs and outputs
class AddNumbers(StepBody):
    def __init__(self):
        self.input1 = 0
        self.input2 = 0
        self.output = 0

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        self.output = self.input1 + self.input2
        return ExecutionResult.next()


#A class to hold workflow wide data
class MyData:
    def __init__(self):
        self.value1 = 0
        self.value2 = 0
        self.value3 = 0


#Our workflow definition with mapped inputs & outputs
class MyWorkflow(Workflow):
    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello)\
            .then(AddNumbers) \
                .input('input1', lambda data, context: data.value1) \
                .input('input2', lambda data, context: data.value2) \
                .output('value3', lambda step: step.output) \
            .then(Goodbye)

```

### Events

A workflow can also wait for an external event before proceeding.  In the following example, the workflow will wait for an event called *"event1"* with a key of *"key1"*.  Once an external source has fired this event, the workflow will wake up and continue processing.

```python
class MyWorkflow(Workflow):
    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello) \
            .wait_for('event1', lambda data, context: 'key1') \
            .then(Goodbye)


#External events are published via the host
#All workflows that have subscribed to event1, key1, will be passed "hello"
host.publish_event('event1', 'key1', 'hello')

#Data from the published event can be captured and mapped to the workflow data object with an output on the WaitFor step
class MyWorkflow(Workflow):
    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello) \
            .wait_for('event1', lambda data, context: 'key1') \
                .output('captured_value', lambda step: step.event_data) \
            .then(Goodbye)

```

### Flow Control

#### Parallel ForEach

```python
class DoStuff(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print(f"doing stuff...{context.execution_pointer.context_item}")
        return ExecutionResult.next()


class MyWorkflow(Workflow):

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello)\
            .for_each(lambda data, context: ["abc", "def", "xyz"])\
                .do(lambda x:\
                    x.start_with(DoStuff))\
            .then(Goodbye)

```

#### While condition

```python
class MyWorkflow(Workflow):
    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello)\
            .while_(lambda data, context: data.value1 < 3)\
                .do(lambda do:\
                    do.start_with(DoStuff)\
                        .input('my_value', lambda data, context: data.value1)\
                        .output('value1', lambda step: step.your_value))\
            .then(Goodbye)

```

#### If condition

```python
class MyWorkflow(Workflow):

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello)\
            .if_(lambda data, context: data.value1 > 3)\
                .do(lambda x:\
                    x.start_with(DoStuff))\
            .then(Goodbye)

```


### Host

The workflow host is the service responsible for executing workflows.  It does this by polling the persistence provider for workflow instances that are ready to run, executes them and then passes them back to the persistence provider to by stored for the next time they are run.  It is also responsible for publishing events to any workflows that may be waiting on one.

#### Usage

When your application starts, create a WorkflowHost service using `configure_workflow_host`,  call *register_workflow*, so that the workflow host knows about all your workflows, and then call *start* to fire up the event loop that executes workflows.  Use the *start_workflow* method to initiate a new instance of a particular workflow.


```python
from liteflow.core import *


host = configure_workflow_host()
host.register_workflow(MyWorkflow())
host.start()

wid = host.start_workflow("MyWorkflow", 1, None)

```

## Persistence

Since workflows are typically long running processes, they will need to be persisted to storage between steps.
There are several persistence providers available as separate packages.

* Memory Persistence Provider *(Default provider, for demo and testing purposes)*
* [MongoDB](https://github.com/danielgerlag/liteflow/tree/master/providers/mongodb)
* *(more to come soon...)*

## Multi-node clusters

By default, the WorkflowHost service will run as a single node using the built-in queue and locking providers for a single node configuration.  Should you wish to run a multi-node cluster, you will need to configure an external queueing mechanism and a distributed lock manager to co-ordinate the cluster.  These are the providers that are currently available.

#### Queue Providers

* SingleNodeQueueProvider *(Default built-in provider)*
* [Azure](https://github.com/danielgerlag/liteflow/tree/master/providers/azure)
* RabbitMQ *(coming soon...)*


#### Distributed lock managers

* LocalLockProvider *(Default built-in provider)*
* [Azure](https://github.com/danielgerlag/liteflow/tree/master/providers/azure)
* Redis Redlock *(coming soon...)*


## Samples

* [Hello World](https://github.com/danielgerlag/liteflow/blob/master/samples/01-hello-world.py)

* [Passing Data](https://github.com/danielgerlag/liteflow/blob/master/samples/02-passing-data.py)

* [Events](https://github.com/danielgerlag/liteflow/blob/master/samples/03-waiting-for-events.py)

* [Parallel ForEach](https://github.com/danielgerlag/liteflow/blob/master/samples/04-foreach.py)

* [If condition](https://github.com/danielgerlag/liteflow/blob/master/samples/05-if.py)

* [While loop](https://github.com/danielgerlag/liteflow/blob/master/samples/06-while.py)


## Authors

* **Daniel Gerlag** - *Initial work*


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

