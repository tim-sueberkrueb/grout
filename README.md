## Baka

Python tool and library for continuous, clean builds.
Baka was primarily designed to be used in combination with Snapcraft.

### Dependencies

* `Python >= 3.5`
    * with all modules listed as `install_requires` in `setup.py`
* One of the following backends:
    * [LXC](https://linuxcontainers.org/)
    * [Docker](https://www.docker.com/)

### Install
```sh
cd baka/
python3 setup.py install
```

### Usage

*Note:* Baka is work in progress. API and supported features are subject to change without notice.

Create a `project.yaml` file.
```yaml
name: test-project
summary: Test project
description: A test project
environment:
  scripts:  # Use Python scripts to setup the build environment
    setup: |
      print("setup")
      # Execute commands inside the build container
      container.exec("touch", "/home/baka/environment_setup")
jobs:
  - name: my-job
    type: base  # You can use pre-defined jobs (e.g. snapcraft)
    source: .
    scripts:
      setup: |  # Run optional scripts for all build steps
        print("setup")
        baka
      perform: |
        print("perform")
        container.exec("touch", "/home/baka/job_perform")
      finish: |
        print("finish")
        container.exec("touch", "/home/baka/job_finish")
```
Use the baka tool to run all jobs
```sh
cd my-project/
baka   # See baka --help
```

### License
Licensed under the terms of the MIT license.
