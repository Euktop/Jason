import sys
import os
import logging
from datetime import datetime
import glob  # добавлен для поиска файлов логов

# 1. Настраиваем пути
base_scripts_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, base_scripts_dir)
jason_dir = r"D:\repos\Jason"
if os.path.exists(jason_dir):
    sys.path.insert(0, jason_dir)

from jasonutils.bootstrap import build_batch_pipeline


def cleanup_old_logs(log_dir, keep_ratio=5):
    """
    Удаляет самый старый лог-файл, если общее количество логов (включая новый)
    становится кратным keep_ratio.
    """
    pattern = os.path.join(log_dir, "run_*.log")
    log_files = glob.glob(pattern)
    if not log_files:
        return
    # Сортируем по времени создания (старые первыми)
    log_files.sort(key=os.path.getctime)
    # Проверяем: если после добавления нового файла количество станет кратным keep_ratio
    if (len(log_files) + 1) % keep_ratio == 0:
        oldest = log_files[0]
        try:
            os.remove(oldest)
            print(f"🧹 Удалён старый лог: {oldest}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить {oldest}: {e}")


def setup_logger(log_dir):
    # Очистка старых логов перед созданием нового
    cleanup_old_logs(log_dir, keep_ratio=5)

    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f"run_{timestamp}.log")
    log_format = "%(asctime)s | %(levelname)-8s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
    return logging.getLogger(__name__), log_file


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, "logs")
    
    logger, current_log_file = setup_logger(log_dir)
    logger.info("=" * 50)
    logger.info("🟢 ЗАПУСК СКРИПТА")
    logger.info(f"Файл лога сохраняется в: {current_log_file}")
    
    try:
        input_dir = os.path.join(base_dir, "input")
        output_dir = os.path.join(base_dir, "output")
        
        logger.info(f"🚀 Начинаем чтение файлов из: {input_dir}")
        
        # Вся магия DI и Clean Architecture скрыта внутри bootstrap
        pipeline = build_batch_pipeline(input_dir, output_dir)
        pipeline.execute()
        
        logger.info(f"✅ Успешно! Результаты сохранены в: {output_dir}")
        logger.info("🔴 ЗАВЕРШЕНИЕ СКРИПТА (Без ошибок)")
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}", exc_info=True)
    finally:
        logger.info("=" * 50)