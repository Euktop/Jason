import os
import shutil
from typing import Optional
from jason import Jason
from jason.infrastructure.command_handlers import AddCommandHandler, PrintCommandHandler
from jasonutils.domain.interfaces import IOutput, ICommandExecutor
from jasonutils.adapters.mappers import CommandMapper
from jasonutils.infrastructure.console_output import ConsoleOutput
from jasonutils.infrastructure.sources import (
    FolderJsonSource,
    YamlCommandSource,
    SingleJsonSource,
)
from jasonutils.infrastructure.writers import JsonResultWriter
from jasonutils.infrastructure.validators import JsonSchemaValidator
from jasonutils.infrastructure.jason_adapter import JasonCommandExecutor
from jasonutils.application.use_cases import BatchProcessingUseCase, SingleCommandUseCase, ExecuteCommandUseCase

# --- Безопасность и файловые команды ---
from jasonutils.infrastructure.security import PathSecurityGuard
from jasonutils.infrastructure.fs_handlers import (
    CreateFileHandler,
    ModifyFileHandler,
    SearchReplaceHandler,
    DeleteFileHandler,
    CopyHandler,
    MoveHandler,
)
# --- Новые obsidian-команды ---
from jasonutils.infrastructure.obsidian_handlers import (
    SetFrontmatterHandler,
    InsertLineHandler,
    AppendToListHandler,
    TouchHandler,
    GlobHandler,
)
# --- Команды чтения (read-only) ---
from jasonutils.infrastructure.read_handlers import (
    ReadFilesHandler,
    ListFilesHandler,
)

# Путь к папке JasonRun (рядом с bootstrap.py)
_JASON_RUN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "JasonRun")

def _build_security_guard(whitelist_path: Optional[str] = None, blacklist_path: Optional[str] = None) -> PathSecurityGuard:
    """Создаёт SecurityGuard, читая списки из txt-файлов."""
    if whitelist_path is None:
        whitelist_path = os.path.join(_JASON_RUN_DIR, "white_list.txt")
    if blacklist_path is None:
        blacklist_path = os.path.join(_JASON_RUN_DIR, "black_list.txt")
    return PathSecurityGuard(whitelist_path, blacklist_path)

def setup_jason_registry() -> Jason:
    """Настройка ядра Jason: базовые + файловые + obsidian-команды."""
    j = Jason()
    
    # Базовые
    j.register("add", AddCommandHandler())
    j.register("print", PrintCommandHandler())
    
    # Безопасность
    guard = _build_security_guard()
    
    # Файловые
    j.register("create_file", CreateFileHandler(guard))
    j.register("modify_file", ModifyFileHandler(guard))
    j.register("search_replace", SearchReplaceHandler(guard))
    j.register("delete_file", DeleteFileHandler(guard))
    j.register("copy", CopyHandler(guard))
    j.register("move", MoveHandler(guard))
    
    # Obsidian-команды
    j.register("set_frontmatter", SetFrontmatterHandler(guard))
    j.register("insert_line", InsertLineHandler(guard))
    j.register("append_to_list", AppendToListHandler(guard))
    j.register("touch", TouchHandler(guard))
    
    executor = JasonCommandExecutor(j)
    j.register("glob", GlobHandler(guard, executor))
    
    # Команды чтения (read-only)
    j.register("read_files", ReadFilesHandler(guard))
    j.register("list_files", ListFilesHandler(guard))
    
    return j

def clear_folder(folder_path: str) -> None:
    """Инфраструктурная утилита для очистки."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)

def build_batch_pipeline(input_dir: str, output_dir: str) -> BatchProcessingUseCase:
    clear_folder(output_dir)
    jason_instance = setup_jason_registry()
    mapper = CommandMapper()
    source = FolderJsonSource(input_dir, mapper)
    executor = JasonCommandExecutor(jason_instance)
    writer = JsonResultWriter(output_dir)
    return BatchProcessingUseCase(source, executor, writer)

def build_single_yaml_pipeline(file_path: str, schema: dict = None) -> SingleCommandUseCase:
    jason_instance = setup_jason_registry()
    validator = JsonSchemaValidator(schema) if schema else None
    mapper = CommandMapper(validator)
    output = ConsoleOutput()
    source = YamlCommandSource(file_path, mapper)
    executor = JasonCommandExecutor(jason_instance)
    return SingleCommandUseCase(source, executor, output)

def build_single_json_pipeline(file_path: str, schema: dict = None) -> SingleCommandUseCase:
    jason_instance = setup_jason_registry()
    validator = JsonSchemaValidator(schema) if schema else None
    mapper = CommandMapper(validator)
    output = ConsoleOutput()
    source = SingleJsonSource(file_path, mapper)
    executor = JasonCommandExecutor(jason_instance)
    return SingleCommandUseCase(source, executor, output)

# --- Новые методы для программного API ---

def build_executor_only() -> ICommandExecutor:
    """Собирает и возвращает только исполнитель команд (без источников и писателей)."""
    jason_instance = setup_jason_registry()
    return JasonCommandExecutor(jason_instance)

def build_execute_command_use_case() -> ExecuteCommandUseCase:
    """Собирает Use Case для программного выполнения команд из памяти."""
    executor = build_executor_only()
    return ExecuteCommandUseCase(executor)