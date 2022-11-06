# AUTOBOT

Framework for making bot from config files (we all love *YAML*, does't we?)


# Usage

```sh
python -m autobot examples/configs/simple.yaml
```

## Sample config

```yaml
title: "AUTOBOT"

states:
  hello:
    text: "Hello, I'm Simple Bot\nWhat is your name?"
    command: "start"
  age_input:
    text: "Nice to meet you!\nHow old are you?"
    add_back_button: yes
  end:
    text: "Good!"
    add_back_button: yes
  bad_age:
    text: "Can't understand your age. Please, try again"

transitions:
  hello-age_input:
    from: hello
    to: age_input
    conditions:
      message:
        - ".+"

  age_input-end:
    from: age_input
    to: end
    conditions:
      message:
        - "\\d+"
      else: "bad_age"

  bag_age-age:
    from: bad_age
    to: age_input
    conditions:
      always:
```
