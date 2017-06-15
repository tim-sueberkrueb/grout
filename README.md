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

Create a `baka.yml` file.
```yaml
name: test-project
summary: Test project
description: A test project
environment:
  scripts:  # Use Python scripts to setup the build environment
    setup: |
      baka = require('baka', '0.1.0')
      print("setup")
      # Execute commands inside the build container
      baka.run("touch", "/home/baka/environment_setup")
jobs:
  - name: my-job
    extends: base  # You can use pre-defined jobs (e.g. snapcraft)
    source: .
    scripts:
      setup: |  # Run optional scripts for all build steps
        print("setup")
      perform: |
        baka = require('baka', '0.1.0')
        print("perform")
        baka.run("touch", "/home/baka/job_perform")
      finish: |
        baka = require('baka', '0.1.0')
        print("finish")
        baka.run("touch", "/home/baka/job_finish")
```
Use the baka tool to run all jobs
```sh
cd my-project/
baka   # See baka --help
```

### License
Licensed under the terms of the MIT license.
