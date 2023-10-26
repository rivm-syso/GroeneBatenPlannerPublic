Each YAML file in this directory describes a dataset. Some guidelines when editting these files:

- Don't add log messages to the file. After a change you can log the reason for the change as
  a GIT commit message. GIT makes it easy to obtain a log of changes.
- It is a very good idea to keep the square brackets and comma's vertically aligned. Then tables
  look like tables, and people using fancy editors that support arbitrary selections of blocks
  will be glad.
- After changing YAML files, validate them, so we know for sure that we can use them from Python code:
  ```bash
  validate_knowledge_yaml.py <filename>
  validate_knowledge_yaml.py table/yaml/*.yaml
  ```
  Don't commit YAML files that are not valid.

More info about YAML:
- https://en.wikipedia.org/wiki/YAML
- https://yaml.org/spec/1.2.2/

YAML is not free text. The files in this directory have to obey a very specific format, which
we can define ourselves. Luckily, YAML does look like free text. It is easy to the eyes and
easy to parse by software.
