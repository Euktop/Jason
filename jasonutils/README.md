# 🚀 JasonUtils

**JasonUtils** — это продвинутая утилита и Python-библиотека для выполнения команд из JSON и YAML файлов, построенная на базе ядра **Jason**. 

Проект строго следует принципам **Clean Architecture** и **SOLID**, что гарантирует высокую тестируемость, гибкость и независимость бизнес-логики от внешних деталей (файловой системы, форматов данных, способов ввода-вывода).

## ✨ Ключевые возможности
- **Одиночное выполнение** команд из JSON- и YAML-файлов.
- **Пакетная обработка** целых директорий с автоматическим сохранением результатов.
- **Валидация** входных данных с помощью JSON Schema.
- **Удобный CLI** для интеграции в bash-скрипты и CI/CD.
- **Чистый Python API** (Фасад) для встраивания в другие приложения.
- **Расширяемость**: легко добавить новые источники данных (БД, HTTP) или форматы вывода.
- **Команды чтения**: безопасное чтение содержимого файлов и структуры папок с контролем глубины (`read_files`, `list_files`).

---

## 📦 Установка

### 1. Установка ядра Jason
```bash
git clone <url-репозитория Jason>
cd Jason
pip install .
```

### 2. Установка JasonUtils
Скопируйте каталог `jasonutils` в ваш проект или установите как пакет.

### 3. Зависимости
Для работы с YAML и валидации установите дополнительные библиотеки:
```bash
pip install pyyaml jsonschema
```

---

## 📝 Формат команд

Команда описывается в виде JSON или YAML объекта:

```json
{
  "command": "название_команды",
  "params": {
    "параметр1": "значение",
    "параметр2": 123
  }
}
```

Допускается использование массива команд в одном файле:
```json
[
  {"command": "add", "params": {"a": 2, "b": 3}},
  {"command": "print", "params": {"message": "Hello!"}}
]
```

---

## 💻 Использование через CLI (Командная строка)

Точка входа: `python -m jasonutils.cli`

### Режим `run` — Одиночное выполнение
Выполняет первую команду из файла (JSON или YAML). Поддерживает опциональную валидацию.

```bash
python -m jasonutils.cli run <путь_к_файлу> [--schema <путь_к_схеме>]
```

**Примеры:**
```bash
# Выполнить команду из JSON
python -m jasonutils.cli run input/command.json

# Выполнить из YAML с жесткой валидацией по схеме
python -m jasonutils.cli run input/command.yaml --schema schemas/command_schema.json
```

### Режим `batch` — Пакетная обработка
Считывает все `.json` файлы из входной папки, выполняет их и сохраняет результаты в выходную папку.

```bash
python -m jasonutils.cli batch <папка_вход> <папка_выход>
```

**Пример:**
```bash
python -m jasonutils.cli batch ./input ./output
```
*Алгоритм:*
1. Читает все `.json` файлы из `./input`.
2. Выполняет команды (файл может содержать объект или список объектов).
3. Для каждой команды создает файл `./output/{имя_файла}.out.json` (или с индексом `_0`, `_1`, если в файле список).

---

## 🐍 Программное использование (Python API)

Для интеграции в скрипты используйте фасад `JasonUtils`. Вся сложность сборки зависимостей (DI) скрыта внутри.

```python
from jasonutils import JasonUtils

if __name__ == "__main__":
    utils = JasonUtils()
    
    # 1. Выполнение одного JSON файла
    utils.run_json_file("command.json")
    
    # 2. Выполнение YAML с валидацией
    schema = {"type": "object", "properties": {"command": {"type": "string"}}}
    utils.run_yaml("command.yaml", schema=schema)
    
    # 3. Пакетная обработка папки
    utils.run_folder("./input", "./output")
```

---

## 🏛 Архитектура проекта

Проект разделен на 4 строгих слоя. Зависимости направлены **строго от периферии к ядру**.

```text
jasonutils/
├── domain/                 # 🧠 Ядро (Entities, Value Objects, Interfaces, Exceptions)
│   ├── entities.py         # CommandPayload, ExecutionRequest, ExecutionResult
│   ├── interfaces.py       # ICommandSource, ICommandExecutor, IResultWriter
│   └── exceptions.py       # DomainError, SourceError, ValidationError
│
├── application/            # ⚙️ Use Cases (Оркестрация потоков данных)
│   └── use_cases.py        # BatchProcessingUseCase, SingleCommandUseCase
│
├── adapters/               # 🔌 Interface Adapters (Маппинг, CLI)
│   ├── mappers.py          # CommandMapper (сырой dict -> Domain)
│   └── cli_controller.py   # Парсинг argparse, вызов Use Cases
│
├── infrastructure/         # 🗄 Frameworks & Drivers (Внешние детали)
│   ├── sources.py          # FolderJsonSource, YamlCommandSource (Чтение файлов)
│   ├── writers.py          # JsonResultWriter, ConsoleResultWriter (Запись)
│   ├── validators.py       # JsonSchemaValidator
│   ├── jason_adapter.py    # Адаптер к ядру Jason
│   └── console_output.py   # Вывод в stdout
│
├── bootstrap.py            # 🏗 Composition Root (Сборка пайплайнов, DI)
├── api.py                  # 🚪 Фасад для Python API
└── cli.py                  # 🚀 Точка входа для CLI (python -m jasonutils.cli)
```

### Преимущества такой архитектуры:
- **Заменяемость**: Хотите читать команды из PostgreSQL или REST API? Просто реализуйте `ICommandSource` в слое `infrastructure/`. Ядро и Use Cases менять **не нужно**.
- **Тестируемость**: `BatchProcessingUseCase` покрывается юнит-тестами за секунды с помощью моков, без обращения к файловой системе.
- **Защита от утечек**: Инфраструктурные детали (JSON, YAML, `argparse`) никогда не проникают в бизнес-логику.

---

## 🛠 Расширение и кастомизация

### Добавление новых команд
По умолчанию `JasonUtils` регистрирует базовые команды (`add`, `print`). Если вам нужны кастомные команды, вы можете настроить реестр в `bootstrap.py` или использовать ядро `Jason` напрямую:

```python
from jason import Jason, ICommandHandler
from jasonutils.infrastructure.jason_adapter import JasonCommandExecutor

class MultiplyHandler(ICommandHandler):
    def execute(self, params):
        return params.get("a", 0) * params.get("b", 1)

# Прямое использование ядра
jason = Jason()
jason.register("multiply", MultiplyHandler())
executor = JasonCommandExecutor(jason)
# ... далее передача executor в Use Cases
```

### Замена формата вывода
Чтобы сохранять результаты не в JSON, а, например, в CSV или базу данных, реализуйте интерфейс `IResultWriter` из `domain/interfaces.py` и подмените его в `bootstrap.py` при сборке `BatchProcessingUseCase`.

---

## ⚠️ Обработка ошибок

- **В CLI (одиночный режим)**: Ошибки валидации или выполнения прерывают работу и выводятся в `stderr` / `stdout`.
- **В CLI (пакетный режим)**: Ошибки **не прерывают** батч. Для каждой упавшей команды в `output` создается файл, где поле `"error"` содержит текст исключения, а `"result"` равно `null`.
- **В Python API**: Исключения домена (`SourceError`, `ValidationError`, `ExecutionError`) пробрасываются вызывающему коду для самостоятельной обработки.

---
## 📜 Логирование (JasonRun)
Скрипт `JasonRun/run.py` автоматически создаёт лог-файлы в папке `logs/`. При каждом запуске создаётся новый файл с меткой времени. Для экономии места реализована автоматическая очистка: каждый 5-й запуск удаляет самый старый лог-файл.

## 📄 Лицензия
MIT. Свободное использование, модификация и распространение.