# Command table

The rule of commands and motions

## Command

The commands are sent from UR to PC.

| Code | Command       | Description            |
| ---- | ------------- | ---------------------- |
| 400  | Reset         | Rest motionOption to 0 |
| 1101 | Done motion-1 | Motion-1 is done       |
| 1201 | Done motion-1 | Motion-1 is done       |

## MotionOption

The options are sent from PC to UR.

| Code | Command  | Description |
| ---- | -------- | ----------- |
| 0    | Idle     |             |
| 1100 | Motion-1 |             |
| 1200 | Motion-2 |             |
