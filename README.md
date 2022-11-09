<p align="center">
    <img src="https://github.com/andrewsapw/autobot/raw/master/docs/static/autobot_head.png" alt="Pyrogram" width="128">
    <br>
    <b>AUTOBOT</b>
    <br>
</p>

> :warning: Project is in active development and not intended for any serious application

Framework for making bot from config files (we all love *YAML*, does't we?)

1. [Features](#features)
2. [Usage](#usage)

# Features
- **Automatic back button configuration** - not need to plainly think about branching
- **Beautiful inline buttons experience** - previous message gets updated on button pressed (much cleaner message history)
- **RegEx message filters**

# Installation

```bash
$ pip install autobot-tg # or: pipx install autobot-tg
$ autobot-tg --help
```
# Usage

Before starting the bot, you have to specify bot token with env variable `BOT_TOKEN`

```sh
autobot examples/configs/simple.yaml
```
# Config
## Config examples
- [Simple one](/examples/configs/simple.yaml)
- [Inline buttons](/examples/configs/inline_buttons.yaml)
## Config schema
Core elements of schema is:
- `states` - describes possible bot states (nodes in network graph)
- `transitions` - describes transitions between states (edges)

### States schema
States can be represented as array of named elements:
- `<state name>`
  - `text` (required) - text message that the bot will send when entering the state
  - `command` (optional) - specifies the command that will trigger state (for example `/start`)
  - `add_back_button` (optional) - whether state should have back button (_yes_ or _no_)
  - `inline_buttons` (optional) - describes inline buttons of this state
    - `row` (required) - buttons in one row (array)
      - `text` -  inline button text
      - `callback_data` - data that will be sent on button pressed
### Transitions
Transitions is an array of elements with these fields:
- `from` (required) - source state. Transition will be triggered only if bot is in this state. Must be present in states schema
- `to` (required) - target state.  Must be present in states schema
- `conditions` (required) - under what conditions the transition will be triggered. Possible conditions:
  - `message` (array of regex) - transition will be triggered on message sent. Applies regex filter to user's message. If filter passes - transition is triggered (for example `.+` will always trigger transition)
  - `data` (array of strings) - transition will be triggered if specified callback data will be sent (when user presses the inline button)
  - `else` (string - name of state) - trigger transition if no other conditions are satisfied. Must be valid state name
  - `always` (no parameters) - always triggers transition. When bot enters `from` state, it will instantly enter `to` state
