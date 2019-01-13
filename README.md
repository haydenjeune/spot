# Spot
Spot is a command line tool that helps to manage AWS spot instances, particularly for the purposes of training neural networks on GPU based instances. This package has only been tested on Mac launching Ubuntu based instances.

## How to use
1. Clone this repo
2. Run `python setup.py install`, make sure you have `setuptools` installed
3. Setup the AWS CLI, and configure a profile called `spot` with command line access to the console
4. Add the AmazonEC2FullAccess policy to your user in AWS (I'll add a policy template with exactly what you need at some point)
5. Create and add a policy with IAM:PassRole permissions to the user
6. Start hacking template.yaml with the parameters you need

```spot list```
Prints a nicely formatted table of all of your instances

```spot launch <path>```
Launches an instance based on the yaml config file at `path`

```spot terminate <instance_id>```
Terminates the instance with `instance_id`

More coming soon
