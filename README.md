## Проект **Jason** — библиотека для выполнения команд из JSON

**Jason** — это легковесная Python-библиотека, реализующая **Clean Architecture** и принципы **SOLID**. Она позволяет загружать команды из JSON-файлов (или строк), парсить их и выполнять с помощью зарегистрированных обработчиков. Библиотека спроектирована так, чтобы **все команды создавались в клиентском проекте** — ядро предоставляет только инфраструктуру и абстракции.

---

### Ключевые особенности

- **Чистая архитектура** — строгое разделение на слои (Domain, Application, Adapters, Infrastructure).
- **Инверсия зависимостей (DIP)** — все зависимости направлены к интерфейсам, определённым в Domain.
- **Открытость/закрытость (OCP)** — добавление новых команд не требует изменения существующего кода.
- **Тестируемость** — бизнес-логика изолирована от внешних систем (файловая система, консоль).
- **Гибкость** — вы можете подменить любой компонент (вывод, чтение файлов, парсер) своей реализацией.

---

### Установка

Библиотека распространяется как Python-пакет. Установите её локально (например, из исходников):

```bash
git clone <url-репозитория>
cd jason
pip install .
```

Либо скопируйте каталог `jason` в свой проект и импортируйте оттуда.

---

### Быстрый старт

#### 1. Создайте свой обработчик команды

Наследуйте `ICommandHandler` и реализуйте метод `execute(params: dict) -> Any`.

```python
from jason import ICommandHandler

class GreetHandler(ICommandHandler):
    def execute(self, params):
        name = params.get("name", "World")
        return f"Hello, {name}!"
```

#### 2. Инициализируйте Jason и зарегистрируйте команду

```python
from jason import Jason

jason = Jason()
jason.register("greet", GreetHandler())
```

#### 3. Выполните команду из JSON-файла

Создайте файл `command.json`:
```json
{
    "command": "greet",
    "params": {"name": "Alice"}
}
```

Запустите:
```python
jason.run_file("command.json")
```

В консоль будет выведено:
```
Hello, Alice!
```

#### 4. Или выполните из JSON-строки

```python
json_str = '{"command": "greet", "params": {"name": "Bob"}}'
jason.run_json(json_str)
```

---

### Расширенное использование

#### Кастомизация вывода и чтения

Вы можете передать свои реализации `IOutput` и `IFileReader`:

```python
from jason import Jason, IOutput, IFileReader

class FileOutput(IOutput):
    def write(self, message: str):
        with open("output.log", "a") as f:
            f.write(message + "\n")

class CustomFileReader(IFileReader):
    def read_text(self, path: str):
        # своя логика чтения
        ...

jason = Jason(output=FileOutput(), file_reader=CustomFileReader())
```

#### Регистрация нескольких команд

```python
jason.register("add", AddHandler())
jason.register("mul", MultiplyHandler())
jason.register("concat", ConcatHandler())
```

#### Использование встроенных обработчиков (опционально)

Библиотека поставляется с несколькими готовыми командами (для демонстрации):
- `print` — выводит `message`
- `add` — складывает `a` и `b`
- `echo` — возвращает `text`
- `sum` — суммирует список `numbers`

Их можно зарегистрировать, импортировав соответствующие классы из `jason.infrastructure.command_handlers`.

---

### Структура библиотеки (Clean Architecture)

```
jason/
├── domain/                     # Ядро (не зависит от внешнего мира)
│   ├── interfaces.py           # Абстрактные классы (ICommandHandler, IOutput, ...)
│   └── exceptions.py           # Доменные исключения
├── application/                # Сценарии использования (Use Cases)
│   ├── dtos.py                 # Data Transfer Objects
│   └── use_cases.py            # ProcessCommandUseCase (оркестрация)
├── adapters/                   # Адаптеры (преобразование данных)
│   ├── json_parser.py          # Парсинг JSON в CommandRequest
│   └── file_loader.py          # Загрузка из файла через IFileReader
├── infrastructure/             # Конкретные реализации (зависимости)
│   ├── console_output.py       # Вывод в консоль
│   ├── file_reader.py          # Чтение файлов
│   ├── command_handlers.py     # Встроенные обработчики (необязательны)
│   └── command_registry.py     # Реестр команд (SimpleCommandRegistry)
├── api.py                      # Фасад Jason (главный интерфейс для клиентов)
└── __init__.py                 # Экспорт публичных символов
```

**Направление зависимостей** всегда идёт от периферии (Infrastructure) к ядру (Domain).  
**Замена любой детали** (например, переход с консоли на лог-файл) не затрагивает бизнес-логику.

---

### Пример: полностью пользовательский проект

```python
# my_app.py
from jason import Jason, ICommandHandler

class MultiplyHandler(ICommandHandler):
    def execute(self, params):
        x = params.get("x", 0)
        y = params.get("y", 1)
        return x * y

if __name__ == "__main__":
    jason = Jason()
    jason.register("multiply", MultiplyHandler())
    jason.run_file("commands.json")
```

`commands.json`:
```json
{"command": "multiply", "params": {"x": 6, "y": 7}}
```

Вывод: `42`

---

### Тестирование

Благодаря изоляции слоёв, вы можете легко тестировать каждый компонент отдельно.  
Например, для тестирования Use Case без реального ввода-вывода:

```python
from jason.application.use_cases import ProcessCommandUseCase
from jason.application.dtos import CommandRequest
from jason.domain.interfaces import ICommandRegistry, IOutput

class MockRegistry(ICommandRegistry):
    def get_handler(self, name):
        return lambda p: f"mocked {name}"

class MockOutput(IOutput):
    def __init__(self): self.last = ""
    def write(self, msg): self.last = msg

def test_use_case():
    reg = MockRegistry()
    out = MockOutput()
    use_case = ProcessCommandUseCase(reg, out)
    use_case.execute(CommandRequest("test", {}))
    assert out.last == "mocked test"
```

---

### Лицензия и вклад

Проект распространяется под MIT-лицензией. Вы можете свободно использовать, модифицировать и встраивать его в свои проекты.  
Приветствуются Pull Request'ы с улучшениями.

---

### Заключение

**Jason** предоставляет минималистичный, но расширяемый каркас для выполнения команд, описанных в JSON. Он следует лучшим практикам Clean Architecture, что делает его надёжным, тестируемым и легко адаптируемым под любые нужды.
