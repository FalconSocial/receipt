# Receipt

A GitHub/GitLab post-receive hook - receiver, written as a [Flask](http://flask.pocoo.org/) application.

Whenever you push code to a GitHub/GitLab repository, with a post-receive hook configured to point at Receipt, the scripts found for the repository and branch will be executed.

If you for instance have configured the `scripts directory` parameter to `scripts` and do a push to the _master_ branch in the _backend_ repository, the scripts found within the directories at `scripts/backend` and `scripts/backend/master` will be executed.

Receipt will execute the scripts the same way if you entered `./script.sh` within a shell, except the default interpreter won't be whichever shell you are using. This generally means you need to include an interpreter on the first line of the script, using the [Shebang](https://en.wikipedia.org/wiki/Shebang_%28Unix%29) syntax or use a binary file.

The program will be called with the repository name as the first argument and branch name as the second. The full JSON payload will be sent to standard input of the program. An example of the payload can be see in the [GitHub](https://developer.github.com/v3/activity/events/types/#pushevent) and [GitLab](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/doc/web_hooks/web_hooks.md#push-events) documentations.

The scripts will be executed as the same user Receipt is running as, if you want to run a script with other permissions, then either use the [setuid bit](https://en.wikipedia.org/wiki/Setuid), or make a shell script which calls `sudo`.


## License

Receipt is available under the MIT license.
