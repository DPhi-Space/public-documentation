# Operations

## Overview

Operations are the blueprints for executions. At its core, an operation is defined by a YAML file, in which a set of tasks is defined with their execution order, input parameters, and outputs.

Operations organize `tasks` and their respective `inputs`. They define what tasks run, how they run, and when they run.

## Operation Example
As an example, the following operation `test-health`:

```YAML
id: test-health
namespace: gamma
description: Example execution with multiple CG2 tasks.
tasks:
- id: pod_run_job
  pod_name: test
  type: dphi.space.cg2.pod.run
  description: Run a pod with parameters
  image:
    name: alpine
    tag: latest
  command:
  - /bin/sh
  args:
  - -c
  - echo 'Debi tirar mas fotos' > /data/hello-from-space.txt
  node: Fpga
  max_duration_seconds: 1
  scheduled_time: null
- id: downlink_results
  type: dphi.space.cg2.downlink
  description: Downlink files to ground
  source:
  - hello-from-space.txt
  destination: /first_test
  volume: payload
```

Defines an operation in which two tasks are performed sequentially. First, the `pod_run_job` task of type `dphi.space.cg2.pod.run` schedules a DPhi Pod to run with the given parameters. This task is expected to create the `hello-from-space.txt` file at the root of the `payload` volume onboard. Then, the `downlink_results` task of type [`dphi.space.cg2.downlink`](/docs/3-dashboard/4-tasks/cg2/downlink.md) will downlink this file and save it to the folder `/first_test` under the namespace of the operation, *i.e.* `gamma`.


## Tasks

Tasks are the atomic units of operations. They are associated with single actions, such as uplinking, executing a DPhi Pod, or deleting a file. They define what should be executed with all the necessary parameters.

Tasks can also generate task-specific outputs. For example, the [`dphi.space.cg2.downlink`](/docs/3-dashboard/4-tasks/cg2/downlink.md) task type exposes downlinked file URIs and metadata.



The list of available tasks can be found in the [Tasks](/docs/3-dashboard/4-tasks/0-intro.md) section.
