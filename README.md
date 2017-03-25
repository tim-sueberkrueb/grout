## Grout

Python tool and library for continuous, clean builds using LXC/LXD.
Grout was primarily designed to be used in combination with Snapcraft.

### Install
```sh
cd grout/
python3 setup.py install
```

### Usage

*Note:* Grout is work in progress. API and supported features are subject to change without notice.

Create a `project.yaml` file.
```
name: test-project
summary: Test project
description: A test project
environment:
  scripts:  # Use Python scripts to setup the build environment
    setup: |
      print("setup")
      # Execute commands inside the build container
      container.exec("touch", "/home/grout/environment_setup")
jobs:
  - name: my-job
    type: base  # You can use pre-defined jobs (e.g. snapcraft)
    source: .
    scripts:
      setup: |  # Run optional scripts for all build steps
        print("setup")
        container.exec("touch", "/home/grout/job_setup")
      perform: |
        print("perform")
        container.exec("touch", "/home/grout/job_perform")
      finish: |
        print("finish")
        container.exec("touch", "/home/grout/job_finish")
```
Use the grout tool to run all jobs
```sh
cd my-project/
grout   # See grout --help
```

### License
Licensed under the terms of the MIT license.
