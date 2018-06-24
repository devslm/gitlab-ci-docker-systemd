# Description and usage will be added soon

# gitlab-ci-docker-systemd
Script allows to execute docker with systemd in Gitlab CI Runner

###### Article about problem here: [habr](https://habr.com/post/413375/)

##### Starting
```
git clone https://github.com/seregaSLM/gitlab-ci-docker-systemd.git
cd <path-with-code>
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py \
  --image dramaturg/docker-debian-systemd # your docker image
  [--network host] # network type, not required
  [--volumes] "/sys/fs/cgroup:/sys/fs/cgroup:ro" "<other volumes>" # /sys/fs/cgroup volume rewuired for systemd and you can add your required volumes separated by whitespace
  [--cmd] "/lib/systemd/systemd" # command if we want to rewrite exists in docker image
  [--data-archive] /opt/data.tar # full archive path to *.tar or *.tar.gz
  [--data-unarchive-path] /opt/data/logs # unarchive path in the destionation container, it will be created if not exists
  [--privileged] # for systemd running is required, other low priority running varinats I don't use
  --exec-commands "touch /opt/example.log" "{bash} ls -la /opt" "mkdir -p /opt/tmp" # the list of bash commands separated by whitespace
```

Special keyword {bash} at start of the command is short version version of the real command /bin/bash -c "command" when your command must bu run under bash.
